"""
Главный модуль приложения - точка входа программы.
Содержит основную логику и интерфейс для взаимодействия с пользователем.
"""

from src.api_manager import HeadHunterAPI
from src.db_manager import DatabaseManager
from src.vacancy_manager import VacancyManager
from src.query_manager import DBManager
import time


# ID компаний для сбора данных
COMPANIES_IDS = [
    3529,  # Сбербанк
    64174,  # 2ГИС
    1740,  # Яндекс
    2180,  # Ozon
    17000,  # HeadHunter
    87021,  # Wildberries
    84585,  # Avito
    78638,  # Т-Банк
    4219,  # T2
    80,  # Альфа-Банк
]


def load_companies_and_vacancies(companies_ids: list) -> None:
    """
    Загружает данные о компаниях и их вакансиях в БД.

    Args:
        companies_ids (list): Список ID компаний для загрузки
    """
    api = HeadHunterAPI()
    db_manager = DBManager()

    print("=" * 60)
    print("ЗАГРУЗКА ДАННЫХ О КОМПАНИЯХ И ВАКАНСИЯХ")
    print("=" * 60)

    for idx, company_id in enumerate(companies_ids, 1):
        print(f"\n[{idx}/{len(companies_ids)}] Обработка компании ID: {company_id}")

        # Получаем информацию о компании
        company_info = api.get_employer_info(company_id)
        if company_info is None:
            print(f"  ✗ Не удалось получить информацию о компании")
            continue

        company_name = company_info.get("name")
        site_url = company_info.get("site_url")
        open_vacancies = company_info.get("open_vacancies", 0)

        print(f"  ✓ Компания: {company_name}")
        print(f"    Открытых вакансий: {open_vacancies}")

        # Вставляем информацию о компании в БД
        if db_manager.insert_company(
            company_id, company_name, site_url, open_vacancies
        ):
            print(f"  ✓ Компания добавлена в БД")
        else:
            print(f"  ✗ Ошибка при добавлении компании в БД")
            continue

        # Получаем все вакансии компании
        print(f"  → Загрузка вакансий...")
        vacancies_data = api.get_all_vacancies_for_employer(company_id)
        print(f"  ✓ Получено вакансий: {len(vacancies_data)}")

        # Обрабатываем и добавляем вакансии в БД
        vacancies = VacancyManager.extract_vacancies(vacancies_data)
        added_count = 0

        for vacancy in vacancies:
            if db_manager.insert_vacancy(
                vacancy.vacancy_id,
                vacancy.company_id,
                vacancy.name,
                vacancy.salary_from,
                vacancy.salary_to,
                vacancy.currency,
                vacancy.area,
                vacancy.experience,
                vacancy.employment_type,
                vacancy.description,
                vacancy.url,
                vacancy.published_at,
            ):
                added_count += 1

        print(f"  ✓ Добавлено в БД: {added_count} вакансий")

        # Соблюдаем ограничения API
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("ЗАГРУЗКА ЗАВЕРШЕНА")
    print("=" * 60)


def display_companies_and_vacancies(db_manager: DBManager) -> None:
    """
    Выводит список компаний и количество их вакансий.

    Args:
        db_manager (DBManager): Менеджер БД для запросов
    """
    print("\n" + "=" * 60)
    print("КОМПАНИИ И КОЛИЧЕСТВО ВАКАНСИЙ")
    print("=" * 60)

    results = db_manager.get_companies_and_vacancies_count()

    if not results:
        print("Нет данных")
        return

    for company_name, vacancy_count in results:
        print(f"{company_name:<40} | Вакансий: {vacancy_count}")


def display_all_vacancies(db_manager: DBManager) -> None:
    """
    Выводит все вакансии с информацией о компании и зарплате.

    Args:
        db_manager (DBManager): Менеджер БД для запросов
    """
    print("\n" + "=" * 60)
    print("ВСЕ ВАКАНСИИ")
    print("=" * 60)

    results = db_manager.get_all_vacancies()

    if not results:
        print("Нет данных")
        return

    for company_name, vacancy_name, salary_from, salary_to, currency, url in results:
        salary_str = "не указана"
        if salary_from and salary_to:
            salary_str = f"{salary_from} - {salary_to} {currency}"
        elif salary_from:
            salary_str = f"от {salary_from} {currency}"
        elif salary_to:
            salary_str = f"до {salary_to} {currency}"

        print(f"\nКомпания: {company_name}")
        print(f"Вакансия: {vacancy_name}")
        print(f"Зарплата: {salary_str}")
        print(f"Ссылка: {url}")
        print("-" * 60)


def display_average_salary(db_manager: DBManager) -> None:
    """
    Выводит среднюю зарплату по всем вакансиям.

    Args:
        db_manager (DBManager): Менеджер БД для запросов
    """
    print("\n" + "=" * 60)
    print("СРЕДНЯЯ ЗАРПЛАТА")
    print("=" * 60)

    avg_salary = db_manager.get_avg_salary()

    if avg_salary is None:
        print("Нет данных для расчета")
    else:
        print(f"Средняя зарплата: {avg_salary:.2f} RUB")


