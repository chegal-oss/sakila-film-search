from app.cli.helpers import IOHelper
from app.db import connect, MySQLConnector
from app.db.repository import SakilaRepo


def main():
    with connect(MySQLConnector) as connection:
        repo = SakilaRepo(connection)
        IOHelper(repo).main_loop()

if __name__ == "__main__":
    main()
