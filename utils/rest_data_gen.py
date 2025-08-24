restaurant_names = [
    "The Golden Spoon", "Blue Horizon Eatery", "Sunset Bistro", "Urban Palate",
    "The Rustic Fork", "Spice Route Cafe", "The Velvet Table", "Olive & Vine",
    "Crimson Plate", "Emerald Garden", "The Silver Fork", "Harbor View Grill",
    "Riverstone Kitchen", "The Gourmet Loft", "Bella Cucina", "Midnight Diner",
    "Rustic Charm", "Ocean Breeze Grill", "Maple & Main", "The Secret Ingredient",
    "Urban Oasis", "Twilight Terrace", "The Red Door Cafe", "Saffron Spice Lounge",
    "The White Orchid", "Garden of Flavors", "The Copper Kettle", "Pearl's Table",
    "Sunrise Cafe", "Cascade Bistro", "The Enchanted Fork", "Sapphire Lounge",
    "Golden Harvest", "The Urban Grille", "Ivory Plate", "The Garden Gate",
    "Moonlight Diner", "The Chic Chef", "Radiant Flavors", "The Bold Bite",
    "Noble Nosh", "Urban Essence", "Terra Bella", "The Classic Corner",
    "Velvet Vine", "Culinary Canvas", "Harmony Bistro", "Fusion Feast",
    "The Epicurean Spot", "Luminous Lounge"
]

addresses = [
    "101 Golden Ave, Downtown", "202 Maple Street, Uptown", "303 Pine Road, Midtown",
    "404 Oak Lane, City Center", "505 Cedar Blvd, Waterfront", "606 Birch Street, Old Town",
    "707 Elm Avenue, Suburban", "808 Willow Road, Business District", "909 Cherry Lane, Downtown",
    "110 Spruce Street, Uptown", "111 Redwood Ave, Midtown", "112 Poplar Road, City Center",
    "113 Cypress Lane, Waterfront", "114 Ash Street, Old Town", "115 Beech Avenue, Suburban",
    "116 Hickory Road, Business District", "117 Sycamore Lane, Downtown", "118 Magnolia Street, Uptown",
    "119 Dogwood Avenue, Midtown", "120 Palm Road, City Center", "121 Fir Lane, Waterfront",
    "122 Sequoia Street, Old Town", "123 Juniper Avenue, Suburban", "124 Alder Road, Business District",
    "125 Hemlock Lane, Downtown", "126 Larch Street, Uptown", "127 Maple Avenue, Midtown",
    "128 Spruce Road, City Center", "129 Oak Lane, Waterfront", "130 Pine Street, Old Town",
    "131 Cedar Avenue, Suburban", "132 Birch Road, Business District", "133 Elm Lane, Downtown",
    "134 Willow Street, Uptown", "135 Cherry Avenue, Midtown", "136 Poplar Road, City Center",
    "137 Ash Lane, Waterfront", "138 Beech Street, Old Town", "139 Hickory Avenue, Suburban",
    "140 Sycamore Road, Business District", "141 Magnolia Lane, Downtown", "142 Dogwood Street, Uptown",
    "143 Palm Avenue, Midtown", "144 Fir Road, City Center", "145 Sequoia Lane, Waterfront",
    "146 Juniper Street, Old Town", "147 Alder Avenue, Suburban", "148 Hemlock Road, Business District",
    "149 Larch Lane, Downtown", "150 Cedar Street, Uptown"
]

cuisines = [
    "Italian", "Japanese", "Indian", "Mexican", "French", "Chinese", "American",
    "Mediterranean", "Thai", "Spanish", "Lebanese", "Turkish", "Korean", "Vietnamese", "Greek"
]
seatings = ["Indoor", "Outdoor", "Booth", "Private Dining"]
ambiances = ["Casual", "Romantic", "Family-friendly", "Upscale", "Trendy", "Cozy"]
price_ranges = ["$", "$$", "$$$", "$$$$"]
open_hours_options = ["10:00 AM - 10:00 PM", "11:00 AM - 11:00 PM", "12:00 PM - 12:00 AM", "9:00 AM - 9:00 PM"]
capacities = [50, 75, 100, 125, 150, 175, 200]
special_requests_options = [
    "Offers vegan options", "Gluten-free options available", "Wheelchair accessible",
    "Live music on weekends", "Outdoor seating available", "Pet-friendly", "No special features"
]

restaurants = []

for i in range(50):
    cuisine = cuisines[i % len(cuisines)]
    seating = seatings[i % len(seatings)]
    ambience = ambiances[i % len(ambiances)]
    price_range = price_ranges[i % len(price_ranges)]
    open_hours = open_hours_options[i % len(open_hours_options)]
    capacity = capacities[i % len(capacities)]
    special_requests = special_requests_options[i % len(special_requests_options)]
    
    rating = round(3.5 + (i % 16) * 0.1, 1)
    if rating > 5.0:
        rating = 5.0

    valet_parking = (i % 2 == 0) 
    bar_available = (i % 2 != 0)    
    
    restaurant = {
        "id": i + 1,
        "name": restaurant_names[i],
        "address": addresses[i],
        "cuisine": cuisine,
        "seating": seating,
        "ambience": ambience,
        "price_range": price_range,
        "open_hours": open_hours,
        "capacity": capacity,
        "special_requests": special_requests,
        "rating": rating,
        "valet_parking": valet_parking,
        "bar_available": bar_available
    }
    restaurants.append(restaurant)

if __name__ == "__main__":
    # Write this to this file so that it can be imported in restaurant_data.py
    with open("./restaurants_data.py", "w") as f:
        f.write("restaurants = " + str(restaurants))
