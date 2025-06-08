# TalentAdore Tech Lead Assignment

A sample microservices-based system built with FastAPI, PostgreSQL, Docker & Docker Compose.  
It consists of:

- **Gateway Service**: Unified entrypoint (`/api/...`), aggregates OpenAPI specs, proxies requests  
- **Member Service**: Manages organization members  
- **Feedback Service**: Manages feedback entries  

All services are containerized, configurable via `.env`, self-documenting (Swagger), TDD-driven (Pytest) and include automatic data seeding on first startup.

---

## 🚀 Quickstart

1. **Clone & env**  
   ```bash
   git clone <repo-url>
   cd <repo>
   cp .env.example .env

2. **Run the stack**

   ```bash
   docker-compose up --build
   ```

   * Gateway ⇢ `http://localhost:8000`
   * Member service ⇢ `http://localhost:8001`
   * Feedback service ⇢ `http://localhost:8002`

3. **Access docs**

   * Gateway Swagger UI ⇢ `http://localhost:8000/docs`
   * Member service docs ⇢ `http://localhost:8001/docs`
   * Feedback service docs ⇢ `http://localhost:8002/docs`

4. **Development (hot-reload)**
   An optional `docker-compose.override.yml` mounts local code and runs Uvicorn with `--reload`.
   Just edit and save `.py` files—no rebuild required.

5. **Run tests**

   ```bash
   # In separate shells, for each service:
   docker exec -it member_service pytest
   docker exec -it feedback_service pytest
   docker exec -it gateway pytest       # if you added gateway tests
   ```

---

## 🗂️ Project Structure

```
.
├── gateway_service/
│   ├── app/
│   │   ├── main.py        # FastAPI gateway with OpenAPI aggregation & proxy
│   │   ├── config.py      # SERVICE URLs & prefixes
│   │   └── routes/proxy.py
│   └── Dockerfile
├── member_service/
│   ├── app/
│   │   ├── main.py        # FastAPI member app
│   │   ├── db.py          # SQLAlchemy engine + retry + get_db
│   │   ├── models.py      # Member table
│   │   ├── schemas.py     # Pydantic models
│   │   ├── crud.py
│   │   ├── routers/members.py
│   │   ├── seed.py        # Initial data seeding
│   │   └── tests/
│   └── Dockerfile
├── feedback_service/
│   ├── app/               # same layout as member_service
│   │   └── seed.py        # Feedback seeding
│   └── Dockerfile
├── docker-compose.yml
├── docker-compose.override.yml  # for hot-reload development
├── .env.example
└── README.md
```

---

## 📋 API Endpoints (via Gateway)

| Method     | Path             | Description                   |
| ---------- | ---------------- | ----------------------------- |
| **GET**    | `/health`        | Gateway health check          |
| **GET**    | `/api/members/`  | List non-deleted members      |
| **POST**   | `/api/members/`  | Create a member               |
| **DELETE** | `/api/members/`  | Soft-delete all members       |
| **GET**    | `/api/feedback/` | List non-deleted feedbacks    |
| **POST**   | `/api/feedback/` | Create feedback               |
| **DELETE** | `/api/feedback/` | Soft-delete all feedbacks     |
| **POST**   | `/refresh-docs`  | Regenerate aggregated OpenAPI |

---

## ✅ Features

* **Microservices**: Independently deployable Member & Feedback services
* **API Gateway**: Single base URL, dynamic OpenAPI aggregation, transparent proxy
* **Dockerized**: `Dockerfile` per service + `docker-compose.yml`
* **Config & Secrets**: All via `.env` & environment variables
* **ORM & Migrations**: SQLAlchemy with automatic `create_all`
* **Database Seeding**: Sample data on first startup (`app/seed.py`)
* **Testing**: Pytest unit & integration tests (in-memory SQLite)
* **TDD Workflow**: Tests first, then implementation
* **Hot-Reload**: No rebuild needed
