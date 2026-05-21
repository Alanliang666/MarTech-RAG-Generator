# MarTech-RAG-Generator

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg?style=flat-square)](https://www.python.org/)
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-Supported-blue?style=flat-square&logo=docker)](https://docs.docker.com/compose/)
[![GCP](https://img.shields.io/badge/GCP-%234285F4?style=flat-square&logo=google-cloud&logoColor=white)](https://cloud.google.com/)

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-%23DD0031?style=flat-square&logo=redis&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F00?style=flat-square&logo=databricks&logoColor=white)
![LlamaIndex](https://img.shields.io/badge/🦙%20LlamaIndex-07C27F?style=flat-square)
![Gemini](https://img.shields.io/badge/Google%20Gemini-8E75C2?style=flat-square&logo=googlegemini&logoColor=white)

</div>

---

## Stop wasting time writing ad copy from scratch

Feed it your past ad data, get perfectly personalized ad copy back in seconds. Save Your time!!

<img width="1152" height="648" alt="Image" src="https://github.com/user-attachments/assets/416daa2a-3407-4917-8d6f-587024557d84" />

---

## Key Features

| Feature | Description |
|---|---|
|  **Asynchronous Architecture** | Drop your data via FastAPI and get an instant response. Let Celery and Redis handle the heavy lifting in the background so you never have to wait for the server! |
|  **Personalized RAG Engine** | Feed your historical ad copy into the Vector Database. The AI easily retrieves this context to generate highly personalized and high-converting ad copy. |
|  **Flexible AI Integration** | Not locked into one option! Choose your preferred AI model to generate the perfect ad copy tailored to your needs. |
|  **Zero-Friction Setup** | Say goodbye to messy environment configs. With Docker Compose, you can get the entire system up and running with just one command. |
|  **Robust Data Persistence** | Keep your data safe and sound. We use PostgreSQL to robustly store your system metadata, perfectly paired with ChromaDB for your vector embeddings. |

---

## Tech Stack
API: FastAPI
Background Jobs: Celery
Broker: Redis
Database: PostgreSQL
Vector Store: ChromaDB
RAG Framework: LlamaIndex
LLM / Embeddings: Google Gemini
Dependency Management: Poetry
Containerization: Docker / Docker Compose

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT REQUEST                           │
│          (keywords, prompts, product details, etc.)             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│      FastAPI  (API & Initialization)                            │
│  • Validates payload                                            │
│  • Generates unique `task_id`                                   │
│  • Saves initial state ──────────────────────────► PostgreSQL   │
└──────────────────────────┬──────────────────────────────────────┘
                           │  Push Task
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│      Redis  (Message Queue / Broker)                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │  Pick Up Task
                           ▼
┌────────────────────────────────────────────────────────────────┐
│      Celery Worker  (Background Processing)                    │
│  • Updates task status → "Processing" in PostgreSQL            │
└────────────┬─────────────────────────────────────┬─────────────┘
             │  RAG Retrieval                      │
             ▼                                     │
┌────────────────────────────┐                     │
│      LlamaIndex            │                     |
│  Retrieves relevant        │                     │
│  historical ad copy from   │                     │
│  ChromaDB Vector Database  │                     │
└────────────┬───────────────┘                     │
             │  Context + Prompts                  │
             ▼                                     │
┌────────────────────────────┐                     │
│     LLM (Gemini / OpenAI)  │                     │
│  Generates personalized    │                     │
│  ad copy                   │                     │
└────────────┬───────────────┘                     │
             │  Save Result                        │
             └─────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│    PostgreSQL  (Completion)                                     │
│  • Saves generated copy                                         │
│  • Updates task status → "Success"                              │
│  • Client fetches result via `task_id`.                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- **Docker & Docker Compose** (for running the services)
- **Python 3.13+ & Poetry** (for local dependency management and running the indexer)

---

## Environment Variables

Configure your environment variables before starting the services. Copy the example file:

```bash
cp .env.example .env
```

Make sure to update the `.env` file with your specific configurations:

```env
YOUR_AI_API_KEY=your-api-key-here
REDIS_URL=redis://redis:6379/0
CHROMADB=./data/chroma
DATABASE_URL=postgresql+asyncpg://postgres:your_password_here@postgres:5432/postgres
```

> **Note:** If you are not using the default Docker setup, make sure to change the Redis and PostgreSQL URLs to match your local servers.

---

## 🚀 Getting Started


### 1. Install dependencies

```bash
poetry install
```

### 2. Install Dependencies & Index Data

Before generating ad copy, you need to ingest the historical data (`data/mock_ad_data.csv`) into the vector database.

> Feel free to modify the CSV file to input whatever historical ad copy you want!

```bash
poetry run python -m src/rag/indexer.py
```

### 3. Start the Services

Spin up the entire infrastructure (FastAPI, Celery Worker, Redis, PostgreSQL, and ChromaDB) in the background:

```bash
docker-compose up --build -d
```

### 4. Access the API Documentation

Once everything is up and running, head over to the interactive API documentation (Swagger UI) to try it out:

👉 **http://localhost:8000/docs**


<img width="1464" height="802" alt="Image" src="https://github.com/user-attachments/assets/17bc1602-2f6f-45a6-8b02-5f2e5461e0be" />

---

## API Endpoints

### Health Check
```http
GET /
```

Example response:

```json
{
  "message": "Welcome to MarTech RAG API!"
}
```

### Create Ad Copy Generation Task
```http
POST /api/v1/generate-copy
```

Request body:
```json
{
  "keyword": "mothers_day",
  "promotional_price": 499.0,
  "original_price": 800.0,
  "product_category": "skincare",
  "product_name": "Miracle Water",
  "promotional_content": "buy one get one free"
}
```

Example response:

```json
{
  "task_id": "uuid-string",
  "status": "processing",
  "result": null
}
```

<img width="1426" height="806" alt="Image" src="https://github.com/user-attachments/assets/0e69ed7b-4553-476b-8d0b-64c6e004c54b" />

### Get Task Status and Result
```http
GET /api/v1/tasks/{task_id}
```

Example response:

```json
{
  "task_id": "uuid-string",
  "status": "completed",
  "result": {
    "ad_copies": [
      "Generated ad copy..."
    ]
  }
}
```

If the task is still running, the status will remain processing.

<img width="1418" height="791" alt="Image" src="https://github.com/user-attachments/assets/46e1bea0-af2d-4610-be5a-6ca485ae3198" />

---

## Customization Notes

**AI Model Selection:** The default engine uses Google Gemini. If you wish to switch to a different model (like OpenAI), you will need to modify the RAG embedding and generation logic in the `src/rag` directory.

---

## Development 

### Run the API locally

```bash
poetry run uvicorn src.main:app --reload
```

Run the Celery worker locally:

```bash
poetry run celery -A src.worker worker --loglevel=info
```

## Testing

### Running Tests Locally

We maintain a testing suite using `pytest`. To ensure the async database operations and endpoints work correctly, we utilize `pytest-asyncio` and `httpx`.

**1. Install Development Dependencies:**

```bash
poetry install --with dev
```

**2. Execute the Test Suite:**

```bash
poetry run pytest -v
```

---

## CI/CD & Deployment (GCP Cloud Run)

<img width="800" height="800" alt="Image" src="https://github.com/user-attachments/assets/3e636407-48f9-4c66-b976-f7a94de2f926" />

This repository is configured with a production-ready GitHub Actions CI/CD pipeline.

Upon merging or pushing to the `main` branch, the workflow automatically:

1. **Builds and Pushes** the Docker image to Google Artifact Registry.

2. **Deploys Decoupled Services:** It intelligently deploys the exact same image into two separate GCP Cloud Run services for better scalability:
   - `martech-api` — The public-facing FastAPI service.
   - `martech-worker` — A background, unauthenticated service running the Celery worker (`celery -A src.worker worker`).

3. **Secret Management:** Environment variables are securely injected at runtime using GCP Secrets Manager.

---

## Contributing

Contributions are highly encouraged! Whether you want to optimize our system mechanisms, add support for new LLMs, or improve the RAG engine's retrieval accuracy, your input makes this project better.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag `"enhancement"`.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Contact & Let's Connect

Developed by **[Alanliang666](https://github.com/Alanliang666)**.

I am a developer deeply passionate about transitioning into a Software Engineering role, with a strong focus on building scalable backend architectures and reliable system monitoring mechanisms. If you're interested in discussing system design, open-source collaborations, or potential engineering opportunities, I'd love to connect!

- **GitHub:** [@Alanliang666](https://github.com/Alanliang666)
- **Email:** [alanliang0428@gmail.com](mailto:alanliang0428@gmail.com)

---

<div align="center">

Don't forget to give the project a star ⭐️ if you found it useful!

</div>
