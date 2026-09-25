FROM python:3.12-slim

WORKDIR /app

COPY src ./src
COPY data/users.json ./data/users.json
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["python","src/fetch_users.py"]