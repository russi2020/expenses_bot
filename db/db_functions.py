import datetime
import logging
from contextlib import contextmanager
from os import path
from typing import Dict, Any

import psycopg2
from psycopg2 import pool


class DbConnector:

    def __init__(self, db_connect_info: Dict[str, Any]):

        self.conn_pool = pool.SimpleConnectionPool(minconn=1, maxconn=10, **db_connect_info)

        log_file_path = path.join(path.dirname(path.abspath("__file__")), 'logging.ini')
        logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
        logger = logging.getLogger(__name__)
        logger.info("Start db instance")

    @contextmanager
    def _get_cursor(self):
        cursor, conn = None, None
        try:
            conn = self.conn_pool.getconn()
            cursor = conn.cursor()
            yield cursor
        except psycopg2.Error as e:
            logging.error(e)
        finally:
            cursor.close()
            self.conn_pool.putconn(conn)

    def _execute(self, query, values: tuple = None):
        with self._get_cursor() as cur:
            cur.execute(query, values)
            cur.execute("COMMIT")


class DbCreator(DbConnector):

    def __init__(self, db_connect_info: Dict[str, Any]):
        super().__init__(db_connect_info)

    def create_users_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS expenses_bot_user(
        id SERIAL NOT NULL PRIMARY KEY, name VARCHAR(100), last_name VARCHAR(100), email VARCHAR(100), 
        telegram_id NOT NULL UNIQUE INTEGER)
        """
        self._execute(query=query)

    def create_category_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS expenses_category(
        id SERIAL NOT NULL PRIMARY KEY, category_name VARCHAR(100);
        """
        self._execute(query=query)

    def create_table_category_dictionary(self):
        """Here is list of words that could be in category. For example, ice cream is in category food.
        These words' user can write in his message and this word checks in database. If there is not such word
        telegram bot suggest adding this word in table expenses_dictionary and add category for this word.
        """
        query = """
        CREATE TABLE IF NOT EXISTS expenses_dictionary(
        id SERIAL NOT NULL PRIMARY KEY, 
        word VARCHAR(100),
        category_id INTEGER
        FOREIGN KEY category_id REFERENCES expenses_category(id) ON DELETE RESTRICT;
        )
        """
        self._execute(query=query)

    def create_expenses_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS expenses(
        id SERIAL NOT NULL PRIMARY KEY,
        expenses_sum FLOAT,
        currency VARCHAR(100),
        category_id NOT NULL INTEGER,
        user_id NOT NULL INTEGER
        FOREIGN KEY category_id REFERENCES expenses_category(id) ON DELETE RESTRICT 
        FOREIGN KEY user_id REFERENCES expenses_bot_user(id) ON DELETE RESTRICT;
        )
        """
        self._execute(query=query)

    def create_first_weekday_func(self):
        query = """
        CREATE OR REPLACE FUNCTION first_wd () RETURNS DATE AS $$
        DECLARE wd DATE;
        BEGIN
        SELECT INTO wd date_trunc('week', now()::timestamp)::date;
        RETURN wd;
        END;
        $$ LANGUAGE 'plpgsql';
        """
        self._execute(query=query)

    def create_last_weekday_func(self):
        query = """
        CREATE OR REPLACE FUNCTION last_wd () RETURNS DATE AS $$
        DECLARE wd DATE;
        BEGIN
        SELECT INTO wd (date_trunc('week', now()::timestamp)+'6 days'::interval)::date as sunday;
        RETURN wd;
        END;
        $$ LANGUAGE 'plpgsql';
        """
        self._execute(query=query)

    def create_tables_and_functions(self):
        self.create_users_table()
        self.create_category_table()
        self.create_expenses_table()
        self.create_first_weekday_func()
        self.create_last_weekday_func()


class DbFunctions(DbConnector):

    def __init__(self, db_connect_info: Dict[str, Any]):
        super().__init__(db_connect_info)

    def insert_expense(self, spending_sum: int, payment_currency: str, category_id: int, user_id):
        """Insert expense into expenses table"""
        query = """
        INSERT INTO expenses(expenses_sum, currency, category_id, user_id) VALUES ($1, $2, $3, $4)
        """
        self._execute(query, (spending_sum, payment_currency, category_id, user_id,))

    def get_expenses_by_specific_day(self, day: datetime.date):
        """Expenses by specific day. For example 2022-10-10. Format for day is 2022-10-10"""
        query: str = """SELECT * FROM expenses WHERE date = $1"""
        self._execute(query, (day,))

    def get_expenses_by_week(self):
        """Expenses by current week"""
        pass

    def get_expenses_by_month_till_today(self, query: str):
        """Expenses for month till current day"""
        pass

    def get_expenses_by_specific_month(self, query: str, month_name: str):
        """Expenses by week specific month.
        For example, you insert 'october',
        so you get all expenses for october only"""
        pass

    def get_expenses_by_year(self, query):
        """Expenses for year from yor first expenses entry"""
        pass

    def get_expenses_by_category_for_current_day(self, category: str):
        """Gets expenses for today by category"""
        pass

    def get_expenses_by_category_for_specific_day(self, category: str):
        """Gets expenses for today by specific category. For example food"""
        pass

    def get_expenses_by_category_for_week(self, category: str):
        """Gets expenses for week by category. For example food"""
        pass

    def get_expenses_by_category_for_specific_month(self, category: str, month: str):
        """Expenses by week specific month.
        For example, you insert 'october',
        so you get all expenses by specific category
        for october only"""
        pass

    def get_expenses_by_category_for_year(self, category: str):
        """Get expenses for year by specific category. For example food."""
        pass
