default: docker

# Run all tests
test: lint test-quick

# Run only unit tests quickly
test-quick:
	py.test

# Run code formatter
fmt:
	yapf . -r -i

# Run python linter
lint:
	flake8

# Debug locally with flask
debug:
	FLASK_DEBUG=1 python flask_app.py

# Migrates to the loaded database
migrate: load
	docker-compose up migrate

# Load and migrate all required infrastructure (databases, caches, etc)
load:
	docker-compose up -d db

# Install local development requirements using your running version of python
install:
	pip install -r requirements-dev.txt

# Start using development mode
dev: load install migrate debug

# Start with docker
docker:
	docker-compose up -d
	docker-compose logs -f

# Build with docker
build:
	docker-compose build

# Deploy to production
deploy:
	docker-compose -f docker-compose.yml -f docker-compose-prod.yml up -d

# Clean up local files and one-time run containers
clean:
	find . | \
	grep -E "(__pycache__|\.pyc$$|\.sqlite$$)" | \
	xargs rm -rf && \
	docker-compose rm -f

# Remove all local code, stopped containers, and databases for this project
purge: clean
	rm -rf mnt

# Kill the running applications (docker-only)
kill:
	docker-compose kill

# In case you really need to clean house, but don't want to waste time spelling out all the commands
stalin: kill purge

# All together now!
.PHONY: test test-quick fmt lint debug migrate load install dev docker build deploy clean purge kill stalin
