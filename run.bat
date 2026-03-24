@echo off

REM Активируем виртуальное окружение
call .\venv\Scripts\activate

REM Устанавливаем зависимости из requirements.txt
python -m pip install -r requirements.txt

REM Запускаем Flask приложение
set FLASK_APP=app.py
python -m flask run --port=8000
