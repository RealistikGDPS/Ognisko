FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV USE_ENV_CONFIG=1

WORKDIR /app

# Setup Go Migrate
RUN wget https://github.com/golang-migrate/migrate/releases/download/v4.15.2/migrate.linux-amd64.tar.gz && \
    tar zxvf migrate.linux-amd64.tar.gz && \
    mv migrate /usr/local/bin/go-migrate && \
    chmod u+x /usr/local/bin/go-migrate && \
    rm migrate.linux-amd64.tar.gz

# Python Dependencies
COPY requirements/requirements.txt .
RUN pip install -r requirements.txt

# Move migrations
COPY database /app/database

# Move scripts to /app
RUN apt update && apt install default-mysql-client curl dos2unix -y
COPY scripts /app/scripts
RUN dos2unix /app/scripts/*
RUN chmod +x /app/scripts/*

# Copy the application
COPY rgdps /app/rgdps
COPY main.py /app/

# Run the application
EXPOSE 80
CMD ["/app/scripts/bootstrap.sh"]
