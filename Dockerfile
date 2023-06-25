FROM python:3.11

RUN apt-get update && apt-get install -y docker-compose

WORKDIR /app

COPY . /app

RUN pip install discord

RUN pip install python-dotenv

CMD ["python", "minecraft_whitelist_bot.py"]
