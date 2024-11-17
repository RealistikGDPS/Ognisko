#!/usr/bin/make
build:
	docker build -t ognisko:latest .

lint:
	pre-commit run --all-files
