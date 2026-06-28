# Alembic Migrations

This directory contains database migration scripts for the backend.

## Running Migrations

### Generate a new migration (autogenerate)

```bash
cd backend
alembic revision --autogenerate -m "description"
```

### Apply migrations

```bash
cd backend
alembic upgrade head
```

### Rollback one migration

```bash
cd backend
alembic downgrade -1
```

### View migration history

```bash
cd backend
alembic history
```

### View current revision

```bash
cd backend
alembic current
```

## Notes

- The `env.py` file imports all models to ensure autogenerate detects them.
- Database URL is configured in `alembic.ini`.
- For Docker deployment, migrations should be run inside the backend container.
