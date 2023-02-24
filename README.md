# Yatube-social-network

## Как запустить проект

Клонировать репозиторий и перейти в него в командной строке:

```git clone https://github.com/beken0w/Yatube-social-network.git```

```cd Yatube-social-network/```

Cоздать и активировать виртуальное окружение:

```python3 -m venv venv```

```source venv/bin/activate```

Установить зависимости из файла requirements.txt:

```python3 -m pip install --upgrade pip```

```pip install -r requirements.txt```

Перейти в директорию с manage.py и выполнить миграции:

```python3 manage.py migrate```

[Опционально] Для быстрого наполнения базы тестовыми данными выполните команду:

```python3 manage.py import_db```

Запустить проект:

```python3 manage.py runserver```

***

