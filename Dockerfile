# MAINTAINER MANISH

FROM python:3.7-alpine

WORKDIR /myapp

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt  

CMD ["python3", "app.py"]