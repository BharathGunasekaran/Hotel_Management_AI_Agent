from fastapi import FastAPI # type: ignore
from pydantic import BaseModel # type: ignore
from fastapi import Query # type: ignore
from fastapi.middleware.cors import CORSMiddleware # Import the middleware
# Import all necessary functions from your tool file
from app.agent_tools import get_weather, check_availability, create_booking, create_room
# Import models (if needed, though requests are defined locally)

app = FastAPI(title="Hotel Management AI Agent")

# --- CORS Configuration (The fix for 405 Method Not Allowed) ---
# The browser sends an OPTIONS request (the preflight check) before sending a POST.
# Setting allow_origins=["*"] and allow_methods=["*"] ensures FastAPI's middleware 
# handles this OPTIONS request correctly, eliminating the 405 error from the local HTML file.
origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_methods=["*"], # Allows ALL methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"], # Allows all headers (Content-Type, Authorization, etc.)
    allow_credentials=True,
)


# ===================================================
# REQUEST MODELS
# ===================================================

class AvailabilityRequest(BaseModel):
    room_type: str
    start_date: str
    end_date: str

class BookingRequest(BaseModel):
    guest_name: str
    room_type: str
    start_date: str
    end_date: str
    contact: str = None

class WeatherRequest(BaseModel):
    city: str

class RoomCreationRequest(BaseModel):
    room_type: str
    total_rooms: int
    price_per_night: float


# ===================================================
# ENDPOINTS
# ===================================================

@app.get("/")
def home():
    return {"message":"Hotel Management AI Agent is running. Access /docs for API documentation."}

# --- Room Management ---
@app.post("/rooms")
def api_create_room(req: RoomCreationRequest):
    """Creates a new room type in the database."""
    success, result = create_room(req.room_type, req.total_rooms, req.price_per_night)
    return {"success": success, "room_type": result}

# --- Availability Check ---
@app.post("/availability")
def api_check_availability_post(req: AvailabilityRequest):
    """Checks room availability based on a JSON body (used by index.html)."""
    available, price, msg = check_availability(req.room_type, req.start_date, req.end_date)
    return {"available_rooms": available, "estimated_price": price, "status_message": msg}


@app.get("/availability")
def api_check_availability_get(
    room_type: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
):
    """Checks room availability using URL query parameters (used by agents)."""
    available, price, msg = check_availability(room_type, start_date, end_date)
    return {"available_rooms": available, "estimated_price": price, "status_message": msg}

# --- Booking ---
@app.post("/booking")
def api_create_booking(req: BookingRequest):
    """Creates a new booking."""
    success, result = create_booking(req.guest_name, req.room_type, req.start_date, req.end_date, req.contact)
    return {"success": success, "result": result}

# --- Weather ---
@app.post("/weather")
def api_weather(req: WeatherRequest):
    """Gets weather information for a given city."""
    return {"result": get_weather(req.city)}
