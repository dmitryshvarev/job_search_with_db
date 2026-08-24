"""
Модуль для управления вакансиями.
Предоставляет класс для работы с данными о вакансиях.
"""

from typing import Optional, List, Dict, Any


class Vacancy:
    """
    Класс для представления вакансии.
    Содержит информацию о вакансии и методы для ее обработки.
    """

    def __init__(
        self,
        vacancy_id: int,
        company_id: int,
        name: str,
        salary_from: Optional[int] = None,
        salary_to: Optional[int] = None,
        currency: Optional[str] = None,
        area: Optional[str] = None,
        experience: Optional[str] = None,
        employment_type: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
        published_at: Optional[str] = None,
    ) -> None:
        """
        Инициализирует объект вакансии.

        Args:
            vacancy_id (int): ID вакансии на hh.ru
            company_id (int): ID компании
            name (str): Название вакансии
            salary_from (Optional[int]): Минимальная зарплата
            salary_to (Optional[int]): Максимальная зарплата
            currency (Optional[str]): Валюта зарплаты
            area (Optional[str]): Регион
            experience (Optional[str]): Требуемый опыт
            employment_type (Optional[str]): Тип занятости
            description (Optional[str]): Описание вакансии
            url (Optional[str]): URL вакансии
            published_at (Optional[str]): Дата публикации
        """
        self.vacancy_id = vacancy_id
        self.company_id = company_id
        self.name = name
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.currency = currency
        self.area = area
        self.experience = experience
        self.employment_type = employment_type
        self.description = description
        self.url = url
        self.published_at = published_at

    @staticmethod
    def parse_from_api(vacancy_data: Dict[str, Any]) -> "Vacancy":
        """
        Создает объект вакансии из данных API.

        Args:
            vacancy_data (Dict[str, Any]): Данные вакансии из API hh.ru

        Returns:
            Vacancy: Объект вакансии
        """
        vacancy_id = vacancy_data.get("id")
        company_id = vacancy_data.get("employer", {}).get("id")
        name = vacancy_data.get("name")

        salary = vacancy_data.get("salary")
        salary_from = None
        salary_to = None
        currency = None

        if salary is not None:
            salary_from = salary.get("from")
            salary_to = salary.get("to")
            currency = salary.get("currency")

        area = vacancy_data.get("area", {}).get("name")
        experience = vacancy_data.get("experience", {}).get("name")
        employment_type = vacancy_data.get("employment", {}).get("name")
        description = vacancy_data.get("description", "")
        url = vacancy_data.get("alternate_url")
        published_at = vacancy_data.get("published_at")

        return Vacancy(
            vacancy_id=int(vacancy_id),
            company_id=int(company_id),
            name=name,
            salary_from=salary_from,
            salary_to=salary_to,
            currency=currency,
            area=area,
            experience=experience,
            employment_type=employment_type,
            description=description,
            url=url,
            published_at=published_at,
        )

    def __repr__(self) -> str:
        """Возвращает строковое представление вакансии."""
        return f"Vacancy(id={self.vacancy_id}, name={self.name}, salary={self.salary_from}-{self.salary_to})"


class VacancyManager:
    """
    Класс для управления вакансиями.
    Предоставляет методы для обработки и фильтрации вакансий.
    """

    @staticmethod
    def extract_vacancies(vacancies_data: List[Dict[str, Any]]) -> List[Vacancy]:
        """
        Извлекает объекты вакансий из данных API.

        Args:
            vacancies_data (List[Dict[str, Any]]): Список данных вакансий из API

        Returns:
            List[Vacancy]: Список объектов вакансий
        """
        vacancies = []
        for vacancy_data in vacancies_data:
            try:
                vacancy = Vacancy.parse_from_api(vacancy_data)
                vacancies.append(vacancy)
            except (KeyError, ValueError, TypeError) as e:
                print(f"Ошибка при обработке вакансии: {e}")
                continue

        return vacancies

    @staticmethod
    def filter_by_keyword(vacancies: List[Vacancy], keyword: str) -> List[Vacancy]:
        """
        Фильтрует вакансии по ключевому слову в названии.

        Args:
            vacancies (List[Vacancy]): Список вакансий
            keyword (str): Ключевое слово для поиска

        Returns:
            List[Vacancy]: Отфильтрованный список вакансий
        """
        keyword_lower = keyword.lower()
        return [v for v in vacancies if keyword_lower in v.name.lower()]

    @staticmethod
    def filter_by_salary_range(
        vacancies: List[Vacancy],
        salary_from: Optional[int] = None,
        salary_to: Optional[int] = None,
    ) -> List[Vacancy]:
        """
        Фильтрует вакансии по диапазону зарплаты.

        Args:
            vacancies (List[Vacancy]): Список вакансий
            salary_from (Optional[int]): Минимальная зарплата
            salary_to (Optional[int]): Максимальная зарплата

        Returns:
            List[Vacancy]: Отфильтрованный список вакансий
        """
        filtered = []
        for v in vacancies:
            if v.salary_from is None and v.salary_to is None:
                continue

            if salary_from is not None and (
                v.salary_to is None or v.salary_to < salary_from
            ):
                continue

            if salary_to is not None and (
                v.salary_from is None or v.salary_from > salary_to
            ):
                continue

            filtered.append(v)

        return filtered
