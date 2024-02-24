FROM python:3.12

ENV PYTHONUNBUFFERED=1
ENV USE_ENV_CONFIG=1

# Apt dependencies
RUN apt update && apt install default-mysql-client curl -y

# Setup Go Migrate
RUN wget https://github.com/golang-migrate/migrate/releases/download/v4.15.2/migrate.linux-amd64.tar.gz && \
    tar zxvf migrate.linux-amd64.tar.gz && \
    mv migrate /usr/local/bin/go-migrate && \
    chmod u+x /usr/local/bin/go-migrate && \
    rm migrate.linux-amd64.tar.gz

# Python Dependencies
COPY requirements/main.txt .
RUN pip install -r main.txt

COPY . /app
WORKDIR /app

# Run the application
EXPOSE 80

ENTRYPOINT ["/app/scripts/bootstrap.sh"]
