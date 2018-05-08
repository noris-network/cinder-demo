FROM python:3.6-slim-stretch


EXPOSE 8080
ENV DATABASE_DIR /app/

RUN mkdir -pv /app/app
RUN mkdir -pv /app/tiny
WORKDIR /app/


COPY manage.py /app/
ADD app/* /app/app/
ADD tiny/* /app/tiny/

CMD  ["python3", "/app/manage.py", "serve", "-H", "0.0.0.0"]
