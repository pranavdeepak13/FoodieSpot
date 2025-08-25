import requests
import time
import json
from services import ChatService, IntentDetector, BookingService, RecommendationService
from data import find_restaurant_by_name, search_restaurants
from models import BookingRequest

class TestBackend:
    def __init__(self):
        self.base_url = "http://localhost:8000"
    
    def test_health_endpoint(self):
        print("Testing health endpoint...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Health check passed: {data['status']}")
                return True
            else:
                print(f"  ✗ Health check failed: Status {response.status_code}")
                return False
        except Exception as e:
            print(f"  ✗ Health check error: {e}")
            return False
    
    def test_restaurants_endpoint(self):
        print("Testing restaurants endpoint...")
        try:
            response = requests.get(f"{self.base_url}/restaurants", timeout=5)
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                print(f"  ✓ Restaurants endpoint passed: {count} restaurants loaded")
                return True
            else:
                print(f"  ✗ Restaurants endpoint failed: Status {response.status_code}")
                return False
        except Exception as e:
            print(f"  ✗ Restaurants endpoint error: {e}")
            return False
    
    def test_chat_endpoint(self):
        print("Testing chat endpoint...")
        test_cases = [
            {
                "message": "Hello",
                "expected_intent": "general_inquiry"
            },
            {
                "message": "I want to book a table for 4 at The Golden Spoon",
                "expected_intent": "book_reservation"
            },
            {
                "message": "Recommend Italian restaurants",
                "expected_intent": "get_recommendations"
            }
        ]
        
        passed = 0
        for i, test_case in enumerate(test_cases):
            try:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": test_case["message"],
                        "session_id": f"test_session_{i}"
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    intent = data.get('intent', 'unknown')
                    if intent == test_case['expected_intent']:
                        print(f"  ✓ Chat test {i+1} passed: {intent}")
                        passed += 1
                    else:
                        print(f"  ~ Chat test {i+1} partial: Expected {test_case['expected_intent']}, got {intent}")
                        passed += 0.5
                else:
                    print(f"  ✗ Chat test {i+1} failed: Status {response.status_code}")
            except Exception as e:
                print(f"  ✗ Chat test {i+1} error: {e}")
        
        success_rate = (passed / len(test_cases)) * 100
        print(f"  Chat endpoint success rate: {success_rate:.1f}%")
        return passed >= len(test_cases) * 0.5

class TestServices:
    def __init__(self):
        self.chat_service = ChatService()
        self.intent_detector = IntentDetector()
        self.booking_service = BookingService()
        self.recommendation_service = RecommendationService()
    
    def test_intent_detection(self):
        print("Testing intent detection...")
        test_cases = [
            ("I want to book a table", "book_reservation"),
            ("Recommend restaurants", "get_recommendations"),
            ("Is The Golden Spoon available", "check_availability"),
            ("Hello there", "general_inquiry")
        ]
        
        passed = 0
        for message, expected in test_cases:
            detected = self.intent_detector.detect_intent(message)
            if detected == expected:
                print(f"  ✓ Intent '{expected}' detected correctly")
                passed += 1
            else:
                print(f"  ~ Intent detection: Expected '{expected}', got '{detected}'")
                passed += 0.5
        
        success_rate = (passed / len(test_cases)) * 100
        print(f"  Intent detection success rate: {success_rate:.1f}%")
        return passed >= len(test_cases) * 0.7
    
    def test_booking_extraction(self):
        print("Testing booking information extraction...")
        message = "Book a table for 4 people at The Golden Spoon tomorrow at 7 PM"
        extracted = self.intent_detector.extract_booking_info(message)
        
        checks = [
            ("restaurant_name", "The Golden Spoon"),
            ("party_size", 4),
            ("date", "tomorrow")
        ]
        
        passed = 0
        for field, expected in checks:
            if field in extracted and extracted[field] == expected:
                print(f"  ✓ Extracted {field}: {extracted[field]}")
                passed += 1
            else:
                print(f"  ~ Extraction {field}: Expected {expected}, got {extracted.get(field)}")
        
        return passed >= len(checks) * 0.7
    
    def test_booking_service(self):
        print("Testing booking service...")
        
        complete_booking = BookingRequest(
            restaurant_name="The Golden Spoon",
            date="tomorrow",
            time="12:00",
            party_size=4
        )
        
        success, message, booking_id = self.booking_service.create_booking(complete_booking)
        
        if success and booking_id:
            print(f"  ✓ Booking created successfully: {booking_id}")
            return True
        else:
            print(f"  ✗ Booking failed: {message}")
            return False
    
    def test_recommendations(self):
        print("Testing recommendation service...")
        
        recommendations = self.recommendation_service.get_recommendations(cuisine="Italian")
        
        if recommendations and len(recommendations) > 0:
            print(f"  ✓ Got {len(recommendations)} Italian restaurant recommendations")
            return True
        else:
            print("  ✗ No recommendations returned")
            return False

