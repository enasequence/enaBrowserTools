FROM python:3

LABEL Author="Blaise Alako" Email="blaise@ebi.ac.uk"

LABEL Description="ENA brokers activities reporting" Vendor="EMBL-EBI" Version="1.0"

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "./broker_activity_reporter.py","--data_type","analysis", "--broker_name","ArrayExpress" ]