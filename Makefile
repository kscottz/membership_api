default: test

install:
	pip install -r requirements.txt

test:
	py.test

fmt:
	yapf . -r -i

lint:
	flake8

install-dev:
	pip install -r requirements-dev.txt

run:
	python flask_app.py

clean:
	find . | \
	grep -E "(__pycache__|\.pyc$$|\.sqlite$$)" | \
	xargs rm -rf

.PHONY: init test fmt run install clean
