\# Task API — Week 2



A simple CRUD API for managing a to-do list, built with FastAPI. Data is stored in memory (no database yet — that's Week 3).



\## What this is



This API lets you create, read, update, and delete tasks in a to-do list. Each task has an `id`, a `title`, and a `done` flag. All data is kept in a Python list in memory — nothing is saved to disk, so restarting the server resets the list back to its 3 starting example tasks.



\## How to run



1\. Create and activate a virtual environment:

&#x20;  ```

&#x20;  python -m venv venv

&#x20;  venv\\Scripts\\Activate.ps1

&#x20;  ```

2\. Install dependencies:

&#x20;  ```

&#x20;  pip install fastapi uvicorn

&#x20;  ```

3\. Start the server:

&#x20;  ```

&#x20;  uvicorn main:app --reload --port 8000

&#x20;  ```

4\. Visit `http://localhost:8000` or `http://localhost:8000/docs` for Swagger UI.



\## Endpoints



| Method | Path | Description |

|---|---|---|

| GET | / | API info |

| GET | /health | Health check |

| GET | /tasks | List all tasks |

| GET | /tasks/{id} | Get one task |

| POST | /tasks | Create a task |

| PUT | /tasks/{id} | Update a task (title and/or done) |

| DELETE | /tasks/{id} | Delete a task |



\## Example curl requests



Create a task:

```

curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\\"title\\": \\"Buy milk\\"}"



HTTP/1.1 201 Created

content-type: application/json



{"id":102,"title":"Buy milk","done":false}

```



Get one task:

```

curl -i http://localhost:8000/tasks/102



HTTP/1.1 200 OK

content-type: application/json



{"id":102,"title":"Buy milk","done":false}

```



Unknown task:

```

curl -i http://localhost:8000/tasks/999



HTTP/1.1 404 Not Found

content-type: application/json



{"error":"Task 999 not found"}

```



\## Example of All Curl Commands:

```

curl.exe -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\\"title\\": \\"Test cycle task\\"}"

curl.exe -i http://localhost:8000/tasks

curl.exe -i -X PUT http://localhost:8000/tasks/102 -H "Content-Type: application/json" -d "{\\"title\\": \\"Updated cycle task\\"}"

curl.exe -i -X PUT http://localhost:8000/tasks/102 -H "Content-Type: application/json" -d "{\\"done\\": true}"

curl.exe -i -X DELETE http://localhost:8000/tasks/102

curl.exe -i http://localhost:8000/tasks

```



\## Swagger UI screenshots



\*\*List all tasks (GET /tasks)\*\*



!\[List all tasks](images/list-tasks.png)



\*\*Get one task / view (GET /tasks/{id})\*\*



!\[View one task](images/view-task.png)



\*\*Create a task (POST /tasks)\*\*



!\[Create task](images/create-task.png)



\*\*Update a task (PUT /tasks/{id})\*\*



!\[Update task](images/update-task.png)



\*\*Delete a task (DELETE /tasks/{id})\*\*



!\[Delete task](images/delete-task.png)



\## Notes : The mortality experiment



Since tasks are stored in a plain Python list in memory, restarting the server wipes out everything I created, updated, or deleted during that run. So the list resets back to the 3 hardcoded example tasks defined in the code. This is exactly why a real database is needed for anything that has to survive a restart or a crash, which is the focus of Week 3.

