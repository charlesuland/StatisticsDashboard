# StatisticsDashboard

This project is intended for my AI class. It is a dashboard for performing statistical models in user inputted data sets. 
The front end was built using Vue.js. The backend used FastAPI. 

## Docker / Development using Docker Compose

There is a `docker-compose.yml` that builds and runs two services:

- `backend` — a Python FastAPI app (served with uvicorn) built from `backend/Dockerfile`.
- `frontend` — the Vite-built Vue app served by Nginx, built from `my-frontend/Dockerfile`.

To build and run the app locally with Docker Compose:

```bash
docker-compose up
```

The backend will be available at http://localhost:8000 and the frontend at http://localhost:5173

Uploaded datasets are persisted to `backend/uploads` on the host (mounted into the backend container).
