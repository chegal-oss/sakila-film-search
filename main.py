from app.cli.helpers import IOHelper
from app import db
from app.db.repository import SakilaRepo
from app.mongo import MongoHistoryConnection


def main():
    with db.connect(db.MySQLConnector) as sql_connection, MongoHistoryConnection() as history :
        repo = SakilaRepo(sql_connection)
        IOHelper(repo, history).main_loop()

if __name__ == "__main__":
    main()
