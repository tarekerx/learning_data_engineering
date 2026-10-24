FROM python:3.12-slim

WORKDIR /app

COPY reqs.txt .
RUN pip install --no-cache-dir -r reqs.txt

COPY . .

CMD ["python","src/convert_users.py","rc/fetch_users.py"]