install-dev:
	pip install -qr requirements.development.txt

test: install-dev
	nosetests --verbose

.PHONY: test
