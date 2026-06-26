FROM python:3.12-slim

WORKDIR /app

RUN mkdir -p data/backups logs

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -c "import asyncio, sys; sys.path.insert(0, '.'); from database import Database; asyncio.run(Database('data/quran_tracker.db').init())"

CMD ["python", "bot.py"]