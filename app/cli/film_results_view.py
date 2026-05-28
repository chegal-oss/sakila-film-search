from app.cli import utils
from app.cli.search_filter import SearchFilter
from app.cli.user_menu import MenuItem, UserMenu
from app.db.repository import SakilaRepo
from app.logger import logger
from app.mongo import MongoHistoryConnection


class FilmResultsView:
    def __init__(self, repo: SakilaRepo, history: MongoHistoryConnection):
        self.__repo = repo
        self.__history = history

    def show(self, search_filter: SearchFilter) -> int:
        logger.debug(
            "Rendering films page: category=%s, years=%s, search=%s, page=%s",
            search_filter.category.name,
            search_filter.years.period,
            search_filter.title_label,
            self.__repo.current_page,
        )
        self.__history.save_query(search_filter.to_history_document())
        print(utils.dict_to_color_str(search_filter.to_history_dict()))

        while True:
            self._print_header()
            count = 0
            for idx, film in enumerate(self.__repo.get_films(
                    category_id=search_filter.category.category_id,
                    years=search_filter.years_param,
                    search_title=search_filter.title,
            )):
                text_film = self._highlight_title(str(film), search_filter.title)
                print(f"{(idx + 1) + (self.__repo.current_page * self.__repo.FILMS_ON_PAGE):5}. {text_film}")
                count += 1

            if not count:
                self._print_not_found()
                self._reset_page()
                return count

            menu_items = self._build_page_menu(count)
            if not menu_items:
                self._reset_page()
                return count

            menu_page = UserMenu("PAGES", menu_items, 1)
            page = menu_page.show("Select page")
            if page == UserMenu.CHOICE_EXIT:
                self._reset_page()
                return count

            logger.debug("Paging action selected: %s", menu_page[page].name)
            self.__repo.current_page += menu_page[page].id
            logger.debug("Page changed to: %s", self.__repo.current_page)

    @staticmethod
    def _print_header() -> None:
        header_text = f"{'':5}. {'Title':30} {'Year':^26} {'Category':20} Rating"
        print(utils.color_text(header_text, "black", "white"))

    @staticmethod
    def _print_not_found() -> None:
        print(utils.color_text(f"{'RESULTS NOT FOUND':^92}", "red"))
        logger.info("No films found for current filters")

    @staticmethod
    def _highlight_title(text: str, title: str) -> str:
        if not title:
            return text
        return text.replace(title.upper(), utils.color_text(title.upper(), "blue"))

    def _build_page_menu(self, count: int) -> list[MenuItem]:
        menu_items = []
        if self.__repo.current_page > 0:
            menu_items.append(MenuItem(-1, "Previous"))
        if count == self.__repo.FILMS_ON_PAGE:
            menu_items.append(MenuItem(1, "Next"))
        return menu_items

    def _reset_page(self) -> None:
        self.__repo.current_page = 0
        logger.debug("Page reset to 0")