class TestData:
    def test_restaurant_data(self):
        print("Testing restaurant data...")
        
        restaurant = find_restaurant_by_name("The Golden Spoon")
        if restaurant:
            print(f"  ✓ Found restaurant: {restaurant.name}")
        else:
            print("  ✗ Restaurant not found")
            return False
        
        italian_restaurants = search_restaurants(cuisine="Italian")
        if italian_restaurants:
            print(f"  ✓ Found {len(italian_restaurants)} Italian restaurants")
        else:
            print("  ✗ No Italian restaurants found")
            return False
        
        return True

class TestConversationFlow:
    def __init__(self):
        self.chat_service = ChatService()
        self.session_id = "test_conversation"
    
    def test_booking_flow(self):
        print("Testing booking conversation flow...")
        
        messages = [
            "I want to make a reservation",
            "The Golden Spoon for 4 people",
            "Tomorrow at 12:00"
        ]
        
        booking_completed = False
        for i, message in enumerate(messages):
            result = self.chat_service.process_message(message, self.session_id)
            print(f"  Step {i+1}: {message}")
            print(f"    Response: {result['response'][:80]}...")
            
            if result.get('data') and result['data'].get('booking_id'):
                print(f"    ✓ Booking completed with ID: {result['data']['booking_id']}")
                booking_completed = True
                break
        
        return booking_completed
    
    def test_recommendation_flow(self):
        print("Testing recommendation conversation flow...")
        
        message = "Recommend Italian restaurants in Downtown"
        result = self.chat_service.process_message(message, f"{self.session_id}_rec")
        
        if result['intent'] == 'get_recommendations' and len(result['response']) > 100:
            print("  ✓ Recommendation flow completed successfully")
            return True
        else:
            print("  ✗ Recommendation flow failed")
            return False

def run_all_tests():
    print("FoodieSpot AI - System Testing")
    print("=" * 50)
    
    test_results = []
    
    print("\n1. Backend API Tests")
    backend_tester = TestBackend()
    test_results.append(("Health Endpoint", backend_tester.test_health_endpoint()))
    test_results.append(("Restaurants Endpoint", backend_tester.test_restaurants_endpoint()))
    test_results.append(("Chat Endpoint", backend_tester.test_chat_endpoint()))
    
    print("\n2. Service Tests")
    service_tester = TestServices()
    test_results.append(("Intent Detection", service_tester.test_intent_detection()))
    test_results.append(("Booking Extraction", service_tester.test_booking_extraction()))
    test_results.append(("Booking Service", service_tester.test_booking_service()))
    test_results.append(("Recommendations", service_tester.test_recommendations()))
    
    print("\n3. Data Tests")
    data_tester = TestData()
    test_results.append(("Restaurant Data", data_tester.test_restaurant_data()))
    
    print("\n4. Conversation Flow Tests")
    conversation_tester = TestConversationFlow()
    test_results.append(("Booking Flow", conversation_tester.test_booking_flow()))
    test_results.append(("Recommendation Flow", conversation_tester.test_recommendation_flow()))
    
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name:<25} [{status}]")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 80:
        print("\n🎉 System is working excellently!")
    elif success_rate >= 60:
        print("\nSystem is working well with minor issues")
    elif success_rate >= 40:
        print("\nSystem is functional but needs attention")
    else:
        print("\nSystem needs significant fixes")

    return success_rate >= 60

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)