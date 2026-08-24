# Поиск вакансий на hh.ru с подключением БД

Проект для сбора и анализа данных о вакансиях и компаниях с портала [hh.ru](https://hh.ru/) с использованием их публичного API. Данные сохраняются в базу данных PostgreSQL и предоставляют различные возможности аналитики.

## 📋 Описание проекта

Этот проект позволяет:
- ✅ Получить данные о компаниях и их вакансиях через API hh.ru
- ✅ Автоматически создать и заполнить базу данных PostgreSQL
- ✅ Выполнять различные аналитические запросы к данным
- ✅ Искать вакансии по ключевым словам
- ✅ Анализировать уровень зарплат

##  Быстрый старт

### Установка

1. Клонируйте репозиторий или скопируйте файлы проекта

```
https://github.com/dmitryshvarev/job_search_with_db.git
```

2. Установите зависимости

```
pip install poetry
```

3. Настройте переменные окружения

Скопируйте файл примера .env.example.
Отредактируйте .env с вашими данными PostgreSQL

4. Запустите программу

```
python main.py
```

## 📚 Модули проекта

### api_manager.py

**Класс: `HeadHunterAPI`**

Предоставляет методы для работы с API hh.ru:

- `get_employer_info(employer_id: int)` - получить информацию о работодателе
- `get_employer_vacancies(employer_id: int, page: int, per_page: int)` - получить вакансии работодателя со страницы
- `get_vacancy_details(vacancy_id: int)` - получить полную информацию о вакансии
- `get_all_vacancies_for_employer(employer_id: int)` - получить все вакансии работодателя со всех страниц

### db_manager.py

**Класс: `DatabaseManager`**

Управляет подключением к базе данных и создает структуру:

- `get_connection()` - получить подключение к БД
- `get_admin_connection()` - получить подключение к системной БД для создания новой БД
- `create_database()` - создать новую БД
- `create_tables()` - создать таблицы для компаний и вакансий
- `clear_tables()` - очистить таблицы

**Структура БД:**

Таблица `companies`:
```
id (SERIAL PRIMARY KEY)
company_id (INTEGER UNIQUE)
name (VARCHAR 255)
site_url (VARCHAR 255)
open_vacancies (INTEGER)
```

Таблица `vacancies`:
```
id (SERIAL PRIMARY KEY)
vacancy_id (INTEGER UNIQUE)
company_id (INTEGER) - FK -> companies.company_id
name (VARCHAR 255)
salary_from (INTEGER)
salary_to (INTEGER)
currency (VARCHAR 10)
area (VARCHAR 100)
experience (VARCHAR 100)
employment_type (VARCHAR 100)
description (TEXT)
url (VARCHAR 500)
published_at (TIMESTAMP)
```

### vacancy_manager.py

**Класс: `Vacancy`**

Представляет отдельную вакансию с методами парсинга из данных API.

**Класс: `VacancyManager`**

Предоставляет утилиты для обработки списков вакансий:

- `extract_vacancies(vacancies_data)` - преобразовать данные API в объекты вакансий
- `filter_by_keyword(vacancies, keyword)` - отфильтровать по ключевому слову
- `filter_by_salary_range(vacancies, salary_from, salary_to)` - отфильтровать по диапазону зарплаты

### query_manager.py

**Класс: `DBManager`**

Предоставляет методы для работы с данными в БД:

- `insert_company(...)` - добавить компанию в БД
- `insert_vacancy(...)` - добавить вакансию в БД
- `get_companies_and_vacancies_count()` - получить компании и количество их вакансий (с JOIN)
- `get_all_vacancies()` - получить все вакансии с информацией о компании (с JOIN)
- `get_avg_salary()` - получить среднюю зарплату (с функцией AVG)
- `get_vacancies_with_higher_salary()` - получить вакансии с зарплатой выше средней (с WHERE)
- `get_vacancies_with_keyword(keyword)` - получить вакансии по ключевому слову (с LIKE)

### main.py

**Главный модуль** содержит:

- **Список компаний для сбора** - 10 топовых IT-компаний и крупных работодателей
- **Функция загрузки данных** - `load_companies_and_vacancies()`
- **Функции отображения результатов** - для каждого из методов DBManager
- **Интерфейс пользователя** - меню для выбора операций
- **Точка входа** - функция `main()`

## 🎯 Использование

После запуска программы вы увидите меню:

```
======== ГЛАВНОЕ МЕНЮ ========
1. Загрузить компании и вакансии с hh.ru
2. Показать компании и количество вакансий
3. Показать все вакансии
4. Показать среднюю зарплату
5. Показать вакансии с зарплатой выше средней
6. Поиск вакансий по ключевому слову
0. Выход
```

### Примеры использования:

**1. Загрузка данных**
```
Выберите опцию: 1
```
Программа загрузит информацию о 10 компаниях и их вакансиях в БД.

**2. Просмотр компаний**
```
Выберите опцию: 2
```
Выведет список компаний с количеством вакансий.

**3. Поиск по ключевому слову**
```
Выберите опцию: 6
Введите ключевое слово: Python
```
Найдет все вакансии, содержащие слово "Python".

## 📊 SQL-запросы

Проект использует следующие типы SQL-запросов:

### JOIN запросы
```sql
SELECT c.name, COUNT(v.id) FROM companies c
LEFT JOIN vacancies v ON c.company_id = v.company_id
GROUP BY c.id, c.name
```

### Агрегатные функции (AVG)
```sql
SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2)
FROM vacancies WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
```

### Фильтрация (WHERE)
```sql
SELECT * FROM vacancies
WHERE salary > (SELECT AVG(salary) FROM vacancies)
```

### Поиск (LIKE)
```sql
SELECT * FROM vacancies
WHERE name ILIKE '%python%'
```

## Безопасность

- Учетные данные БД хранятся в файле `.env` и не коммитятся в Git
