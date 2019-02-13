init:
	pip install -r requirements.txt --user

test: lint unit-tests

unit-tests:
	nosetests --exe

bulk-test:
	nosetests --exe tests/test_create_bulk_agents.py tests/test_delete_bulk_agents.py tests/test_get_bulk_decision_trees.py

bulk-test-debug:
	nosetests --exe -v --nocapture tests/test_create_bulk_agents.py

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
