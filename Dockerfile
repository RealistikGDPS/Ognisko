FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

# Python Dependencies
COPY requirements/main.txt .
RUN pip install -r main.txt

COPY ./tests /app/tests
COPY ./requirements /app/requirements
COPY ./scripts /app/scripts
WORKDIR /app

# Run the application
EXPOSE 80

ENTRYPOINT ["/app/scripts/bootstrap.sh"]
