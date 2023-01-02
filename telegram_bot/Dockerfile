FROM python:3.7-slim
WORKDIR /app

RUN  apt-get update -y
RUN  apt-get install libpq-dev -y
RUN  apt-get install build-essential -y
#todo buil in other container
COPY telegram_bot/requirements.txt .
RUN  pip install -r requirements.txt

COPY telegram_bot/configurer/* ./configurer/
COPY telegram_bot/telegram/* ./telegram/
COPY same_files/* ./same_files/
COPY telegram_bot/main.py ./main.py
CMD ["python3", "main.py"]