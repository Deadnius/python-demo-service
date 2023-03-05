FROM python:3.10.7-alpine
WORKDIR /app
COPY . .
COPY requirments.txt .
RUN pip install -r requirments.txt
EXPOSE 8000
ENTRYPOINT [ "python", "./main.py"]