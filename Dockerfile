FROM python:3.9

ENV PYTHONUNBUFFERED=1
ENV USE_ENV_CONFIG=1

WORKDIR /app

# Temporary workaround for my xor cipher module being broken
ENV CYTHONISE = 1
RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/RealistikDash/xor_cipher
RUN pip install cython
RUN cd xor_cipher && python3 setup.py build_ext --inplace && pip install . && cd ..

# Python Dependencies
COPY requirements/requirements.txt .
RUN pip install -r requirements.txt

# Extra Dependencies (dependencies I usually didn't need but Docker somehow needs)
RUN pip install python-multipart cryptography

# Copy the application
COPY realistikgdps /app/realistikgdps
COPY main.py /app/

# Run the application
EXPOSE 80
CMD ["python", "/app/main.py"]
