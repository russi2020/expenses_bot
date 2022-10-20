import datetime
import logging
from contextlib import contextmanager
from os import path
from typing import Dict, Any, List, Tuple

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
        """Custom execute function with context manager. Used for INSERT, UPDATE, DELETE functions"""
        with self._get_cursor() as cur:
            cur.execute(query, args)
            cur.execute("COMMIT")


class BaseDbExtended(DbConnector):

    def _db_execute_with_fetchall_return(self, query, *args) -> List[tuple]:
        """For select all results from database"""
        with self._get_cursor() as cur:
            cur.execute(query=query, vars=args)
            return cur.fetchall()

    def _db_execute_with_fetchone_return(self, query, *args) -> Any:
        """For select one result from database"""
        with self._get_cursor() as cur:
            cur.execute(query=query, vars=args)
            return cur.fetchone()[0]


class DbCreator(DbConnector):

    def __init__(self, db_connect_info: Dict[str, Any]):
        super().__init__(db_connect_info)

    def create_users_table(self):
        """Creates table expenses_bot_user"""
        query = """
        CREATE TABLE IF NOT EXISTS expenses_bot_user(
        id SERIAL PRIMARY KEY, name VARCHAR(100), last_name VARCHAR(100), email VARCHAR(100), 
        telegram_id INTEGER NOT NULL UNIQUE
        );
        """
        self._execute(query=query)

    def create_category_table(self):
        """Creates table expenses_category"""
        query = """
        CREATE TABLE IF NOT EXISTS expenses_category(
        id SERIAL PRIMARY KEY, category_name VARCHAR(100)
        );
        """
        self._execute(query=query)

    def create_currency_table(self):
        """Creates table currency"""
        query = """
        CREATE TABLE IF NOT EXISTS currency(id SERIAL PRIMARY KEY, currency_name VARCHAR(100));
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
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES expenses_category(id) ON DELETE RESTRICT
        );
        """
        self._execute(query=query)

    def create_expenses_table(self):
        """Creates table expenses"""
        query = """
        CREATE TABLE IF NOT EXISTS expenses(
        id SERIAL PRIMARY KEY,
        expenses_sum FLOAT,
        currency_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        created_at DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (currency_id) REFERENCES currency(id) ON DELETE RESTRICT,
        FOREIGN KEY (category_id) REFERENCES expenses_category(id) ON DELETE RESTRICT,
        FOREIGN KEY (user_id) REFERENCES expenses_bot_user(id) ON DELETE RESTRICT
        );
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

    def create_get_first_month_day_func(self):
        """
        Function to get first day of current month.
        For get_expenses_by_week and get_expenses_by_current_month functions
        :return: None
        """
        query = """
        CREATE OR REPLACE FUNCTION first_monthday () RETURNS DATE AS $$
        DECLARE first_monthday DATE;
        BEGIN
        SELECT INTO first_monthday date_trunc('month', now()::timestamp)::date as first_monthday;
        RETURN first_monthday;
        END;
        $$ LANGUAGE 'plpgsql';
        """
        self._execute(query=query)

    def create_get_last_month_day_func(self):
        """
        Function to get last day of current month.
        For get_expenses_by_week and get_expenses_by_current_month functions
        """
        query = """
        CREATE OR REPLACE FUNCTION last_monthday () RETURNS DATE AS $$
        DECLARE last_monthday DATE;
        BEGIN
        SELECT INTO last_monthday (date_trunc('month', now()::timestamp)+'1 month'::interval-'1 day'::interval)::date 
        as last_monthday;
        RETURN last_monthday;
        END;
        $$ LANGUAGE 'plpgsql';
        """
        self._execute(query=query)

    def create_get_specific_month_last_day(self):
        """Function to get last day of specific month and year. For example, args is 9 for september and 2022 for year.
        So function returns date 2022-09-30.
        """
        query = """
        CREATE OR REPLACE FUNCTION last_specific_monthday (month_number varchar(2), year_number varchar(4) ) 
        RETURNS DATE AS $$
        DECLARE last_monthday DATE;
        BEGIN
        SELECT INTO last_monthday (CONCAT(year_number, month_number, '01')::date + 
        interval '1 month' - interval '1 days')::date 
        as last_monthday;
        RETURN last_monthday;
        END;
        $$ LANGUAGE 'plpgsql';
        """
        self._execute(query=query)

    def create_tables_and_functions(self):
        """Creates all table and functions"""
        self.create_users_table()
        self.create_category_table()
        self.create_table_category_dictionary()
        self.create_currency_table()
        self.create_expenses_table()
        self.create_first_weekday_func()
        self.create_last_weekday_func()
        self.create_get_first_month_day_func()
        self.create_get_last_month_day_func()
        self.create_get_specific_month_last_day()


class DbFunctions(BaseDbExtended):

    def __init__(self, db_connect_info: Dict[str, Any]):
        super().__init__(db_connect_info)
        logger = logging.getLogger(__name__)
        logger.info("Start db_functions instance")

    def create_user(self, name: str, last_name: str, email: str, telegram_id: int):
        """Inserts user entry into expenses_bot_user table"""
        query = """
        INSERT INTO expenses_bot_user(name, last_name, email, telegram_id) VALUES (%s, %s, %s, %S)
        """
        self._execute(query, name, last_name, email, telegram_id)

    def find_user_by_email(self, email: str):
        """Checks if email exists in database"""
        query = """SELECT email FROM expenses_bot_user WHERE email = %s;"""
        return self._db_execute_with_fetchone_return(query, email)

    def get_user_id_by_telegram_id(self, telegram_id: int):
        """Get user id by telegram_id"""
        query = """SELECT id FROM expenses_bot_user WHERE telegram_id = %s;"""
        return self._db_execute_with_fetchone_return(query, telegram_id)

    def check_category(self, category_name: str):
        """Get expenses_category id by category_name"""
        query = """
        SELECT id FROM expenses_category WHERE category_name = %s;
        """
        return self._db_execute_with_fetchone_return(query, category_name)

    def insert_category(self, category_name: str):
        """Inserts category entry into expenses_category table"""
        query = """
        INSERT INTO expenses_category(category_name) VALUES (%s);
        """
        self._execute(query, category_name)

    def check_currency(self, currency_name: str):
        """Get currency id by currency_name"""
        query = """
        SELECT id FROM currency WHERE currency_name = %s;
        """
        return self._db_execute_with_fetchone_return(query, currency_name)

    def insert_currency(self, currency_name: str):
        """Inserts currency entry into currency table"""
        query = """
        INSERT INTO currency(currency_name) VALUES (%s);
        """
        self._execute(query, currency_name)

    def insert_expense(self, spending_sum: int, currency_id: int, category_id: int, user_id: int):
        """Insert expense into expenses table"""
        query = """
        INSERT INTO expenses(expenses_sum, currency_id, category_id, user_id) VALUES (%s, %s, %s, %s)
        """
        self._execute(query, spending_sum, currency_id, category_id, user_id)

    def get_expenses_by_specific_day(self, day: datetime.date):
        """Expenses by specific day. For example 2022-10-10. Format for day is 2022-10-10"""
        query: str = """
        SELECT exp.expenses_sum, cur.currency_name, exp_cat.category_name
        FROM expenses exp 
        JOIN expenses_category exp_cat ON exp.category_id = exp_cat.id
        JOIN currency cur ON exp.currency_id = cur.id
        WHERE created_at = %s
        """
        self._execute(query, day)

    def get_expenses_by_week(self) -> List[Tuple[Any, ...]]:
        """Expenses by current week"""
        query = """
        SELECT exp.expenses_sum, cur.currency_name, exp_cat.category_name
        FROM expenses exp 
        JOIN expenses_category exp_cat ON exp.category_id = exp_cat.id
        JOIN currency cur ON exp.currency_id = cur.id
        WHERE created_at BETWEEN first_wd() AND last_wd();
        """
        return self._db_execute_with_fetchall_return(query)

    def get_expenses_by_month_till_today(self):
        """Expenses for month till current day"""
        query = """
        SELECT exp.expenses_sum, cur.currency_name, exp_cat.category_name
        FROM expenses exp 
        JOIN expenses_category exp_cat ON exp.category_id = exp_cat.id
        JOIN currency cur ON exp.currency_id = cur.id
        WHERE created_at > CURRENT_DATE - INTERVAL '1 month';
        """
        return self._db_execute_with_fetchall_return(query)

    def get_expenses_by_current_month(self):
        """Expenses for current month. From first day till last day"""
        query = """
        SELECT exp.expenses_sum, cur.currency_name, exp_cat.category_name
        FROM expenses exp 
        JOIN expenses_category exp_cat ON exp.category_id = exp_cat.id
        JOIN currency cur ON exp.currency_id = cur.id
        WHERE created_at BETWEEN first_monthday() AND last_monthday();
        """
        return self._db_execute_with_fetchall_return(query)

    def get_expenses_by_specific_month(self, month_number: str, year_number: str):
        """Expenses for specific month.
        For example, you insert 'october',
        so you get all expenses for october only"""
        query = """
        SELECT exp.expenses_sum, cur.currency_name, exp_cat.category_name
        FROM expenses exp 
        JOIN expenses_category exp_cat ON exp.category_id = exp_cat.id
        JOIN currency cur ON exp.currency_id = cur.id
        WHERE created_at BETWEEN CONCAT(%s, %s, '01')::date AND last_specific_monthday(%s, %s);
        """
        return self._db_execute_with_fetchall_return(query, month_number, year_number, month_number, year_number)

    def get_expenses_by_year(self):
        """Expenses for current year from yor first expenses entry"""
        query = """
        SELECT exp.expenses_sum, cur.currency_name, exp_cat.category_name
        FROM expenses exp 
        JOIN expenses_category exp_cat ON exp.category_id = exp_cat.id
        JOIN currency cur ON exp.currency_id = cur.id
        WHERE created_at > date_trunc('year', CURRENT_DATE)::date;
        """
        return self._db_execute_with_fetchall_return(query)

    def get_expenses_by_category_for_current_day(self, category: str):
        """Gets expenses for today by category"""
        query = """
        SELECT exp.expenses_sum, cur.currency_name, exp_cat.category_name 
        FROM expenses exp 
        JOIN expenses_category exp_cat ON exp.category_id = exp_cat.id
        JOIN currency cur ON exp.currency_id = cur.id
        WHERE exp_cat.category_name = %s;
        """
        return self._db_execute_with_fetchall_return(query, category)

    def get_expenses_by_specific_category_for_today(self, category: str):
        """Gets expenses for today by specific category. For example food"""
        query = """
        SELECT exp.expenses_sum, cur.currency_name, exp_cat.category_name
        FROM expenses exp 
        JOIN expenses_category exp_cat ON exp.category_id = exp_cat.id
        JOIN currency cur ON exp.currency_id = cur.id
        WHERE exp_cat.category_name = %s AND created_at = CURRENT_DATE;
        """
        return self._db_execute_with_fetchall_return(query, category)

    def get_expenses_by_specific_category_for_specific_day(self, category: str, date: str):
        """Gets expenses for specific date by specific category. For example food"""
        query = """
        SELECT exp.expenses_sum, cur.currency_name, exp_cat.category_name
        FROM expenses exp 
        JOIN expenses_category exp_cat ON exp.category_id = exp_cat.id
        JOIN currency cur ON exp.currency_id = cur.id
        WHERE exp_cat.category_name = %s AND created_at = %s;
        """
        return self._db_execute_with_fetchall_return(query, category, date)

    def get_expenses_by_category_for_week(self, category: str):
        """Gets expenses for current week by category. For example food"""
        query = """
        SELECT exp.expenses_sum, cur.currency_name, exp_cat.category_name
        FROM expenses exp 
        JOIN expenses_category exp_cat ON exp.category_id = exp_cat.id
        JOIN currency cur ON exp.currency_id = cur.id
        WHERE exp_cat.category_name = %s
        AND created_at BETWEEN first_wd() AND last_wd();
        """
        return self._db_execute_with_fetchall_return(query, category)

    def get_expenses_by_category_for_specific_month(self, category: str, month: str, year: str):
        """Expenses by week specific month.
        For example, you insert 'october',
        so you get all expenses by specific category
        for october only"""
        query = """
        SELECT exp.expenses_sum, cur.currency_name, exp_cat.category_name
        FROM expenses exp 
        JOIN expenses_category exp_cat ON exp.category_id = exp_cat.id
        JOIN currency cur ON exp.currency_id = cur.id
        WHERE exp_cat.category_name = %s
        AND created_at BETWEEN CONCAT(%s, %s, '01')::date AND last_specific_monthday(%s, %s);     
        """
        return self._db_execute_with_fetchall_return(query, category, month, year, month, year)

    def get_expenses_by_category_for_year(self, category: str):
        """Get expenses for year by specific category. For example food."""
        query = """
        SELECT exp.expenses_sum, cur.currency_name, exp_cat.category_name
        FROM expenses exp 
        JOIN expenses_category exp_cat ON exp.category_id = exp_cat.id
        JOIN currency cur ON exp.currency_id = cur.id
        WHERE created_at > date_trunc('year', CURRENT_DATE)::date
        AND exp_cat.category_name = %s;
        """
        return self._db_execute_with_fetchall_return(query, category)
