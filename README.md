# AAP Agentic Server

A Python microservice that provides a REST API for initiating and checking the status of Agentic AI workflows using the llama-stack ReActAgent module.

## Features

- REST API with two main endpoints:
  - `POST /api/send_chat` - Submit a chat message to the AI Agent
  - `POST /api/get_chat` - Retrieve the status and response from an agent session
- Asynchronous agent execution
- Session management for tracking multiple concurrent conversations
- Comprehensive test suite

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

Start the server using:
```bash
python main.py
```

The server will run on `http://0.0.0.0:8000` by default.

## API Endpoints

### POST /api/send_chat
Submit a chat message to the AI Agent.

**Request Body:**
```json
{
  "text": "What model are you?"
}
```

**Response:**
```json
{
  "session_id": "uuid-string"
}
```

### POST /api/get_chat
Retrieve the current status and response from an AI Agent session.

**Request Body:**
```json
{
  "session_id": "uuid-string"
}
```

**Response:**
```json
{
  "response": "Agent response text...",
  "chat_complete": false
}
```

### GET /health
Health check endpoint.

## Running Tests

Run the test suite with:
```bash
pytest tests/
```

## Project Structure

```
aap-agentic-server/
├── app/
│   ├── __init__.py
│   ├── api.py              # FastAPI application and endpoints
│   ├── agent_service.py    # Agent service with ReActAgent integration
│   ├── models.py           # Pydantic models for requests/responses
│   └── session_manager.py  # Session management
├── tests/
│   ├── __init__.py
│   └── test_api.py         # Test cases
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Notes

- The implementation includes a fallback mechanism if llama-stack is not available, allowing the service to run for testing purposes.
- Agent execution is handled asynchronously to prevent blocking the API.
- Sessions are tracked in-memory. For production use, consider using a persistent storage solution.

