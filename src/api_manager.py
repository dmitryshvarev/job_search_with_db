"""
Модуль для работы с API hh.ru.
Предоставляет функции для получения данных о компаниях и их вакансиях.
"""

import requests
import time
from typing import Optional, List, Dict, Any


class HeadHunterAPI:
    """
    Класс для взаимодействия с API hh.ru.
    Позволяет получать данные о компаниях и их вакансиях.
    """

    BASE_URL = "https://api.hh.ru"
    HEADERS = {"User-Agent": "JobParser/1.0"}

    @staticmethod
    def get_employer_vacancies(
        employer_id: int, page: int = 0, per_page: int = 100
    ) -> Optional[Dict[str, Any]]:
        """
        Получает список вакансий для указанного работодателя.

        Args:
            employer_id (int): ID работодателя на hh.ru
            page (int): Номер страницы (начиная с 0)
            per_page (int): Количество вакансий на странице (максимум 100)

        Returns:
            Optional[Dict[str, Any]]: JSON-ответ API или None в случае ошибки
        """
        url = f"{HeadHunterAPI.BASE_URL}/vacancies"
        params = {"employer_id": employer_id, "page": page, "per_page": per_page}

        try:
            response = requests.get(
                url, params=params, headers=HeadHunterAPI.HEADERS, timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе вакансий для работодателя {employer_id}: {e}")
            return None

    @staticmethod
    def get_employer_info(employer_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о работодателе.

        Args:
            employer_id (int): ID работодателя на hh.ru

        Returns:
            Optional[Dict[str, Any]]: Информация о работодателе или None в случае ошибки
        """
        url = f"{HeadHunterAPI.BASE_URL}/employers/{employer_id}"

        try:
            response = requests.get(url, headers=HeadHunterAPI.HEADERS, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе информации о работодателе {employer_id}: {e}")
            return None

    @staticmethod
    def get_vacancy_details(vacancy_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает полную информацию о вакансии.

        Args:
            vacancy_id (int): ID вакансии на hh.ru

        Returns:
            Optional[Dict[str, Any]]: Полная информация о вакансии или None в случае ошибки
        """
        url = f"{HeadHunterAPI.BASE_URL}/vacancies/{vacancy_id}"

        try:
            response = requests.get(url, headers=HeadHunterAPI.HEADERS, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе информации о вакансии {vacancy_id}: {e}")
            return None

    @staticmethod
    def get_all_vacancies_for_employer(employer_id: int) -> List[Dict[str, Any]]:
        """
        Получает все вакансии работодателя со всех страниц.

        Args:
            employer_id (int): ID работодателя на hh.ru

        Returns:
            List[Dict[str, Any]]: Список всех вакансий работодателя
        """
        all_vacancies = []
        page = 0
        per_page = 100

        while True:
            data = HeadHunterAPI.get_employer_vacancies(employer_id, page, per_page)

            if data is None:
                break

            vacancies = data.get("items", [])
            all_vacancies.extend(vacancies)

            # Проверяем количество страниц
            pages = data.get("pages", 0)
            if page >= pages - 1:
                break

            page += 1
            # Не перегружаем сервер
            time.sleep(0.1)

        return all_vacancies
