FROM python:3.7
WORKDIR /code
ENV FLASK_APP flaskr
ENV FLASK_RUN_HOST 0.0.0.0
RUN apt-get -y update &&\
  apt install -y libpq-dev python-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
RUN chmod +x run_trade.sh
RUN mkdir /code/trade/logs
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]