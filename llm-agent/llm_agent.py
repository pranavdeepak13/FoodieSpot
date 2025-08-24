import os
import json
import logging
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

HF_API_URL = os.environ.get("HF_API_URL", "https://api-inference.huggingface.co/models/llama-3.1-8b-Instrcut")
HF_API_KEY = os.environ.get("HF_API_KEY", "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")

def call_llm_api(prompt: str) -> dict:
    """
    Calls the Hugging Face Inference API with the provided prompt.
    
    The prompt should instruct the model to output a JSON string containing
    the keys 'intent' and 'parameters'.
    
    Parameters:
        prompt (str): The prompt containing conversation context and instructions.
    
    Returns:
        dict: Parsed JSON response from the model.
    """
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True}
    }
    
    logger.debug("Calling Hugging Face LLM API at %s with payload: %s", HF_API_URL, payload)
    
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        output = response.json()
        logger.debug("Received response from HF API: %s", output)
        if isinstance(output, list) and len(output) > 0:
            generated_text = output[0].get("generated_text", "")
            logger.debug("Extracted generated text: %s", generated_text)
            try:
                parsed_output = json.loads(generated_text)
                return parsed_output
            except json.JSONDecodeError as e:
                logger.error("Error parsing generated text as JSON: %s", e)
                return {"intent": "unknown", "parameters": {}}
        else:
            logger.error("Unexpected response format from HF API: %s", output)
            return {"intent": "unknown", "parameters": {}}
    except requests.exceptions.RequestException as e:
        logger.error("Error calling HF API: %s", e)
        return {"intent": "unknown", "parameters": {}}

def process_user_input(user_message: str) -> dict:
    """
    Processes the user's input by constructing a detailed prompt and calling the LLM.
    
    The prompt instructs the model to determine if the user wants to book a reservation
    or get a restaurant recommendation. It then returns a JSON object with the keys 'intent'
    and 'parameters'.
    
    Parameters:
        user_message (str): The raw input message from the user.
    
    Returns:
        dict: A dictionary with keys 'intent' and 'parameters'.
    """
    logger.info("Processing user input: %s", user_message)
    prompt_template = (
        "You are an intelligent assistant for FoodieSpot. Given the user's message below, "
        "determine whether the user wants to book a reservation or get a restaurant recommendation. "
        "Return a JSON object with keys 'intent' (possible values: 'book_reservation', "
        "'recommend_restaurant', or 'unknown') and 'parameters' (extract details such as restaurant name, "
        "date, time, number of people, cuisine, location, etc. If a parameter is missing, set its value to null).\n"
        "User Message: \"{user_message}\"\n"
    )
    prompt = prompt_template.format(user_message=user_message)
    logger.debug("Constructed prompt: %s", prompt)
    
    return call_llm_api(prompt)

if __name__ == "__main__":
    test_input = "I would like to book a table for 4 this Saturday at Sunset Bistro."
    result = process_user_input(test_input)
    print("LLM Processing Result:", result)
