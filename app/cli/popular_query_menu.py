from app.cli import utils
from app.cli.search_filter import SearchFilter
from app.cli.user_menu import MenuItem, UserMenu
from app.logger import logger
from app.mongo import MongoHistoryConnection


class PopularQueryMenu:
    def __init__(self, history: MongoHistoryConnection):
        self.__history = history

    def choose(self) -> SearchFilter | None:
        options = []

        for item in self.__history.get_popular_queries():
            search_filter = SearchFilter.from_history_document(item.query)
            if search_filter is None:
                continue

            searched_at = item.last_searched_at.astimezone().strftime("%Y-%m-%d %H:%M")
            label = f"{search_filter.to_history_key()} [{item.count}] {searched_at}"
            options.append((item.query, search_filter, label))

        if not options:
            print(utils.color_text(f"{'NO POPULAR QUERIES YET':^80}", "yellow"))
            return None

        menu_items = [MenuItem(idx, label) for idx, (_, _, label) in enumerate(options)]
        menu = UserMenu("POPULAR QUERIES", menu_items, 5)
        selected_idx = menu.show("Repeat query")
        if selected_idx == UserMenu.CHOICE_EXIT:
            return None

        query, search_filter, _ = options[menu[selected_idx].id]
        logger.info("Popular query selected: %s", query)
        return search_filter
