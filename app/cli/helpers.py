from app.cli import utils
from app.cli.film_results_view import FilmResultsView
from app.cli.popular_query_menu import PopularQueryMenu
from app.cli.search_filter import SearchFilter
from app.cli.user_menu import UserMenu, MenuItem
from app.db.model import Category, Year
from app.db.repository import SakilaRepo
from app.logger import logger
from app.mongo import MongoHistoryConnection


class IOHelper:
    def __init__(self, repo: SakilaRepo, history: MongoHistoryConnection):
        self.__repo = repo
        self.__category: Category | None = None
        self.__years: Year | None = None
        self.__results_view = FilmResultsView(repo, history)
        self.__popular_menu = PopularQueryMenu(history)

    def main_loop(self):
        logger.debug("UI loop started")
        print(utils.sakila_banner())
        while True:
            self._fill_category()
            if not self.__category:
                logger.debug("Category selection canceled, exiting UI loop")
                break
            if self.__category.category_id == Category.POPULAR:
                search_filter = self.__popular_menu.choose()
                if search_filter:
                    self.__category = search_filter.category
                    self.__years = search_filter.years
                    self.__results_view.show(search_filter)
                    self._fill_search_title()
                continue

            self._fill_years()
            if not self.__years:
                logger.debug("Year selection canceled, restarting category selection")
                continue

            self._fill_search_title()

    def _fill_category(self):
        menu_category = UserMenu("CATEGORY", [MenuItem(c.category_id, c.name) for c in self.__repo.get_category()])
        while (idx := menu_category.show("Select category")) != UserMenu.CHOICE_EXIT:
            self.__category = Category(menu_category[idx].id, menu_category[idx].name)
            logger.info("Category selected: %s", self.__category.name)
            return
        self.__category = None
        logger.debug("Category selection exited")

    def _fill_years(self):
        menu_year = UserMenu("YEARS", [MenuItem(y.id, y.period) for y in self.__repo.get_year()])
        while (idx := menu_year.show("Select period")) != UserMenu.CHOICE_EXIT:
            self.__years = Year(menu_year[idx].id, menu_year[idx].name)
            logger.info("Year selected: %s", self.__years.period)
            return
        self.__years = None
        logger.debug("Year selection exited")

    def _fill_search_title(self) -> str | None:
        if self.__category is None or self.__years is None:
            logger.debug("Search title input skipped because filter is incomplete")
            return None

        while True:
            prompt_text = utils.color_text("Enter a title (Enter - all, q - exit): ", "cyan")
            search_title = input(prompt_text)
            if search_title.lower() == "q":
                logger.debug("Search input exited")
                break
            logger.info("Search title entered: %s", search_title or "All")
            self.__results_view.show(SearchFilter(self.__category, self.__years, search_title))
