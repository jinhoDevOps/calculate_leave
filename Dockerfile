FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install flask numpy requests

EXPOSE 25002

CMD ["python", "main.py"]
