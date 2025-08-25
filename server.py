from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, ChatResponse
from services import ContextSwitchChatService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FoodieSpot AI",
    description="Restaurant reservation and recommendation system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_service = ContextSwitchChatService()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Received message: {request.message[:50]}...")
        
        result = chat_service.process_message(request.message, request.session_id)
        
        response = ChatResponse(
            response=result["response"],
            intent=result["intent"],
            data=result["data"]
        )
        
        logger.info(f"Sending response with intent: {result['intent']}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Sorry, I encountered an error processing your request. Please try again."
        )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "FoodieSpot AI",
        "version": "1.0.0"
    }

@app.get("/restaurants")
async def get_restaurants():
    from data import get_all_restaurants
    restaurants = get_all_restaurants()
    return {
        "restaurants": [r.dict() for r in restaurants],
        "count": len(restaurants)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)