1. Create virtual environment: `python3 -m venv venv`

2. Activate virtual environment: `source venv/bin/activate`

3. Install poetry: `pip install poetry`

4. Install dependencies: `poetry install`

5. Install pre-commit hooks: `pre-commit install`

6. Configure environment `cat .env.default | tee .env .env.test`

7. Add ruff linter extension: `https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff`