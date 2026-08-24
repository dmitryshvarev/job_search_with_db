"""
Модуль для работы с базой данных PostgreSQL.
Предоставляет функции для создания таблиц и управления подключением к БД.
"""

import psycopg2
from typing import Optional
import os
from dotenv import load_dotenv


class DatabaseManager:
    """
    Класс для управления подключением к базе данных PostgreSQL.
    Обеспечивает безопасное хранение учетных данных через переменные окружения.
    """

    def __init__(self) -> None:
        """Инициализирует менеджер БД, загружая переменные окружения."""
        load_dotenv()
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "hh_database")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "")

    def get_connection(self) -> Optional[psycopg2.extensions.connection]:
        """
        Получает подключение к базе данных.

        Returns:
            Optional[psycopg2.extensions.connection]: Объект подключения или None
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            return conn
        except psycopg2.Error as e:
            print(f"Ошибка подключения к БД: {e}")
            return None

    def get_admin_connection(self) -> Optional[psycopg2.extensions.connection]:
        """
        Получает подключение к системной БД postgres для создания новой БД.

        Returns:
            Optional[psycopg2.extensions.connection]: Объект подключения или None
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database="postgres",
            )
            return conn
        except psycopg2.Error as e:
            print(f"Ошибка подключения к системной БД: {e}")
            return None

    def create_database(self) -> bool:
        """
        Создает новую базу данных если она не существует.

        Returns:
            bool: True если БД создана или уже существует, False при ошибке
        """
        conn = self.get_admin_connection()
        if conn is None:
            return False

        try:
            conn.autocommit = True
            cursor = conn.cursor()

            # Проверяем существование БД
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (self.database,)
            )

            if cursor.fetchone() is not None:
                print(f"БД '{self.database}' уже существует")
                cursor.close()
                conn.close()
                return True

            # Создаем БД
            cursor.execute(f"CREATE DATABASE {self.database}")
            print(f"БД '{self.database}' успешно создана")
            cursor.close()
            conn.close()
            return True

        except psycopg2.Error as e:
            print(f"Ошибка при создании БД: {e}")
            return False
        finally:
            if conn is not None:
                conn.close()

    def create_tables(self) -> bool:
        """
        Создает таблицы для компаний и вакансий.

        Returns:
            bool: True при успешном создании, False при ошибке
        """
        conn = self.get_connection()
        if conn is None:
            return False

        try:
            cursor = conn.cursor()

            # Создаем таблицу компаний
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    site_url VARCHAR(255),
                    open_vacancies INTEGER DEFAULT 0
                )
            """
            )

            # Создаем таблицу вакансий
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    id SERIAL PRIMARY KEY,
                    vacancy_id INTEGER UNIQUE NOT NULL,
                    company_id INTEGER NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    currency VARCHAR(10),
                    area VARCHAR(100),
                    experience VARCHAR(100),
                    employment_type VARCHAR(100),
                    description TEXT,
                    url VARCHAR(500),
                    published_at TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id)
                )
            """
            )

            conn.commit()
            print("Таблицы успешно созданы")
            cursor.close()
            return True

        except psycopg2.Error as e:
            print(f"Ошибка при создании таблиц: {e}")
            conn.rollback()
            return False
        finally:
            if conn is not None:
                conn.close()

    def clear_tables(self) -> bool:
        """
        Очищает таблицы (удаляет все данные).

        Returns:
            bool: True при успешной очистке, False при ошибке
        """
        conn = self.get_connection()
        if conn is None:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute("TRUNCATE TABLE vacancies CASCADE")
            cursor.execute("TRUNCATE TABLE companies CASCADE")
            conn.commit()
            print("Таблицы успешно очищены")
            cursor.close()
            return True

        except psycopg2.Error as e:
            print(f"Ошибка при очистке таблиц: {e}")
            conn.rollback()
            return False
        finally:
            if conn is not None:
                conn.close()
