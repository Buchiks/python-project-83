# Анализатор страниц

## Статус:

### Hexlet tests and linter status:
[![Actions Status](https://github.com/Buchiks/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Buchiks/python-project-83/actions)

[![Python CI](https://github.com/Buchiks/python-project-83/actions/workflows/github-actions.yaml/badge.svg)](https://github.com/Buchiks/python-project-83/actions/workflows/github-actions.yaml)

## Описание:
Анализатор страниц – это веб-приложение, разработанное с использованием Flask, которое позволяет пользователям быстро и бесплатно проверять веб-сайты на SEO-пригодность.

* Реализованы добавление URL для последующего анализа
* Анализ добавленного URL на SEO-пригодность
* История добавленных URL с кратким содержанием

## SQlite версия сайта:
[Buchik.pythonanywhere.com](https://buchik.pythonanywhere.com/) <br>
Так как данный проект размещен бесплатно, Pythonanywhere ограничевает доступ к сайтам. [Список доступных сайтов](https://www.pythonanywhere.com/whitelist/)

## Установка:
### Склонируйте репозиторий по ссылке:
```bash
git clone https://github.com/Buchiks/python-project-83.git
cd python-project-83
```
### Установка uv (если не установлен):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
### Установите зависимости:
```bash
make install
```
### Создайте .env файл и настройте структуру, как показано в примере :
```bash
SECRET_KEY=ваш_секретный_ключ
DATABASE_URL=postgresql://пользователь:пароль@localhost:5432/имя_базы
```
### Создайте таблицы:
```bash
make db-init
```

### Запустите приложение на локальном сервере::
```bash
make dev
```
