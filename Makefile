lint:
	poetry run black request_curl tests

test:
	poetry run pytest tests