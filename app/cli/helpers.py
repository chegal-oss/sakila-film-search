from app.cli import utils
from app.cli.user_menu import UserMenu, MenuItem
from app.db.model import Category, Year, Film
from app.db.repository import SakilaRepo
from app.logger import logger


class IOHelper:
    USER_SEARCH_HISTORY = {}

    def __init__(self, repo: SakilaRepo):
        self.__repo = repo
        self.__category: Category | None = None
        self.__years: Year | None = None
        self.__search_title: str | None = None

    def main_loop(self):
        logger.info("UI loop started")
        while True:
            self._fill_category()
            if not self.__category:
                logger.debug("Category selection canceled, exiting UI loop")
                break

            self._fill_years()
            if not self.__years:
                logger.debug("Year selection canceled, restarting category selection")
                continue

            self._fill_search_title()
            if self.__search_title is None:
                logger.debug("Search input canceled, restarting year selection")
                continue

            self.print_page()


    @classmethod
    def print_user_history(cls):
        print(utils.dict_to_color_str(cls.USER_SEARCH_HISTORY))


    @classmethod
    def add_to_history(cls, key: str, mes: str):
        cls.USER_SEARCH_HISTORY[key] = mes


    def _fill_category(self):
        menu_category = UserMenu("CATEGORY", [MenuItem(c.category_id, c.name) for c in self.__repo.get_category()])
        while (idx := menu_category.show("Select category")) != UserMenu.CHOICE_EXIT:
            self.__category = Category(menu_category[idx].id, menu_category[idx].name)
            self.add_to_history("category", self.__category.name)
            logger.info("Category selected: %s", self.__category.name)
            return
        self.__category = None
        logger.debug("Category selection exited")




    def _fill_years(self):
        menu_year = UserMenu("YEARS", [MenuItem(y.id, y.period) for y in self.__repo.get_year()])
        while (idx := menu_year.show("Select period")) != UserMenu.CHOICE_EXIT:
            self.__years = Year(menu_year[idx].id, menu_year[idx].name)
            self.add_to_history("years", self.__years.period)
            logger.info("Year selected: %s", self.__years.period)
            return
        self.__years = None
        logger.debug("Year selection exited")



    def _fill_search_title(self) -> str | None:
        while True:
            self.__search_title = input("Enter a title (Enter - all, q - exit): ")
            if self.__search_title.lower() == "q":
                self.__search_title = None
                logger.debug("Search input exited")
                break
            self.add_to_history("title", self.__search_title if self.__search_title else "All")
            logger.info("Search title entered: %s", self.__search_title or "All")
            self.print_page()



    def print_page(self) -> int:
        logger.info(
            "Rendering films page: category=%s, years=%s, search=%s, page=%s",
            self.__category.name if self.__category else None,
            self.__years.period if self.__years else None,
            self.__search_title or "All",
            self.__repo.current_page,
        )
        while True:
            header = utils.color_text(" " * 5 + str(Film(0, "Title", 0, 0, 0, "Category", "Rating    ")),
                                      "black", "white")
            print(header)
            count = 0
            for idx, film in enumerate(self.__repo.get_films(category_id=self.__category.category_id,
                                                             years=self.__years.period if self.__years.id else None,
                                                             search_title=self.__search_title)):
                text_file = str(film)
                if self.__search_title:
                    text_file = text_file.replace(self.__search_title.upper(),
                                                  utils.color_text(self.__search_title.upper(), "blue"))

                print(f"{(idx + 1) + (self.__repo.current_page * self.__repo.FILMS_ON_PAGE):5}. {text_file}")
                count += 1

            if not count:
                print(utils.color_text(f"{'RESULTS NOT FOUND':^{len(header) - 17}}", "red"))
                logger.info("No films found for current filters")
            else:
                menu_items = []
                if self.__repo.current_page > 0:
                    menu_items.append(MenuItem(-1, "Previous"))
                if count == self.__repo.FILMS_ON_PAGE:
                    menu_items.append(MenuItem(1, "Next"))

                if menu_items:
                    menu_page = UserMenu("PAGES", menu_items, 1)
                    page = menu_page.show("Select page")
                    if page != UserMenu.CHOICE_EXIT:
                        logger.debug("Paging action selected: %s", menu_page[page].name)
                        self.__repo.current_page += menu_page[page].id
                        logger.debug("Page changed to: %s", self.__repo.current_page)

            self.__repo.current_page = 0
            logger.debug("Page reset to 0")
