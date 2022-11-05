FROM python:3.10
WORKDIR /code

COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY ./ ./

EXPOSE 8050

CMD ["python", "./app.py"]