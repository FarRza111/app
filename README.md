# FastAPI Project

A simple FastAPI project with basic setup.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn main:app --reload
```

## Available Endpoints

- `GET /`: Welcome message
- `GET /health`: Health check endpoint
- `GET /docs`: Swagger documentation (provided by FastAPI)
- `GET /redoc`: ReDoc documentation (provided by FastAPI)

## Development

The server will reload automatically when you make changes to the code.
