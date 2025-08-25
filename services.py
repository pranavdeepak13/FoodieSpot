import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from models import BookingRequest, Booking
from data import get_all_restaurants, find_restaurant_by_name, search_restaurants

class BookingState(Enum):
    INITIAL = "initial"
    GATHERING_INFO = "gathering_info"
    MODIFYING = "modifying"
    CONFIRMING = "confirming"
    COMPLETED = "completed"

class ConversationContext:
    def __init__(self):
        self.booking_state = BookingState.INITIAL
        self.last_intent = None
        self.conversation_history = []
        self.last_modification_type = None
        self.modification_count = 0

class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def get_session(self, session_id: str) -> dict:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "conversation_history": [],
                "current_booking": BookingRequest(),
                "context": ConversationContext(),
                "last_intent": None,
                "last_successful_booking": None,
                "booking_history": []
            }
        return self.sessions[session_id]
    
    def save_successful_booking(self, session_id: str, booking: BookingRequest):
        session = self.get_session(session_id)
        session["last_successful_booking"] = BookingRequest(
            restaurant_name=booking.restaurant_name,
            date=booking.date,
            time=booking.time,
            party_size=booking.party_size
        )
        print(f"DEBUG: Saved successful booking: {session['last_successful_booking']}")
    
    def restore_booking_for_modification(self, session_id: str):
        session = self.get_session(session_id)
        if session["last_successful_booking"]:
            current = session["current_booking"]
            is_mostly_empty = not all([current.restaurant_name, current.date, current.time, current.party_size])
            
            if is_mostly_empty:
                print(f"DEBUG: Restoring booking data for modification")
                session["current_booking"] = BookingRequest(
                    restaurant_name=session["last_successful_booking"].restaurant_name,
                    date=session["last_successful_booking"].date,
                    time=session["last_successful_booking"].time,
                    party_size=session["last_successful_booking"].party_size
                )
                session["context"].booking_state = BookingState.MODIFYING
                print(f"DEBUG: Restored booking: {session['current_booking']}")
    
    def update_booking_info(self, session_id: str, new_info: dict, is_modification: bool = False):
        session = self.get_session(session_id)
        
        if is_modification:
            self.restore_booking_for_modification(session_id)
        
        current_booking = session["current_booking"]
        
        print(f"DEBUG: {'Modifying' if is_modification else 'Updating'} booking info")
        print(f"DEBUG: Current booking before update: restaurant={current_booking.restaurant_name}, date={current_booking.date}, time={current_booking.time}, party_size={current_booking.party_size}")
        print(f"DEBUG: New info to merge: {new_info}")
        
        changes_made = []
        
        for key, value in new_info.items():
            if value is not None:
                old_value = getattr(current_booking, key)
                setattr(current_booking, key, value)
                
                if old_value != value:
                    if is_modification and old_value is not None:
                        changes_made.append(f"{key}: {old_value} → {value}")
                        print(f"DEBUG: Modified {key}: {old_value} → {value}")
                    else:
                        changes_made.append(f"Added {key}: {value}")
                        print(f"DEBUG: Added {key}: {value}")
        
        print(f"DEBUG: Booking after update: restaurant={current_booking.restaurant_name}, date={current_booking.date}, time={current_booking.time}, party_size={current_booking.party_size}")
        
        return changes_made
    
    def get_booking_context(self, session_id: str) -> str:
        session = self.get_session(session_id)
        booking = session["current_booking"]
        context_parts = []
        
        if booking.restaurant_name:
            context_parts.append(f"Restaurant: {booking.restaurant_name}")
        if booking.date:
            context_parts.append(f"Date: {booking.date}")
        if booking.time:
            context_parts.append(f"Time: {booking.time}")
        if booking.party_size:
            context_parts.append(f"Party size: {booking.party_size}")
        
        return ", ".join(context_parts) if context_parts else "No booking details yet"
    
    def get_missing_fields(self, session_id: str) -> List[str]:
        session = self.get_session(session_id)
        booking = session["current_booking"]
        missing = []
        
        if not booking.restaurant_name:
            missing.append("restaurant")
        if not booking.date:
            missing.append("date")
        if not booking.time:
            missing.append("time")
        if not booking.party_size:
            missing.append("party size")
        
        return missing
    
    def clear_booking(self, session_id: str):
        session = self.get_session(session_id)
        print(f"DEBUG: Clearing booking - saving current booking first")
        self.save_successful_booking(session_id, session["current_booking"])
        session["current_booking"] = BookingRequest()
        session["context"].booking_state = BookingState.COMPLETED
    
    def start_new_booking(self, session_id: str):
        session = self.get_session(session_id)
        session["current_booking"] = BookingRequest()
        session["context"].booking_state = BookingState.INITIAL
        session["last_successful_booking"] = None
        print(f"DEBUG: Started fresh booking session")
    
    def add_message(self, session_id: str, role: str, message: str):
        session = self.get_session(session_id)
        session["conversation_history"].append({
            "role": role,
            "message": message,
            "timestamp": datetime.now()
        })

