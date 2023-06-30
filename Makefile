#!/usr/bin/make
build:
	docker build -t realistikgdps .

run:
	docker-compose up \
		redis \
		mysql \
		meilisearch \
		realistikgdps

shell:
	docker run -it --net=host --entrypoint /bin/bash realistikgdps:latest
