# Tech Spec: MarTech RAG Ad Copy Generator

## 1. Background & Goals
* **Background**: When running advertisement campaigns, we need to generate multiple ad copies for A/B testing. However, we typically face two main challenges:
    1. **Time constraints**: During seasonal campaigns or festivals, we lack the time to manually write dozens of ad variations for testing, which limits our ability to optimize performance for our clients.
    2. **Lack of domain knowledge**: Junior colleagues may lack experience in specific industries, making it difficult for them to write accurate and effective ad copy.
* **Goals**: The primary goal is to significantly reduce the time spent on copywriting while improving the overall quality and relevance of the ad copy.
* **Non-Goals**: Image generation and building an admin dashboard are excluded from the MVP.

## 2. System Architecture
* **Core Components**:
    * **API Framework**: FastAPI
    * **LLM Engine**: OpenAI API (ChatGPT)
    * **RAG Framework**: LlamaIndex
    * **Vector Database**: ChromaDB
    * **Task Queue**: Celery & Redis
* **Data Flow**:
    1. The client sends an API request containing keywords and context (e.g., target festival or product category).
    2. The FastAPI endpoint dispatches an asynchronous task to Celery and immediately returns a `task_id`.
    3. In the background, the Celery worker retrieves contextually relevant historical ad copies from the vector database (ChromaDB) using LlamaIndex.
    4. The worker constructs a prompt combining the retrieved context and the user's keywords, then sends it to the LLM to generate 5 ad copy variations.
    5. The worker saves the result to the database, allowing the client to fetch it using the `task_id`.

## 3. API Design

### 3.1 Generate Copy (POST)
* **Endpoint**: `POST /api/v1/generate-copy`
* **Request Body (JSON)**:
    ```json
    {
      "keyword": "string",
      "promotional_price": 0.0,
      "original_price": 0.0,
      "product_category": "string",
      "promotional_content": "string"
    }
    ```
* **Response (JSON)**:
    ```json
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "processing"
    }
    ```

### 3.2 Check Task Status (GET)
* **Endpoint**: `GET /api/v1/tasks/{task_id}`
* **Response (JSON)**:
    ```json
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "completed",
      "result": {
        "ad_copies": ["copy 1", "copy 2", "copy 3", "copy 4", "copy 5"]
      }
    }
    ```

## 4. Data Storage
* **Relational Database (PostgreSQL / SQLite)**:
    * Stores task statuses (e.g., pending, completed, failed) and historical generation logs.
* **Vector Database (ChromaDB)**:
    * Stores vectorized historical ad copies along with metadata (e.g., `{"product_category": "drink", "festival": "mother's day"}`) for precise pre-filtering during retrieval.

## 5. Trade-offs
* **Why Celery over FastAPI BackgroundTasks?**
    * While BackgroundTasks is built-in and easy, Celery + Redis provides a robust, distributed queue system. It supports task retries, monitoring, and scaling, which is critical for handling long-running, unpredictable LLM API calls in a production environment.
* **Why RAG over Fine-tuning?**
    * RAG is more cost-effective and flexible. It allows us to update our "knowledge base" simply by inserting data into the vector database without retraining the model. It also prevents the LLM from hallucinating by anchoring its responses to real historical data.
* **Why FastAPI over Django?**
    * This project is heavily I/O-bound (waiting for Vector DB and LLM APIs). FastAPI's native asynchronous support (`async/await`) handles this far more efficiently than Django's synchronous architecture.
* **Why LlamaIndex over LangChain?**
    * LlamaIndex is specifically optimized for data ingestion and retrieval (RAG) with a cleaner API. LangChain's abstractions can be overly complex for our focused use case.
* **Why both PostgreSQL and ChromaDB?**
    * We need "polyglot persistence": PostgreSQL is for structured, relational data (user sessions, task states), while ChromaDB is purpose-built for storing high-dimensional vectors and performing fast similarity searches.

## 6. Future Enhancements
1. Implement AI-driven image generation for ad creatives.
2. Integrate A/B testing performance monitoring (e.g., CTR tracking).
3. Implement a feedback loop: Feed high-performing ad copies back into the Vector Database to continuously improve the RAG generation quality.
