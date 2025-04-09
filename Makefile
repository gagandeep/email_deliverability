.PHONY: test docs clean publish

test:
	python -m unittest discover tests

docs:
	cd docs && make html

clean:
	rm -rf build/ dist/ *.egg-info
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

publish:
	./scripts/publish.sh

install-dev:
	pip install -e ".[dev]"