def display_vacancies_with_higher_salary(db_manager: DBManager) -> None:
    """
    Выводит вакансии с зарплатой выше средней.

    Args:
        db_manager (DBManager): Менеджер БД для запросов
    """
    print("\n" + "=" * 60)
    print("ВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ")
    print("=" * 60)

    results = db_manager.get_vacancies_with_higher_salary()

    if not results:
        print("Нет вакансий с зарплатой выше средней")
        return

    print(f"Найдено вакансий: {len(results)}\n")

    for company_name, vacancy_name, salary_from, salary_to, currency, url in results:
        salary_str = "не указана"
        if salary_from and salary_to:
            salary_str = f"{salary_from} - {salary_to} {currency}"
        elif salary_from:
            salary_str = f"от {salary_from} {currency}"
        elif salary_to:
            salary_str = f"до {salary_to} {currency}"

        print(f"Компания: {company_name}")
        print(f"Вакансия: {vacancy_name}")
        print(f"Зарплата: {salary_str}")
        print(f"Ссылка: {url}")
        print("-" * 60)


def display_vacancies_by_keyword(db_manager: DBManager, keyword: str) -> None:
    """
    Выводит вакансии по ключевому слову.

    Args:
        db_manager (DBManager): Менеджер БД для запросов
        keyword (str): Ключевое слово для поиска
    """
    print("\n" + "=" * 60)
    print(f"ПОИСК ВАКАНСИЙ ПО КЛЮЧЕВОМУ СЛОВУ: '{keyword}'")
    print("=" * 60)

    results = db_manager.get_vacancies_with_keyword(keyword)

    if not results:
        print(f"Вакансии с ключевым словом '{keyword}' не найдены")
        return

    print(f"Найдено вакансий: {len(results)}\n")

    for company_name, vacancy_name, salary_from, salary_to, currency, url in results:
        salary_str = "не указана"
        if salary_from and salary_to:
            salary_str = f"{salary_from} - {salary_to} {currency}"
        elif salary_from:
            salary_str = f"от {salary_from} {currency}"
        elif salary_to:
            salary_str = f"до {salary_to} {currency}"

        print(f"Компания: {company_name}")
        print(f"Вакансия: {vacancy_name}")
        print(f"Зарплата: {salary_str}")
        print(f"Ссылка: {url}")
        print("-" * 60)


def show_menu() -> None:
    """Выводит главное меню."""
    print("\n" + "=" * 60)
    print("ГЛАВНОЕ МЕНЮ")
    print("=" * 60)
    print("1. Загрузить компании и вакансии с hh.ru")
    print("2. Показать компании и количество вакансий")
    print("3. Показать все вакансии")
    print("4. Показать среднюю зарплату")
    print("5. Показать вакансии с зарплатой выше средней")
    print("6. Поиск вакансий по ключевому слову")
    print("0. Выход")
    print("=" * 60)


def main() -> None:
    """Главная функция приложения."""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║        ПАРСЕР ВАКАНСИЙ С HH.RU                            ║")
    print("║        Сбор и анализ данных о вакансиях и компаниях       ║")
    print("╚════════════════════════════════════════════════════════════╝")

    # Инициализируем менеджер БД
    db = DatabaseManager()

    # Создаем БД если её нет
    print("\n→ Инициализация базы данных...")
    if db.create_database():
        print("✓ База данных инициализирована")
    else:
        print("✗ Ошибка при инициализации БД")
        return

    # Создаем таблицы если их нет
    print("→ Создание таблиц...")
    if db.create_tables():
        print("✓ Таблицы созданы")
    else:
        print("✗ Ошибка при создании таблиц")
        return

    # Инициализируем менеджер запросов
    db_manager = DBManager()

    # Основной цикл программы
    while True:
        show_menu()
        choice = input("Выберите опцию: ").strip()

        if choice == "1":
            load_companies_and_vacancies(COMPANIES_IDS)

        elif choice == "2":
            display_companies_and_vacancies(db_manager)

        elif choice == "3":
            display_all_vacancies(db_manager)

        elif choice == "4":
            display_average_salary(db_manager)

        elif choice == "5":
            display_vacancies_with_higher_salary(db_manager)

        elif choice == "6":
            keyword = input("Введите ключевое слово для поиска: ").strip()
            if keyword:
                display_vacancies_by_keyword(db_manager, keyword)
            else:
                print("Ключевое слово не может быть пустым")

        elif choice == "0":
            print("\nСпасибо за использование программы!")
            break

        else:
            print("✗ Неверный выбор. Пожалуйста, выберите корректную опцию.")


if __name__ == "__main__":
    main()
