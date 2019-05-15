init:
	pip install -r requirements.txt

test: lint unit-tests

unit-tests:
	nosetests

lint:
	pylint --load-plugins pylint_quotes craftai tests

yolo:
	nosetests --exe -v --nocapture tests/test_pandas_add_operations_bulk.py

update-readme:
	./scripts/update_readme.sh

version-increment-major:
	./scripts/update_version.sh major

version-increment-minor:
	./scripts/update_version.sh minor

version-increment-patch:
	./scripts/update_version.sh patch
