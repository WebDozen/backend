# MVP Alfa People сервис ИПР (backend)

## Описание проекта

Сервис предназначен для составления сотрудникам ИПР (индивидуальных планов развития), его просмотра и отслеживания.

## Локальный запуск сервиса в Docker 

Склонировать репозиторий на свой компьютер и перейти в корневую папку:
```python
git clone git@github.com:WebDozen/backend.git
cd backend
```

Создать в корневой папке файл .env с переменными окружения, необходимыми
для работы приложения.

Пример содержимого файла:
```
TOKEN='dskjldfskjldfjksdfgklfgdskjsfgdjndnsf'
USE_SQLITE='false'
DEBUG='tRue'

POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
```

Из корневой директории запустить сборку контейнеров с помощью
docker-compose:
```python
docker-compose up -d
```

При разворачивании контейнеров автоматически будет загружена тестовая база данных.

Документация будет доступка по ссылке http://127.0.0.1/api/swagger/

Для попадания в админ-зону, перейдите по адресу http://127.0.0.1:8000/admin/.

Логин и пароль:
- login: admin
- password: admin

## Технологии

* Python 3.12.1
* Django 3.2
* Django REST framework 3.13
* Nginx
* Docker
* Postgres 13.10

### Авторы

Артём Мариненко, Андрей Палагута, Данила Мандрейкин, Вадим Гуржий
