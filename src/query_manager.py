"""
Класс DBManager для работы с данными в базе данных.
Предоставляет методы для выполнения различных запросов к БД.
"""

import psycopg2
from typing import List, Tuple, Optional
from src.db_manager import DatabaseManager


class DBManager:
    """
    Класс для работы с данными в базе данных PostgreSQL.
    Использует библиотеку psycopg2 для взаимодействия с БД.
    """

    def __init__(self) -> None:
        """Инициализирует DBManager с менеджером БД."""
        self.db = DatabaseManager()

    def insert_company(
        self, company_id: int, name: str, site_url: Optional[str], open_vacancies: int
    ) -> bool:
        """
        Вставляет информацию о компании в таблицу.

        Args:
            company_id (int): ID компании на hh.ru
            name (str): Название компании
            site_url (Optional[str]): Сайт компании
            open_vacancies (int): Количество открытых вакансий

        Returns:
            bool: True при успешной вставке, False при ошибке
        """
        conn = self.db.get_connection()
        if conn is None:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO companies (company_id, name, site_url, open_vacancies)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (company_id) DO UPDATE
                SET name = EXCLUDED.name,
                    site_url = EXCLUDED.site_url,
                    open_vacancies = EXCLUDED.open_vacancies
            """,
                (company_id, name, site_url, open_vacancies),
            )

            conn.commit()
            cursor.close()
            return True

        except psycopg2.Error as e:
            print(f"Ошибка при вставке компании: {e}")
            conn.rollback()
            return False
        finally:
            if conn is not None:
                conn.close()

    def insert_vacancy(
        self,
        vacancy_id: int,
        company_id: int,
        name: str,
        salary_from: Optional[int],
        salary_to: Optional[int],
        currency: Optional[str],
        area: Optional[str],
        experience: Optional[str],
        employment_type: Optional[str],
        description: Optional[str],
        url: Optional[str],
        published_at: Optional[str],
    ) -> bool:
        """
        Вставляет информацию о вакансии в таблицу.

        Args:
            vacancy_id (int): ID вакансии на hh.ru
            company_id (int): ID компании
            name (str): Название вакансии
            salary_from (Optional[int]): Минимальная зарплата
            salary_to (Optional[int]): Максимальная зарплата
            currency (Optional[str]): Валюта
            area (Optional[str]): Регион
            experience (Optional[str]): Требуемый опыт
            employment_type (Optional[str]): Тип занятости
            description (Optional[str]): Описание
            url (Optional[str]): URL вакансии
            published_at (Optional[str]): Дата публикации

        Returns:
            bool: True при успешной вставке, False при ошибке
        """
        conn = self.db.get_connection()
        if conn is None:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO vacancies
                (vacancy_id, company_id, name, salary_from, salary_to, currency,
                 area, experience, employment_type, description, url, published_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (vacancy_id) DO NOTHING
            """,
                (
                    vacancy_id,
                    company_id,
                    name,
                    salary_from,
                    salary_to,
                    currency,
                    area,
                    experience,
                    employment_type,
                    description,
                    url,
                    published_at,
                ),
            )

            conn.commit()
            cursor.close()
            return True

        except psycopg2.Error as e:
            print(f"Ошибка при вставке вакансии: {e}")
            conn.rollback()
            return False
        finally:
            if conn is not None:
                conn.close()

    def get_companies_and_vacancies_count(self) -> List[Tuple]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.

        Returns:
            List[Tuple]: Список кортежей (название компании, количество вакансий)
        """
        conn = self.db.get_connection()
        if conn is None:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT c.name, COUNT(v.id) as vacancy_count
                FROM companies c
                LEFT JOIN vacancies v ON c.company_id = v.company_id
                GROUP BY c.id, c.name
                ORDER BY vacancy_count DESC
            """
            )

            results = cursor.fetchall()
            cursor.close()
            return results

        except psycopg2.Error as e:
            print(f"Ошибка при получении компаний и вакансий: {e}")
            return []
        finally:
            if conn is not None:
                conn.close()

    def get_all_vacancies(self) -> List[Tuple]:
        """
        Получает список всех вакансий с названием компании, названием вакансии, зарплатой и ссылкой.

        Returns:
            List[Tuple]: Список кортежей (компания, вакансия, зарплата, ссылка)
        """
        conn = self.db.get_connection()
        if conn is None:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT c.name as company_name,
                       v.name as vacancy_name,
                       v.salary_from,
                       v.salary_to,
                       v.currency,
                       v.url
                FROM vacancies v
                JOIN companies c ON v.company_id = c.company_id
                ORDER BY c.name, v.name
            """
            )

            results = cursor.fetchall()
            cursor.close()
            return results

        except psycopg2.Error as e:
            print(f"Ошибка при получении вакансий: {e}")
            return []
        finally:
            if conn is not None:
                conn.close()

    def get_avg_salary(self) -> Optional[float]:
        """
        Получает среднюю зарплату по всем вакансиям.

        Returns:
            Optional[float]: Средняя зарплата или None при ошибке
        """
        conn = self.db.get_connection()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2) as avg_salary
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            """
            )

            result = cursor.fetchone()
            cursor.close()

            return result[0] if result and result[0] is not None else None

        except psycopg2.Error as e:
            print(f"Ошибка при получении средней зарплаты: {e}")
            return None
        finally:
            if conn is not None:
                conn.close()

    def get_vacancies_with_higher_salary(self) -> List[Tuple]:
        """
        Получает список всех вакансий, у которых зарплата выше средней.

        Returns:
            List[Tuple]: Список вакансий с высокой зарплатой
        """
        conn = self.db.get_connection()
        if conn is None:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT c.name as company_name,
                       v.name as vacancy_name,
                       v.salary_from,
                       v.salary_to,
                       v.currency,
                       v.url
                FROM vacancies v
                JOIN companies c ON v.company_id = c.company_id
                WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 > (
                    SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2)
                    FROM vacancies
                    WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                )
                AND (v.salary_from IS NOT NULL OR v.salary_to IS NOT NULL)
                ORDER BY (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 DESC
            """
            )

            results = cursor.fetchall()
            cursor.close()
            return results

        except psycopg2.Error as e:
            print(f"Ошибка при получении вакансий с высокой зарплатой: {e}")
            return []
        finally:
            if conn is not None:
                conn.close()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple]:
        """
        Получает список всех вакансий, в названии которых содержится переданное слово.

        Args:
            keyword (str): Ключевое слово для поиска

        Returns:
            List[Tuple]: Список найденных вакансий
        """
        conn = self.db.get_connection()
        if conn is None:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT c.name as company_name,
                       v.name as vacancy_name,
                       v.salary_from,
                       v.salary_to,
                       v.currency,
                       v.url
                FROM vacancies v
                JOIN companies c ON v.company_id = c.company_id
                WHERE v.name ILIKE %s
                ORDER BY c.name, v.name
            """,
                (f"%{keyword}%",),
            )

            results = cursor.fetchall()
            cursor.close()
            return results

        except psycopg2.Error as e:
            print(f"Ошибка при поиске вакансий по ключевому слову: {e}")
            return []
        finally:
            if conn is not None:
                conn.close()
