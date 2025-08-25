from models import Restaurant

RESTAURANTS = [
    Restaurant(
        id=1,
        name="The Golden Spoon",
        cuisine="Italian",
        location="Downtown",
        price_range="$$",
        rating=4.2,
        capacity=50,
        available_times=["12:00", "13:00", "14:00", "18:00", "19:00", "20:00"],
        features=["Outdoor seating", "Vegan options", "Wine bar"]
    ),
    Restaurant(
        id=2,
        name="Sunset Bistro",
        cuisine="French",
        location="Midtown",
        price_range="$$$",
        rating=4.5,
        capacity=40,
        available_times=["11:30", "12:30", "18:30", "19:30", "20:30"],
        features=["Romantic ambiance", "Prix fixe menu", "Sommelier"]
    ),
    Restaurant(
        id=3,
        name="Spice Garden",
        cuisine="Indian",
        location="Uptown",
        price_range="$",
        rating=4.1,
        capacity=60,
        available_times=["12:00", "13:00", "17:30", "18:30", "19:30", "20:00"],
        features=["Buffet available", "Halal options", "Spice levels"]
    ),
    Restaurant(
        id=4,
        name="Ocean View",
        cuisine="Seafood",
        location="Waterfront",
        price_range="$$$$",
        rating=4.7,
        capacity=35,
        available_times=["17:00", "18:00", "19:00", "20:00"],
        features=["Ocean view", "Fresh catch", "Raw bar"]
    ),
    Restaurant(
        id=5,
        name="Taco Libre",
        cuisine="Mexican",
        location="Downtown",
        price_range="$",
        rating=3.9,
        capacity=80,
        available_times=["11:00", "12:00", "13:00", "17:00", "18:00", "19:00", "20:00", "21:00"],
        features=["Happy hour", "Live music", "Margaritas"]
    ),
    Restaurant(
        id=6,
        name="Zen Garden",
        cuisine="Japanese",
        location="Business District",
        price_range="$$$",
        rating=4.4,
        capacity=30,
        available_times=["12:00", "13:00", "18:00", "19:00", "20:00"],
        features=["Sushi bar", "Sake selection", "Private rooms"]
    ),
    Restaurant(
        id=7,
        name="Mediterranean Breeze",
        cuisine="Mediterranean",
        location="Old Town",
        price_range="$$",
        rating=4.0,
        capacity=45,
        available_times=["12:00", "13:00", "14:00", "18:00", "19:00", "20:00"],
        features=["Patio dining", "Mezze plates", "Greek wines"]
    ),
    Restaurant(
        id=8,
        name="The Steakhouse",
        cuisine="American",
        location="Financial District",
        price_range="$$$$",
        rating=4.6,
        capacity=55,
        available_times=["17:30", "18:30", "19:30", "20:30"],
        features=["Dry aged beef", "Cigar lounge", "Whiskey bar"]
    ),
    Restaurant(
        id=9,
        name="Noodle Express",
        cuisine="Chinese",
        location="Chinatown",
        price_range="$",
        rating=3.8,
        capacity=25,
        available_times=["11:00", "12:00", "13:00", "17:00", "18:00", "19:00", "20:00"],
        features=["Hand pulled noodles", "Quick service", "Vegetarian options"]
    ),
    Restaurant(
        id=10,
        name="Farm Table",
        cuisine="American",
        location="Suburbs",
        price_range="$$",
        rating=4.3,
        capacity=65,
        available_times=["11:00", "12:00", "13:00", "17:00", "18:00", "19:00", "20:00"],
        features=["Farm to table", "Seasonal menu", "Family friendly"]
    )
]

def get_all_restaurants():
    return RESTAURANTS

def find_restaurant_by_name(name):
    for restaurant in RESTAURANTS:
        if restaurant.name.lower() == name.lower():
            return restaurant
    return None

def search_restaurants(cuisine=None, location=None, price_range=None):
    results = RESTAURANTS
    
    if cuisine:
        results = [r for r in results if r.cuisine.lower() == cuisine.lower()]
    
    if location:
        results = [r for r in results if r.location.lower() == location.lower()]
    
    if price_range:
        results = [r for r in results if r.price_range == price_range]
    
    return results