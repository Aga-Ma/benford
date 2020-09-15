FROM python:3.7-slim
RUN mkdir -p /app
WORKDIR /app
COPY ./setup.py /app/
COPY ./requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/

VOLUME ["/app"]
EXPOSE 5000