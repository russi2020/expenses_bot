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
        """Context manager for cursor. Used in _execute function"""

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

    def _execute(self, query, *args):
        """Custom execute function with context manager"""

        with self._get_cursor() as cur:
            cur.execute(query, args)
            cur.execute("COMMIT")


class DbCreator(DbConnector):

    def __init__(self, db_connect_info: Dict[str, Any]):
        super().__init__(db_connect_info)

    def create_users_table(self):
        """Creates table expenses_bot_user"""

        query = """
        CREATE TABLE IF NOT EXISTS expenses_bot_user(
        id SERIAL PRIMARY KEY, name VARCHAR(100), last_name VARCHAR(100), email VARCHAR(100), 
        telegram_id NOT NULL UNIQUE INTEGER)
        """
        self._execute(query=query)

    def create_category_table(self):
        """Creates table expenses_category"""

        query = """
        CREATE TABLE IF NOT EXISTS expenses_category(
        id SERIAL PRIMARY KEY, category_name VARCHAR(100);
        """
        self._execute(query=query)

    def create_currency_table(self):
        """Creates table currency"""

        query = """
        CREATE TABLE IF NOT EXISTS currency(id SERIAL PRIMARY KEY, currency_name VARCHAR(100))
        """
        self._execute(query=query)

    def create_table_category_dictionary(self):
        """Here is list of words that could be in category. For example, ice cream is in category food.
        These words' user can write in his message and this word checks in database. If there is not such word
        telegram bot suggest adding this word in table expenses_dictionary and add category for this word.
        """

        query = """
        CREATE TABLE IF NOT EXISTS expenses_dictionary(
        id SERIAL PRIMARY KEY, 
        word VARCHAR(100),
        category_id INTEGER
        FOREIGN KEY category_id REFERENCES expenses_category(id) ON DELETE RESTRICT;
        )
        """
        self._execute(query=query)

    def create_expenses_table(self):
        """Creates table expenses"""

        query = """
        CREATE TABLE IF NOT EXISTS expenses(
        id SERIAL PRIMARY KEY,
        expenses_sum FLOAT,
        currency_id NOT NULL INTEGER,
        category_id NOT NULL INTEGER,
        user_id NOT NULL INTEGER
        FOREIGN KEY currency_id REFERENCES currency(id) ON DELETE RESTRICT
        FOREIGN KEY category_id REFERENCES expenses_category(id) ON DELETE RESTRICT 
        FOREIGN KEY user_id REFERENCES expenses_bot_user(id) ON DELETE RESTRICT;
        )
        """
        self._execute(query=query)

    def create_first_weekday_func(self):
        """
        Function to get first day of week. For get_expenses_by_week and get_expenses_by_category_for_week functions
        """

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
        """
        Function to get last day of week. For get_expenses_by_week and get_expenses_by_category_for_week functions
        """

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
        """Creates all table and functions"""

        self.create_users_table()
        self.create_category_table()
        self.create_expenses_table()
        self.create_first_weekday_func()
        self.create_last_weekday_func()


class DbFunctions(DbConnector):

    def __init__(self, db_connect_info: Dict[str, Any]):
        super().__init__(db_connect_info)

    def create_user(self, name: str, last_name: str, email: str, telegram_id: int):
        """Inserts user entry into expenses_bot_user table"""
        query = """
        INSERT INTO expenses_bot_user(name, last_name, email, telegram_id) VALUES ($1, $2, $3, $4)
        """
        self._execute(query, name, last_name, email, telegram_id)

    def insert_category(self, category_name: str):
        """Inserts category entry into expenses_category table"""
        query = """
        INSERT INTO expenses_category(category_name) VALUES ($1)
        """
        self._execute(query, category_name)

    def insert_currency(self, currency_name: str):
        """Inserts currency entry into currency table"""
        query = """
        INSERT INTO currency(currency_name) VALUES ($1)
        """
        self._execute(query, currency_name)

    def insert_expense(self, spending_sum: int, currency_id: int, category_id: int, user_id: int):
        """Insert expense into expenses table"""
        query = """
        INSERT INTO expenses(expenses_sum, currency_id, category_id, user_id) VALUES ($1, $2, $3, $4)
        """
        self._execute(query, spending_sum, currency_id, category_id, user_id)

    def get_expenses_by_specific_day(self, day: datetime.date):
        """Expenses by specific day. For example 2022-10-10. Format for day is 2022-10-10"""
        query: str = """SELECT * FROM expenses WHERE date = $1"""
        self._execute(query, day)

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
