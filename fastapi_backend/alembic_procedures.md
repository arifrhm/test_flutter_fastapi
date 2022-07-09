To do migrations
=====

from container or pods, go to this directory /app/app/migrations

run this everytime schema db has changed without dropping tables.

# Generate Migration
```bash
$ alembic stamp head
$ alembic revision --autogenerate -m "<your update message, ex: change column>"
```

# Running Migration
```bash
$ alembic upgrade head
$ alembic stamp head
```