# 🚀 Apollo — Local Development Guide

1️⃣ Create and initialize the virtual environment & install dependencies:
```bash
make install
```
This will:
- create a virtual environment in `venv/` (if not already there)
- install all dependencies (including editable `apollo` and `poethepoet`) using `uv`

2️⃣ Activate the virtual environment:
```bash
source venv/bin/activate
```

3️⃣ Install pre-commit hooks:
```bash
pre-commit install
```

4️⃣ Configure environment variables:
```bash
cp .env.default .env
```

5️⃣ Install the Ruff linter extension for VSCode:
👉 [Ruff VSCode extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

6️⃣ Install `psql` (PostgreSQL client):
```bash
<package_manager> <install_command> postgresql
```
*(replace `<package_manager>` and `<install_command>` with your OS-specific command, e.g. `brew install postgresql` on Mac)*

7️⃣ Log into the locally running Postgres instance:
```bash
psql -h localhost -p 5432 -U apollo apollo
```

8️⃣ Create a readonly user:
```sql
CREATE USER <your_user> WITH PASSWORD '<your_password>';
GRANT pg_read_all_data TO <your_user>;
```

9️⃣ Log out and log back in as the readonly user:
```bash
psql -h localhost -p 5432 -U <your_user> apollo
```