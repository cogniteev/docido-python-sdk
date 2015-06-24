PYTHON ?= python

pypi_upload:
	$(PYTHON) setup.py sdist upload -r pypi --sign

pypi_register:
	$(PYTHON) setup.py sdist register -r pypi
