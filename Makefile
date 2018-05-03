.PHONY: install
install:
	rm -rf dist/*
	python setup.py sdist
	pip install dist/*

.PHONY: upload-pypi
upload-pypi:
	pip install --upgrade pip setuptools wheel
	pip install twine
	sh deploy/pypi_upload.sh