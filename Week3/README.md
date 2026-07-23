# Task API — Week 3 (Postgres + Docker)

This week extends the Week 2 Task API by replacing the in-memory task list with a real PostgreSQL database, running in Docker. The app and database now start together with a single command, and data survives a full restart of both the app and the container.

## What changed from Week 2

- Storage moved from a Python list in memory to a PostgreSQL database
- A repository layer (`repository.py`) now handles all database queries
- **The routes and service logic in `main.py` did not change in shape** — every route still accepts the same input and returns the same JSON shape as before. Only what each route calls underneath changed (a Python list operation → a SQL query). This is the repository pattern: swapping storage should only touch one layer.

## How it's built — step by step

### 1. Postgres in Docker, with a volume

Postgres runs in its own container. By default, a container's filesystem is wiped when the container is removed — so Postgres's data folder is mounted to a **named Docker volume** (`pgdata`) instead. The volume lives independently of the container; deleting and recreating the container does not delete the data.

### 2. `.env` — the connection string

The app needs to know how to reach Postgres: host, port, username, password, database name. This lives in `.env`, loaded at startup with `python-dotenv`, and is never committed to git. `.env.example` is committed instead, with placeholder values, so anyone cloning the repo knows what to fill in.

```
DATABASE_URL=postgresql://username:password@host:5432/dbname
```

### 3. `schema.sql` — the table definition

A single SQL file defines the `tasks` table:

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT false
);
```

`SERIAL` auto-generates each new task's `id`, replacing the manual max-id logic from the in-memory version. This file has to be run against the database once (Postgres doesn't run it automatically unless placed in a special init folder).

### 4. `database.py` — the connection pool

Opening a fresh database connection on every request would be slow. Instead, a **connection pool** (a small set of reusable connections) opens once, when the app starts, using FastAPI's `lifespan` feature:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))
    yield
    await app.state.db_pool.close()
```

The pool is stored on `app.state`, so any route can reach it.

### 5. `repository.py` — the data access layer

Each function here takes the connection pool and runs one SQL query, using **parameterized queries** (`$1`, `$2`, ...) rather than string-formatting values into SQL — this prevents SQL injection. Results come back as `asyncpg.Record` objects and are converted to plain Python dictionaries with `dict(row)`, so they match the shape the routes already expect.

| Function | SQL |
|---|---|
| `get_all_tasks(pool)` | `SELECT * FROM tasks` |
| `get_task(id, pool)` | `SELECT * FROM tasks WHERE id = $1` |
| `insert_task(title, pool)` | `INSERT INTO tasks (title, done) VALUES ($1, $2) RETURNING *` |
| `replace_task(id, title, done, pool)` | `UPDATE tasks SET title = COALESCE($1, title), done = COALESCE($2, done) WHERE id = $3 RETURNING *` |
| `delete_task(id, pool)` | `DELETE FROM tasks WHERE id = $1 RETURNING *` |

`COALESCE(new_value, existing_value)` picks the new value if it's provided, otherwise keeps the existing column value — this is what allows updating just `title`, just `done`, or both, in one query.

### 6. `main.py` — the swap

Every route now grabs the pool from `request.app.state.db_pool`, calls the matching repository function, and returns the result — instead of reading/writing the old in-memory list directly.

### 7. `Dockerfile` — packaging the app itself

Postgres uses an official, pre-built image, so it needs no Dockerfile. The FastAPI app is custom code, so it needs its own recipe for how to build it into a runnable image:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8. `docker-compose.yml` — running both together

Compose defines two services — `db` (Postgres) and `web` (this app, built from the Dockerfile) — on a shared private network. Containers on that network reach each other by service name, not `localhost`. That's why the connection string inside Compose points to `db`, not `localhost`:

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: a2
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:devpassword@db:5432/a2
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
```

**The healthcheck matters:** `depends_on` alone only controls start *order*, not whether Postgres is actually ready to accept connections. Without the healthcheck, the app container could start and try to connect before Postgres finished initializing, and crash. The healthcheck makes `web` wait until `db` reports genuinely ready.

## How to run

```bash
docker compose up
```

This builds the app image (first run only), starts both containers, and connects them. The API is available at `http://localhost:8000`, docs at `http://localhost:8000/docs`.

If starting from a completely fresh volume (no `tasks` table yet), run the schema once:
```bash
docker exec -i week3-db-1 psql -U postgres -d a2 < schema.sql
```

## Proving persistence

To confirm data survives a full restart of both the app and the database container:

1. Create tasks through the running API
2. Confirm they exist: `curl -i http://localhost:8000/tasks`
3. Fully tear down the stack: `docker compose down` (this removes both containers and the network — but not the volume)
4. Bring it back up: `docker compose up`
5. Check again: `curl -i http://localhost:8000/tasks`

**Actual result:**

```
Before down/up:
[{"id":1,"title":"Assignment 3","done":false},{"id":2,"title":"Test Task","done":false}]

$ docker compose down
✔ Container week3-web-1 Removed
✔ Container week3-db-1  Removed
✔ Network week3_default Removed

$ docker compose up
db-1  | PostgreSQL Database directory appears to contain a database; Skipping initialization
db-1  | database system is ready to accept connections
web-1 | Application startup complete.

After down/up:
[{"id":1,"title":"Assignment 3","done":false},{"id":2,"title":"Test Task","done":false}]
```

Both containers were fully removed and rebuilt, and the tasks were still there. This works because the data lives in the `pgdata` Docker volume, which is independent of the containers — deleting and recreating containers does not touch the volume.

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | / | API info |
| GET | /health | Health check |
| GET | /tasks | List all tasks |
| GET | /tasks/{id} | Get one task |
| POST | /tasks | Create a task |
| PUT | /tasks/{id} | Update a task's title and/or done status |
| DELETE | /tasks/{id} | Delete a task |

## A gotcha worth remembering

Docker Compose automatically prefixes volume names with the project folder name. A volume named `pgdata` in `docker-compose.yml`, run from a folder called `Week3`, actually becomes `week3_pgdata` — a separate volume from one created manually outside Compose with the same short name. This caused a `relation "tasks" does not exist` error the first time the stack was brought up with Compose, since the new volume had never had the schema applied to it. Fixed by running `schema.sql` against the correct container. To avoid this and reuse an existing volume deliberately, mark it `external: true` in the `volumes:` section.