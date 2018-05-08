FROM 3.6-slim-stretch

ENV DATABASE_DIR /app/

RUN mkdir /app
WORKDIR /app/


COPY manage.py /app/
ADD app /app/
ADD tiny /app/

ENTRYPOINT python3 /app/manage.py serve -H 0.0.0.0
