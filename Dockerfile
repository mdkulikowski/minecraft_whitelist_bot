FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install discord

RUN pip install python-dotenv

CMD ["python", "minecraft_whitelist_bot.py"]
