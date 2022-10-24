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

# Temporary workaround for my xor cipher module being broken
ENV CYTHONISE = 1
RUN apt-get install -y git
RUN git clone https://github.com/RealistikDash/xor_cipher
RUN pip install cython
RUN cd xor_cipher && python3 setup.py build_ext --inplace && pip install . && cd ..

# Python Dependencies
COPY requirements/requirements.txt .
RUN pip install -r requirements.txt

# Move scripts to /app
RUN apt update && apt install default-mysql-client -y
COPY scripts /app/scripts

# Copy the application
COPY realistikgdps /app/realistikgdps
COPY main.py /app/

# Run the application
EXPOSE 80
CMD ["./scripts/bootstrap.sh"]
