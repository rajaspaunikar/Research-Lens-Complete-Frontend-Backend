# Research Lens Backend API

The backend engine powering **Research Lens**, a platform built to scrape, analyze, and index research papers from sources like **arXiv**. Using NLP and automation, the system extracts metadata, tracks trends, and exposes insights through a high-performance REST API.

This backend automates research discovery by analyzing temporal trends, extracting keywords, downloading PDFs, and serving structured data to the frontend.

---

## Project Structure

```
├── README.md
├── requirements.txt
└── src
    ├── analysis                      # NLP logic (keyword extraction, trends, summarization)
    │   ├── metadata_extractor.py
    │   └── trend_analyzer.py
    ├── api.py                        # FastAPI routes and endpoint definitions
    ├── database
    │   └── db_manager.py             # PostgreSQL + SQLAlchemy ORM
    ├── main.py                       # CLI entry point for scraping/initialization
    ├── scraper                       # arXiv scraping engine (PDF downloads + metadata)
    │   ├── old
    │   │   └── scraper_version0.1.ipynb
    │   ├── scraper.py
    │   └── test_scraper.py
    └── tasks                         # Background automation and scheduling
        └── auto_task.py
```

---

## Tech Stack

- **Framework:** Python, FastAPI  
- **Database:** PostgreSQL + SQLAlchemy ORM  
- **Scraping:** BeautifulSoup4, Requests  
- **NLP:** Spacy, Regex, Hugging Face Transformers  
- **Server Runtime:** Uvicorn  

---

## Key Features

-  **Automated Scraping**  
  Fetches papers (title, abstract, metadata, PDF) from arXiv and other sources.

-  **Metadata Extraction**  
  Title parsing, keyword extraction, topic mapping.

-  **Trend Analysis**  
  Calculates keyword popularity and growth velocity over time.

-  **Paper Summarization**  
  NLP-based summarization using transformer models.

-  **PDF Management**  
  Automatic downloads with local caching and DB tracking.

-  **Report Generation**  
  Create PDF reports with trends, charts, and summaries.

-  **Alert System**  
  Configurable Slack/Email alerts for new papers matching filters.

-  **Citation Metrics**  
  Integrates citation counts via Semantic Scholar API.

---

##  Getting Started

### 1 Prerequisites

- Python **3.10+**
- PostgreSQL server running

---

### 2 Installation

```bash
pip install -r requirements.txt
```

---

### 3 Environment Setup

Create a `.env` file:

```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/research_lens
```

---

### 4 Initialize Database & Run First Scrape

```bash
cd src
python main.py init
```

This fetches and indexes the most recent research papers.

---

### 5 Run the API Server

```bash
# From inside src/
uvicorn api:app --reload --port 8000
```

API available at:

```
http://localhost:8000
```

Interactive docs:

```
http://localhost:8000/docs
```

---

## Key API Endpoints

| Method | Endpoint                             | Description |
|--------|--------------------------------------|-------------|
| GET    | `/api/dashboard/stats`               | Returns global paper statistics and insights |
| GET    | `/api/papers`                        | Search, filter, and paginate papers |
| GET    | `/api/analytics/keyword-trends`      | Keyword velocity and trend history |
| POST   | `/api/papers/{id}/download`          | Downloads and stores PDF locally |

---
