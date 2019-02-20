init:
	pip install -r requirements.txt --user

test: lint unit-tests

unit-tests:
	nosetests --exe

bulk-test:
	nosetests --exe tests/test_create_agents.py tests/test_delete_agents.py tests/test_get_decision_trees.py

bulk-test-debug:
	nosetests --exe -v --nocapture tests/test_add_operations_bulk.py

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
