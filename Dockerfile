FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV USE_ENV_CONFIG=1
ENV HTTP_PORT=80

WORKDIR /app

# Python Dependencies
COPY requirements/requirements.txt .
RUN pip install -r requirements.txt

# Copy the application
COPY realistikgdps/ /app/realistikgdps/

# Run the application
CMD ["python", "realistikgdps/main.py"]
