# sudo docker build . -t ctf-manager
# sudo docker run --name ctf-manager --rm -it -d ctf-manager

FROM python:3.9-alpine
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN apk add gcc python3-dev musl-dev

COPY ctf-manager-bot/ .

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
