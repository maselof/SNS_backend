FROM python:3.7
COPY . /backend
WORKDIR /backend
RUN pip3 install --upgrade pip -r requirements.txt
CMD ["python", "main.py"]
