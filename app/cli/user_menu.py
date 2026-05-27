import math

from app.cli import utils
from app.logger import logger


class MenuItem:

    def __init__(self, item_id: int, name: str):
        self.id: int = item_id
        self.name: str = name
    def __repr__(self):
        return f"id = {self.id} name = {self.name}"

class UserMenu:
    CHOICE_EXIT = -1

    def __init__(self, title: str, items: list[MenuItem], max_rows=7):
        self.__title = title
        self.__items = items
        self.__max_rows = max_rows

    def __iter__(self):
        yield from self.__items

    def __getitem__(self, item):
        return self.__items[item]

    def __len__(self):
        return self.__items.__len__()


    def show(self, prompt = "Make a choice") -> int:
        if self:
            rows_count = min(self.__max_rows, max(1, len(self)))
            cols_count = max(1, math.ceil(len(self) / rows_count))
            matrix = [["" for _ in range(cols_count)] for _ in range(rows_count)]

            for idx, item in enumerate(self):
                row = idx % rows_count
                col = idx // rows_count
                matrix[row][col] = f"{idx + 1:>2}. {item.name}"

            max_item_len = max(map(lambda x: len(str(x)), self)) + 3
            string_list = [(f"│ {{:{max_item_len}}}" * len(row)).format(*row) + "│" for row in matrix]
            header_width = max(map(len, string_list))
            title = utils.color_text(f"{self.__title:^{header_width}}", "black", "white")
            footer = "└" + "─" * (header_width - 2) + "┘"

            print(title + "\n" + "\n".join(string_list) + "\n" + footer)

        while True:
            user_input = input(prompt + " (q - exit): ")
            if user_input.lower() == "q":
                return self.CHOICE_EXIT
            try:
                menu_number = int(user_input)
                if 1 <= menu_number <= len(self):
                    return menu_number - 1
                raise ValueError("Incorrect number")
            except ValueError as e:
                print("Enter correct number or 'q'")
                logger.debug(e)




    def __str__(self):
        return f"Menu {self.__title}"
