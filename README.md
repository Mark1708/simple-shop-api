# Simple Shop API

## Описание
Это простая реализация Онлайн магазина для практики в Python


## Запуск
### Миграции
```shell
alembic init migrations
alembic revision --autogenerate -m "Added category and product table"
```

### Запуск приложения
```shell
# Запускаем базу данных
docker compose up -d

# Устанавливаем нужные зависимости
python -m venv venv
source venv/bin/activate
# pip3 freeze > requirements.txt Фиксация зависимостей
pip3 install -r requirements.txt

# Запускаем приложение
chmod +x entrypoint.sh
./entrypoint.sh
```

## Технологии
- Python
- Fast API
- Pydantic
- SQLAlchemy
- Slowapi

## Статус
Проект _окончен_

## Цель
Ознакомиться с возможностями языка и лучшими практиками

## Контакты
Выполнен [Гурьяновым Марком](https://mark1708.github.io/)
#### +7(962)024-50-04 | mark1708.work@gmail.com | [github](http://github.com/Mark1708)

![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=Mark1708&repo=simple-shop-api&theme=chartreuse-dark&show_icons=true)