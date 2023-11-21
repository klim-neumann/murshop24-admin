FROM python:3.11

WORKDIR /usr/src/murshop24-admin

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY murshop24_admin murshop24_admin

EXPOSE 8000

CMD [ "gunicorn", "murshop24_admin:app", "--bind", "0.0.0.0" ]
