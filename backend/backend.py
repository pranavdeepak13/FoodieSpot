import torch
import logging
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from data.restaurants_data import restaurants

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, torch_dtype=torch.bfloat16, device_map="auto"
)

text_generator = pipeline(
    "text-generation", model=model, tokenizer=tokenizer, device_map="auto",
    truncation=True,            
    pad_token_id=128001
)

app = FastAPI()

class QueryRequest(BaseModel):
    user_query: str
    max_length: int = 500


def generate_booking_id():
    return "BOOK-" + str(random.randint(100000, 999999))


def determine_intent(prompt: str) -> dict:

    try:
        response = text_generator(
            prompt,
            max_length=500,
            num_return_sequences=1,
            temperature=0.7,
            top_k=50,
            top_p=0.95
        )
        generated_text = response[0]["generated_text"]
        return eval(generated_text) 
    except Exception as e:
        logger.error(f"LLM error: {e}")
        raise HTTPException(status_code=500, detail="Intent detection failed.")


def book_reservation(parameters: dict) -> str:
    required_fields = ["restaurant", "date", "time", "people"]
    missing_fields = [field for field in required_fields if field not in parameters or not parameters[field]]

    if missing_fields:
        return f"Missing details: {', '.join(missing_fields)}. Please provide them."

    restaurant_name = parameters["restaurant"]
    selected_restaurant = next((r for r in restaurants if r["name"].lower() == restaurant_name.lower()), None)

    if not selected_restaurant:
        return "Restaurant not found. Please choose another."

    if parameters["time"] not in selected_restaurant["available_slots"]:
        return f"{restaurant_name} is unavailable at {parameters['time']}. Try another time."

    booking_id = generate_booking_id()
    confirmation_message = f"""
    ✅ **Reservation Confirmed!** ✅
    ---
    **Restaurant:** {selected_restaurant["name"]}
    **Cuisine:** {selected_restaurant["cuisine"]}
    **Location:** {selected_restaurant["location"]}
    **Seating:** {selected_restaurant["seating"]}
    **Capacity:** {selected_restaurant["capacity"]} people
    **Date & Time:** {parameters['date']} at {parameters['time']}
    **Booking ID:** `{booking_id}`
    ---
    🎉 We’re excited to have you! Your table is ready. Enjoy your meal at **{selected_restaurant["name"]}**! 🍽️
    """
    return confirmation_message


def recommend_restaurant(parameters: dict) -> str:
    cuisine = parameters.get("cuisine")
    location = parameters.get("location")

    filtered_restaurants = [
        r for r in restaurants if
        (not cuisine or r["cuisine"].lower() == cuisine.lower()) and
        (not location or r["location"].lower() == location.lower())
    ]

    if not filtered_restaurants:
        return "No matching restaurants found. Try adjusting your preferences."

    recommendations = "\n".join([f"- {r['name']} ({r['cuisine']} in {r['location']})" for r in filtered_restaurants[:3]])
    return f"Here are some great recommendations for you:\n{recommendations}"


@app.post("/query")
async def query_llm(request: QueryRequest):
    intent_data = determine_intent(request.user_query)
    intent = intent_data.get("intent", "unknown")
    parameters = intent_data.get("parameters", {})

    if intent == "book_reservation":
        return {"response": book_reservation(parameters)}
    elif intent == "recommend_restaurant":
        return {"response": recommend_restaurant(parameters)}
    else:
        return {"response": "I didn't understand that. Can you clarify?"}


@app.post("/custom_query")
async def custom_llm_request(request: QueryRequest):
    return {"response": determine_intent(request.user_query)}