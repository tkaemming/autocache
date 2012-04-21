install-dev:
	pip install -qr requirements.development.txt

check: install-dev
	find . -name \*.py -not -path \*tests\* | xargs pyflakes
	pep8 --repeat ./

test: install-dev
	nosetests --verbose

.PHONY: check install-dev test
