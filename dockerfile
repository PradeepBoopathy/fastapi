FROM python:3.8-slim-buster

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod 444 test.py
RUN chmod 444 requirements.txt

ENV PORT 4000

ENTRYPOINT ["python"]

CMD ["test.py"]