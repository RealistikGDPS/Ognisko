#!/usr/bin/make
build:
	docker build -t realistikgdps .

run:
	docker-compose up \
		redis \
		mysql \
		realistikgdps
