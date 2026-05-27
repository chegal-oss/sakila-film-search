from typing import Generator

from .connector import Connector
from .model import Film, Category, Year
from app.logger import logger


class SakilaRepo:

    FILMS_ON_PAGE = 10

    def __init__(self, connector: Connector):
        self.__connector: Connector = connector
        self.current_page: int = 0


    def get_films(self, category_id:int = None, years:str = None, search_title:str = None)-> Generator[Film]:
        where_statement = ((f" and c.category_id = {category_id}" if category_id else "")
        + (f" and f.release_year between {years.split("-")[0]} and {years.split("-")[1]}" if years else "")
        + (f" and f.title like '%%{search_title.lower()}%%'" if search_title else ""))
        params = (self.current_page * self.FILMS_ON_PAGE, self.FILMS_ON_PAGE)
        logger.info(
            "Fetching films: category_id=%s, years=%s, search=%s, offset=%s, limit=%s",
            category_id,
            years,
            search_title or "All",
            params[0],
            params[1],
        )
        rows = self.__connector.execute(Film.get_query(where_statement), params)
        logger.info("Films fetched: %s", len(rows))
        yield from map(Film.from_dict, rows)

    def get_category(self) -> Generator[Category]:
        yield from map(Category.from_dict, self.__connector.execute(Category.get_query()))

    def get_year(self) -> Generator[Year]:
        yield from map(Year.from_dict, self.__connector.execute(Year.get_query()))
