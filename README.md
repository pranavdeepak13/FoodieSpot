# FoodieSpot AI - Restaurant Reservation System

A conversational AI system for restaurant reservations and recommendations built with FastAPI and Streamlit.

## Architecture

```
Frontend (Streamlit) ←→ Backend (FastAPI) ←→ Services (Business Logic) ←→ Data (Restaurants)
```

## Features

- **Natural Language Booking**: "Book a table for 4 at The Golden Spoon tomorrow at 7 PM"
- **Restaurant Recommendations**: Get suggestions based on cuisine, location, and preferences  
- **Availability Checking**: View restaurant details and available time slots
- **Session Management**: Maintains conversation context within browser session
- **Chat Interface**: Claude-like conversational experience

## Quick Start

### 1. Setup Environment

```bash
mkdir foodiespot
cd foodiespot

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Start Backend

```bash

python server.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 3. Start Frontend

```bash

streamlit run app.py
```

Expected output:
```
Local URL: http://localhost:8501
```

## Project Structure

```
foodiespot-ai/
├── app.py              # Streamlit frontend (chat interface)
├── server.py           # FastAPI backend (API endpoints)  
├── models.py           # Data models (Restaurant, Booking, etc.)
├── services.py         # Business logic (ChatService, BookingService, etc.)
├── data.py             # Restaurant database (10 sample restaurants)
├── test_system.py      # Testing suite
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## API Endpoints

### POST /chat

```json
Request:
{
    "message": "Book a table for 4 at The Golden Spoon",
    "session_id": "user-session-123"
}

Response:
{
    "response": "I'll help you book that table...",
    "intent": "book_reservation", 
    "data": {"booking_id": "abc123"}
}
```

### GET /health
Health check endpoint
```json
Response:
{
    "status": "healthy",
    "service": "FoodieSpot AI",
    "version": "1.0.0"
}
```

### GET /restaurants
Get all restaurants
```json
Response:
{
    "restaurants": [...],
    "count": 10
}
```

## Testing

### Run All Tests
```bash
python test_system.py
```

### Manual Testing Scenarios

**Booking Flow:**
1. "I want to make a reservation"
2. "The Golden Spoon for 4 people"  
3. "Tomorrow at 7 PM"

**Recommendations:**
- "Recommend Italian restaurants"
- "Find restaurants in Downtown"
- "Show me upscale dining options"

**Availability:**
- "Check availability at Sunset Bistro"
- "What time slots are available?"

## System Components

### Frontend (app.py)
- **Streamlit Chat Interface**: Chat-like conversation experience
- **Session Management**: Maintains conversation state until browser refresh
- **Error Handling**: Graceful handling of backend connectivity issues
- **Real-time Updates**: Immediate message display with loading indicators

### Backend (server.py)  
- **FastAPI REST API**: Three simple endpoints (/chat, /health, /restaurants)

### Services (services.py)
- **ChatService**: Main orchestrator for processing user messages
- **IntentDetector**: Rule-based intent classification using regex patterns
- **BookingService**: Handles reservation creation and validation
- **RecommendationService**: Filters and ranks restaurants
- **SessionManager**: Maintains conversation state and partial booking data

### Data Layer (data.py)
- **Restaurant Database**: 10 diverse restaurants with different cuisines and locations

## Troubleshooting

### Backend won't start
```bash
lsof -i :8000

kill -9 $(lsof -t -i:8000)
```

### Frontend can't connect to backend
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check firewall settings
3. Ensure both services use correct ports

### Import errors
```bash
source venv/bin/activate

pip list | grep fastapi
pip list | grep streamlit
```

### Session not persisting
- Session data persists until browser refresh
- Each browser tab gets separate session
- Backend sessions stored in memory only
