FROM python:3.11.5

WORKDIR /app
COPY /app .

ENV FLASK_APP=webapp/ap.py
ENV FLASK_ENV=development

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT bash entrypoint.sh