class AdvancedIntentDetector:
    def __init__(self):
        self.patterns = {
            "book_reservation": [
                r"book.*table|make.*reservation|reserve.*table",
                r"book.*for|table.*for|reservation.*for",
                r"want.*table|need.*table|like.*book",
                r"get.*table|find.*table",
                r"dinner.*reservation|lunch.*reservation"
            ],
            "modify_booking": [
                r"actually|change.*to|make.*it|switch.*to",
                r"instead|rather|no.*make.*it",
                r"change.*mind|different|another",
                r"update.*to|modify.*to|alter.*to",
                r"let.*make.*it|let.*change.*it"
            ],
            "get_recommendations": [
                r"recommend|suggest|find.*restaurant",
                r"what.*restaurant|where.*eat|good.*place",
                r"looking.*for.*food|want.*to.*eat",
                r"show.*me.*restaurant|best.*restaurant"
            ],
            "check_availability": [
                r"available|open|free.*table",
                r"check.*availability|is.*open",
                r"can.*get.*table|do.*you.*have"
            ],
            "provide_info": [
                r"^[A-Za-z\s]+$",
            ],
            "confirm_booking": [
                r"yes|yeah|yep|confirm|correct|right|ok|okay",
                r"that.*right|sounds.*good|perfect"
            ]
        }
        
        self.modification_indicators = [
            r"actually", r"instead", r"rather", r"change.*to", r"make.*it",
            r"no.*make.*it", r"switch.*to", r"different", r"another",
            r"update.*to", r"modify.*to", r"let.*make.*it", r"and\s+change"
        ]
        
        self.restaurant_names = [r.name.lower() for r in get_all_restaurants()]
    
    def detect_intent_with_context(self, message: str, context: ConversationContext, session_booking: BookingRequest) -> str:
        message_lower = message.lower().strip()
        print(f"DEBUG: Analyzing message: '{message_lower}' with context state: {context.booking_state}")
        
        is_modification = self._is_modification_request(message_lower)
        
        if is_modification:
            print(f"DEBUG: Detected modification request")
            return "modify_booking"
        
        if context.booking_state in [BookingState.GATHERING_INFO, BookingState.MODIFYING]:
            return self._detect_contextual_intent(message_lower, context, session_booking)
        
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    print(f"DEBUG: Found pattern '{pattern}' for intent '{intent}'")
                    return intent
        
        if any(name in message_lower for name in self.restaurant_names):
            return "provide_info"
        
        if re.search(r'\d', message_lower):
            return "provide_info"
        
        print(f"DEBUG: No pattern matched, returning general_inquiry")
        return "general_inquiry"
    
    def _is_modification_request(self, message: str) -> bool:
        for pattern in self.modification_indicators:
            if re.search(pattern, message):
                print(f"DEBUG: Found modification indicator: {pattern}")
                return True
        return False
    
    def _detect_contextual_intent(self, message: str, context: ConversationContext, booking: BookingRequest) -> str:
        if re.search(r'yes|yeah|yep|confirm|correct|ok|okay', message):
            return "confirm_booking"
        elif any(name in message for name in self.restaurant_names):
            return "provide_info"
        elif re.search(r'\d+\s*(?:people|person|guest|pax)', message):
            return "provide_info"
        elif re.search(r'\d+\s*(?:am|pm|:|AM|PM)', message):
            return "provide_info"
        elif re.search(r'today|tomorrow|tonight|\d+/\d+', message):
            return "provide_info"
        else:
            return "continue_booking"
    
    def extract_comprehensive_info(self, message: str) -> dict:
        info = {}
        message_lower = message.lower()
        print(f"DEBUG: Extracting comprehensive info from: '{message}'")
        
        restaurant_names = [r.name for r in get_all_restaurants()]
        for restaurant in restaurant_names:
            if restaurant.lower() in message_lower:
                info["restaurant_name"] = restaurant
                print(f"DEBUG: Found restaurant: {restaurant}")
                break
        
        time_info = self._extract_robust_time(message)
        if time_info:
            info["time"] = time_info
            print(f"DEBUG: Found time: {time_info}")
        
        party_size = self._extract_party_size_fixed(message_lower)
        if party_size:
            info["party_size"] = party_size
            print(f"DEBUG: Found party size: {party_size}")
        
        date_info = self._extract_date(message_lower)
        if date_info:
            info["date"] = date_info
            print(f"DEBUG: Found date: {date_info}")
        
        print(f"DEBUG: Extracted comprehensive info: {info}")
        return info
    
    def extract_modification_info(self, message: str) -> dict:
        info = {}
        message_lower = message.lower()
        print(f"DEBUG: Extracting modification info from: '{message}'")
        
        modification_patterns = {
            "party_size": [
                r"make.*it.*(\d+).*people",
                r"change.*to.*(\d+).*people",
                r"actually.*(\d+).*people",
                r"instead.*(\d+).*people",
                r"(\d+).*people.*instead",
                r"(\d+)\s*people"
            ],
            "time": [
                r"make.*it.*at.*(\d{1,2})\s*(am|pm|AM|PM)",
                r"change.*to.*(\d{1,2})\s*(am|pm|AM|PM)",
                r"actually.*(\d{1,2})\s*(am|pm|AM|PM)",
                r"instead.*(\d{1,2})\s*(am|pm|AM|PM)",
                r"(\d{1,2})\s*(am|pm|AM|PM).*instead",
                r"change.*time.*to.*(\d{1,2})\s*(am|pm|AM|PM)",
                r"(\d{1,2}):(\d{2})",
                r"(\d{1,2})\s*(am|pm|AM|PM)"
            ],
            "restaurant_name": [
                r"make.*it.*(The\s+[\w\s]+|[\w\s]+\s+Bistro|[\w\s]+\s+Garden|Ocean\s+View|[\w\s]+\s+Spoon)",
                r"change.*to.*(The\s+[\w\s]+|[\w\s]+\s+Bistro|[\w\s]+\s+Garden|Ocean\s+View|[\w\s]+\s+Spoon)",
                r"actually.*(The\s+[\w\s]+|[\w\s]+\s+Bistro|[\w\s]+\s+Garden|Ocean\s+View|[\w\s]+\s+Spoon)",
                r"instead.*(The\s+[\w\s]+|[\w\s]+\s+Bistro|[\w\s]+\s+Garden|Ocean\s+View|[\w\s]+\s+Spoon)"
            ]
        }
        
        for field, patterns in modification_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    if field == "party_size":
                        info[field] = int(match.group(1))
                        print(f"DEBUG: Found modification for {field}: {info[field]}")
                        break
                    elif field == "time":
                        if len(match.groups()) >= 2 and match.group(2):
                            hour = int(match.group(1))
                            period = match.group(2).lower()
                            if period == "pm" and hour != 12:
                                hour += 12
                            elif period == "am" and hour == 12:
                                hour = 0
                            info[field] = f"{hour:02d}:00"
                        elif len(match.groups()) >= 2:
                            info[field] = f"{int(match.group(1)):02d}:{int(match.group(2)):02d}"
                        else:
                            hour = int(match.group(1))
                            info[field] = f"{hour:02d}:00"
                        print(f"DEBUG: Found modification for {field}: {info[field]}")
                        break
                    elif field == "restaurant_name":
                        potential_name = match.group(1).strip()
                        restaurant_names = [r.name for r in get_all_restaurants()]
                        for restaurant in restaurant_names:
                            if restaurant.lower() in potential_name.lower() or potential_name.lower() in restaurant.lower():
                                info[field] = restaurant
                                print(f"DEBUG: Found modification for {field}: {restaurant}")
                                break
                        if field in info:
                            break
        
        if not info:
            print(f"DEBUG: No specific modification patterns found, using general extraction")
            info = self.extract_comprehensive_info(message)
        
        return info
    
    def _extract_robust_time(self, message: str) -> Optional[str]:
        print(f"DEBUG: Extracting time from: '{message}'")
        patterns = [
            r'(\d{1,2})\s*(?::(\d{2}))?\s*(am|pm|AM|PM)(?!\s*people)',
            r'(\d{1,2}):(\d{2})(?!\s*people)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.lastindex >= 2 and match.group(2) else 0
                period = match.group(match.lastindex) if match.lastindex >= 3 else None
                
                print(f"DEBUG: Time extraction - hour: {hour}, minute: {minute}, period: {period}")
                
                if period:
                    period = period.lower()
                    if period == "pm" and hour != 12:
                        hour += 12
                    elif period == "am" and hour == 12:
                        hour = 0
                
                result = f"{hour:02d}:{minute:02d}"
                print(f"DEBUG: Extracted time result: {result}")
                return result
        
        print(f"DEBUG: No time found")
        return None
    
    def _extract_party_size_fixed(self, message: str) -> Optional[int]:
        print(f"DEBUG: Extracting party size from: '{message}'")
        
        patterns = [
            r'(?:table\s+for|book.*for|reservation.*for)\s+(\d+)\s+(?:people|person|guest|pax)',
            r'(?:table\s+for|book.*for|reservation.*for)\s+(\d+)(?!\s*(?:am|pm|:\d+))',
            r'(\d+)\s+(?:people|person|guest|pax)(?!\s*(?:am|pm|:\d+))',
            r'party.*of.*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                party_size = int(match.group(1))
                if 1 <= party_size <= 20:
                    print(f"DEBUG: Found party size with pattern '{pattern}': {party_size}")
                    return party_size
        
        print(f"DEBUG: No party size found")
        return None
    
    def _extract_date(self, message: str) -> Optional[str]:
        date_keywords = {
            "today": "today",
            "tomorrow": "tomorrow", 
            "tonight": "today",
            "this evening": "today"
        }
        
        for keyword, date_val in date_keywords.items():
            if keyword in message:
                return date_val
        
        return None

class EnhancedBookingService:
    def __init__(self):
        self.bookings = {}
    
    def create_booking(self, booking_request: BookingRequest) -> Tuple[bool, str, Optional[str]]:
        print(f"DEBUG: Attempting to create booking with: {booking_request}")
        
        if not self._is_booking_complete(booking_request):
            missing = self._get_missing_fields(booking_request)
            print(f"DEBUG: Missing fields: {missing}")
            return False, f"I still need: {', '.join(missing)}", None
        
        restaurant = find_restaurant_by_name(booking_request.restaurant_name)
        if not restaurant:
            available_restaurants = [r.name for r in get_all_restaurants()[:5]]
            suggestion = f"Restaurant '{booking_request.restaurant_name}' not found. Available restaurants include: {', '.join(available_restaurants)}"
            return False, suggestion, None
        
        if booking_request.time not in restaurant.available_times:
            available_times = ", ".join(restaurant.available_times)
            return False, f"Sorry, {restaurant.name} doesn't have a table available at {booking_request.time}. Available times: {available_times}", None
        
        if booking_request.party_size > restaurant.capacity:
            return False, f"Sorry, {restaurant.name} can accommodate up to {restaurant.capacity} people. Your party size of {booking_request.party_size} is too large.", None
        
        booking_id = str(uuid.uuid4())[:8].upper()
        booking = Booking(
            id=booking_id,
            restaurant_name=booking_request.restaurant_name,
            date=booking_request.date,
            time=booking_request.time,
            party_size=booking_request.party_size,
            status="confirmed",
            created_at=datetime.now()
        )
        
        self.bookings[booking_id] = booking
        
        success_message = f"""🎉 Booking Confirmed! 🎉

Restaurant: {restaurant.name}
Date: {booking_request.date}
Time: {booking_request.time}
Party Size: {booking_request.party_size} people
Booking ID: {booking_id}

Location: {restaurant.location}
Your table is reserved! If you need to make changes, just let me know."""
        
        print(f"DEBUG: Booking created successfully: {booking_id}")
        return True, success_message, booking_id
    
    def _is_booking_complete(self, booking: BookingRequest) -> bool:
        required_fields = [booking.restaurant_name, booking.date, booking.time, booking.party_size]
        complete = all(field is not None for field in required_fields)
        print(f"DEBUG: Booking complete check: {complete} (restaurant: {booking.restaurant_name}, date: {booking.date}, time: {booking.time}, party_size: {booking.party_size})")
        return complete
    
    def _get_missing_fields(self, booking: BookingRequest) -> List[str]:
        missing = []
        if not booking.restaurant_name:
            missing.append("restaurant name")
        if not booking.date:
            missing.append("date")
        if not booking.time:
            missing.append("time")
        if not booking.party_size:
            missing.append("number of people")
        return missing

class ContextSwitchChatService:
    def __init__(self):
        self.session_manager = SessionManager()
        self.intent_detector = AdvancedIntentDetector()
        self.booking_service = EnhancedBookingService()
    
    def process_message(self, message: str, session_id: str) -> dict:
        print(f"\nDEBUG: Processing message: '{message}' for session: {session_id}")
        
        session = self.session_manager.get_session(session_id)
        context = session["context"]
        current_booking = session["current_booking"]
        
        self.session_manager.add_message(session_id, "user", message)
        
        intent = self.intent_detector.detect_intent_with_context(message, context, current_booking)
        
        print(f"DEBUG: Detected intent: {intent}")
        print(f"DEBUG: Current booking context: {self.session_manager.get_booking_context(session_id)}")
        
        context.last_intent = intent
        session["last_intent"] = intent
        
        if intent == "book_reservation":
            context.booking_state = BookingState.GATHERING_INFO
            return self._handle_booking_request(message, session_id)
        elif intent == "modify_booking":
            context.booking_state = BookingState.MODIFYING
            return self._handle_booking_modification(message, session_id)
        elif intent == "provide_info":
            if context.booking_state in [BookingState.GATHERING_INFO, BookingState.MODIFYING]:
                return self._handle_booking_info_provision(message, session_id)
            else:
                context.booking_state = BookingState.GATHERING_INFO
                return self._handle_booking_request(message, session_id)
        elif intent == "confirm_booking":
            return self._handle_booking_confirmation(message, session_id)
        elif intent == "get_recommendations":
            return self._handle_recommendations(message, session_id)
        else:
            return self._handle_general(message, session_id)
    
    def _handle_booking_request(self, message: str, session_id: str) -> dict:
        extracted_info = self.intent_detector.extract_comprehensive_info(message)
        self.session_manager.update_booking_info(session_id, extracted_info, is_modification=False)
        
        return self._attempt_booking_or_continue(session_id)
    
    def _handle_booking_modification(self, message: str, session_id: str) -> dict:
        print(f"DEBUG: Handling booking modification")
        
        modification_info = self.intent_detector.extract_modification_info(message)
        changes = self.session_manager.update_booking_info(session_id, modification_info, is_modification=True)
        
        if changes:
            current_context = self.session_manager.get_booking_context(session_id)
            response = f"Got it! I've updated your booking. Now I have: {current_context}"
            
            return self._attempt_booking_or_continue(session_id, custom_message=response)
        else:
            return {
                "response": "I didn't catch what you'd like to change. Could you be more specific?",
                "intent": "modify_booking",
                "data": None
            }
    
    def _handle_booking_info_provision(self, message: str, session_id: str) -> dict:
        extracted_info = self.intent_detector.extract_comprehensive_info(message)
        self.session_manager.update_booking_info(session_id, extracted_info, is_modification=False)
        
        return self._attempt_booking_or_continue(session_id)
    
    def _attempt_booking_or_continue(self, session_id: str, custom_message: str = None) -> dict:
        session = self.session_manager.get_session(session_id)
        current_booking = session["current_booking"]
        
        success, response_message, booking_id = self.booking_service.create_booking(current_booking)
        
        if success:
            session["context"].booking_state = BookingState.COMPLETED
            self.session_manager.clear_booking(session_id)
            return {
                "response": response_message,
                "intent": "book_reservation",
                "data": {"booking_id": booking_id}
            }
        else:
            missing_fields = self.session_manager.get_missing_fields(session_id)
            current_context = self.session_manager.get_booking_context(session_id)
            
            if custom_message:
                if missing_fields:
                    follow_up = self._generate_follow_up(missing_fields)
                    full_response = f"{custom_message}\n\n{follow_up}"
                else:
                    full_response = custom_message
            else:
                if current_context != "No booking details yet":
                    if missing_fields:
                        follow_up = self._generate_follow_up(missing_fields)
                        full_response = f"Great! I have: {current_context}\n\n{follow_up}"
                    else:
                        full_response = response_message
                else:
                    follow_up = self._generate_follow_up(missing_fields)
                    full_response = f"I'd be happy to help you make a reservation! {follow_up}"
            
            return {
                "response": full_response,
                "intent": "book_reservation",
                "data": None
            }
    
    def _handle_booking_confirmation(self, message: str, session_id: str) -> dict:
        return self._attempt_booking_or_continue(session_id)
    
    def _handle_recommendations(self, message: str, session_id: str) -> dict:
        response = "I can help you find great restaurants! What type of cuisine are you looking for?"
        return {
            "response": response,
            "intent": "get_recommendations",
            "data": None
        }
    
    def _handle_general(self, message: str, session_id: str) -> dict:
        response = """Hello! I'm your FoodieSpot AI assistant. I can help you with:

🍽️ **Restaurant Reservations** - Book tables at great restaurants
🔍 **Restaurant Recommendations** - Find the perfect place to dine  
📋 **Availability Checks** - See restaurant details and open times

What would you like to do?"""
        
        return {
            "response": response,
            "intent": "general_inquiry",
            "data": None
        }
    
    def _generate_follow_up(self, missing_fields: List[str]) -> str:
        if len(missing_fields) == 1:
            questions = {
                "restaurant": "Which restaurant would you like to book?",
                "date": "What date would you prefer?",
                "time": "What time works best for you?",
                "party size": "How many people will be dining?"
            }
            return questions.get(missing_fields[0], f"I need the {missing_fields[0]}.")
        elif len(missing_fields) > 1:
            return f"I still need the {', '.join(missing_fields[:-1])} and {missing_fields[-1]}."
        else:
            return ""