init:
	pip install -r requirements.txt --user

test: lint unit-tests

unit-tests:
	nosetests

lint:
	pylint --load-plugins pylint_quotes craftai tests

update-readme:
	./scripts/update_readme.sh

version-increment-major:
	./scripts/update_version.sh major

version-increment-minor:
	./scripts/update_version.sh minor

version-increment-patch:
	./scripts/update_version.sh patch
