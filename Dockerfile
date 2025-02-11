FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install flask

EXPOSE 25002

CMD ["python", "flask_annual_leave.py"]
