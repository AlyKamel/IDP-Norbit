FROM rasa/rasa:3.2.8-full

WORKDIR /app
COPY . /app
USER root

RUN pip install -r components/requirements.txt

CMD ["run", "--enable-api"]