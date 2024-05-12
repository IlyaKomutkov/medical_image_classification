Для запуска проекта нужно создать и активировать виртуальное окружение, а затем запустить команды:
```
mkdir -p media/images
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
