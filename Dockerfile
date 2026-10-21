FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends tzdata ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY bot.py /app/bot.py
ENV PYTHONUNBUFFERED=1 TZ=Europe/Paris
ENTRYPOINT ["python", "/app/bot.py"]
CMD ["run", "--data", "/app/live_data", "--state", "/app/state/alerts.sqlite3"]
