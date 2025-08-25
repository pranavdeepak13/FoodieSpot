from services import ContextSwitchChatService

def test_context_switching():
    service = ContextSwitchChatService()
    session_id = "test_session"
    
    print("=== TESTING FIXED CONTEXT SWITCHING ===")
    
    print("\n1. Initial booking request:")
    result1 = service.process_message("Book table for 4 at Ocean View tomorrow 7PM", session_id)
    print(f"Response: {result1['response'][:100]}...")
    
    session = service.session_manager.get_session(session_id)
    print(f"Last successful booking: {session['last_successful_booking']}")
    print(f"Current booking after step 1: {session['current_booking']}")
    
    print("\n2. Modifying party size:")
    result2 = service.process_message("Actually, make it 6 people", session_id)
    print(f"Response: {result2['response'][:200]}...")
    
    session = service.session_manager.get_session(session_id)
    booking = session["current_booking"]
    print(f"Current booking after modification:")
    print(f"  Restaurant: {booking.restaurant_name}")
    print(f"  Date: {booking.date}")
    print(f"  Time: {booking.time}")
    print(f"  Party size: {booking.party_size}")
    
    print("\n3. Modifying time:")
    result3 = service.process_message("And change the time to 8PM", session_id)
    print(f"Response: {result3['response'][:200]}...")
    
    session = service.session_manager.get_session(session_id)
    booking = session["current_booking"]
    print(f"Final booking state:")
    print(f"  Restaurant: {booking.restaurant_name}")
    print(f"  Date: {booking.date}")
    print(f"  Time: {booking.time}")
    print(f"  Party size: {booking.party_size}")
    
    missing = service.session_manager.get_missing_fields(session_id)
    print(f"Missing fields: {missing}")
    
    context = service.session_manager.get_booking_context(session_id)
    print(f"Context string: {context}")

if __name__ == "__main__":
    test_context_switching()