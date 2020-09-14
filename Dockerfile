FROM python:3.7-alpine
WORKDIR /code
ENV FLASK_APP flaskr
ENV FLASK_RUN_HOST 0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["python3", "run_trade.py", "&&", "gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]