## Local Application Setup

1. Create virtual environment:

```
python3 -m venv venv
```
2. Activate virtual environment:
```
source venv/bin/activate
```
3. Install poetry:
```
pip install poetry
```
4. Install dependencies:
```
poetry install
```
5. Install pre-commit hooks:
```
pre-commit install
```
6. Configure environment
```
cat .env.default > .env
```
7. Add ruff linter extension:
```
https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff
```

<br></br>

## Local Database Access

1. Install psql:
```
<package_manager> <action> psql
```

2. Log into locally running Postgres instance:
```
psql -h localhost -p 5432 -U apollo apollo
```
3. Create readonly user:
```
CREATE USER <your_user> WITH PASSWORD '<your_password>';
GRANT pg_read_all_data to <your_user>;
```
4. Log out and log in back with readonly user:
```
psql -h localhost -p 5432 -U <your_user> apollo
```