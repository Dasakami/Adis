FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r --no-cache requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver"]