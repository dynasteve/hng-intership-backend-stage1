# 🧠 String Analyzer (HNGI Stage 1 Task)

A RESTful API built with FastAPI that analyzes strings and stores their computed properties in a PostgreSQL database. Made for the HNG Internship Stage 1

It supports:

String property analysis (length, palindrome, etc.)

Querying and filtering stored strings

Natural language filtering

Deletion of strings

## 🚀 Features

For each analyzed string, the API computes and stores:

- Property	Description
- length -	Number of characters
- is_palindrome	- Whether the string reads the same forwards/backwards
- unique_characters	- Count of distinct characters
- word_count - Number of words separated by whitespace
- sha256_hash -	SHA-256 hash used as a unique ID
- character_frequency_map - JSON map of each character to its frequency

## ⚙️ Tech Stack

- FastAPI — modern Python web framework
- PostgreSQL — production-grade database
- SQLAlchemy ORM — for database models and queries
- Pydantic — request/response validation
- Uvicorn — ASGI server
- Python 3.10+

## Project Structure
```bash
string_analyzer/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── dependencies.py
│   ├── routes/
│   │   └── strings.py
│   └── services/
│       └── analyzer.py
├── tests/
│   └── test_api.py
├── .env
├── requirements.txt
└── README.md
```
---

## Setup Instructions
### 1️⃣ Clone Repository
```bash
git clone https://github.com/<your-username>/string-analyzer-service.git
cd string-analyzer-service
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate (Windows)
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables
Create a .env file in the project root:
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/string_analyzer_db
⚠️ Replace <username> and <password> with your actual PostgreSQL credentials.

### 🗄️ Database Setup

Start PostgreSQL and create the database:
```bash
CREATE DATABASE string_analyzer_db;
```

### Create tables:
```bash
python -c "from app.database import Base, engine; import app.models; Base.metadata.create_all(bind=engine)"
```

---

## ▶️ Run the Application

Start the FastAPI development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at:
👉 http://127.0.0.1:8000

Interactive docs:
👉 http://127.0.0.1:8000/docs

## Example Requests
### Create / Analyze String

#### POST /strings
```bash
curl -X POST "http://127.0.0.1:8000/strings" \
-H "Content-Type: application/json" \
-d '{"value": "A man a plan a canal Panama"}'
```

#### Get Specific String
```bash
GET /strings/A%20man%20a%20plan%20a%20canal%20Panama
```

#### Filter Strings
```bash
GET /strings?is_palindrome=true&min_length=5&word_count=1
```

#### Natural Language Filter
```bash
GET /strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings
```

#### Delete String
```bash
DELETE /strings/hello
```

---

🧠 Author

- Name: Stephen Tosisiye Akande
- Email: tosisiyesteve@gmail.com
- GitHub: www.github.com/dynasteve
- LinkedIn: www.linkedin.com/in/stephen-akande-tos