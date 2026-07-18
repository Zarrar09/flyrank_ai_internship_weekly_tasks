async def get_all_tasks(pool):
    rows = await pool.fetch("SELECT * FROM tasks")
    return [dict(row) for row in rows]


async def get_task(id, pool):
    row = await pool.fetchrow("SELECT * FROM tasks WHERE id = $1", id)
    if row is None:
        return None
    
    return dict(row)

async def insert_task(title, pool):
    row = await pool.fetchrow(
        "INSERT INTO tasks (title, done) VALUES ($1, $2) RETURNING *", title, False
    )
    
    return dict(row)

async def replace_task(id, title, done, pool):
    row = await pool.fetchrow(
        "UPDATE tasks SET title = COALESCE($1, title), done = COALESCE($2, done) WHERE id = $3 RETURNING *",
        title, done, id
    )
    if row is None:
        return None
    return dict(row)

async def delete_task(id, pool):
    row = await pool.fetchrow(
        "DELETE FROM tasks WHERE id = $1 RETURNING *", id
    )
    
    if row is None:
        return None
    
    return dict(row)