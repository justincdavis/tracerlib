.PHONY: help install clean docs blobs test ci mypy

help: 
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  install    to install the package"
	@echo "  clean      to clean the directory tree"
	@echo "  docs       to generate the documentation"
	@echo "  ci 	    to run the CI workflows"
	@echo "  mypy       to run the type checker"
	@echo "  test       to run the tests"

install:
	pip3 install .

clean: 
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf tracerlib/*.egg-info
	rm -rf src/tracerlib/*.egg-info
	pyclean .

docs:
	rm -rf docs/source/*
	sphinx-apidoc -o docs/source/ src/tracerlib/
	cd docs && make html

ci:	
	-./scripts/ci/pyupgrade.sh
	python3 -m ruff ./src//tracerlib --fix
	python3 -m isort src/tracerlib
	python3 -m black src/tracerlib --safe
	python3 -m mypy src/tracerlib --config-file=pyproject.toml

mypy:
	python3 -m mypy src/tracerlib --config-file=pyproject.toml

test:
	./scripts/run_tests.sh
