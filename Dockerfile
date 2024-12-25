FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

# Python Dependencies
COPY requirements/main.txt .
RUN pip install -r main.txt --no-cache-dir

# Copy the pre-requisites
COPY ./tests /app/tests
COPY ./requirements /app/requirements
COPY ./scripts /app/scripts

# Copy the application
COPY ./ognisko /app/ognisko
WORKDIR /app

ENTRYPOINT ["/app/scripts/bootstrap.sh"]
