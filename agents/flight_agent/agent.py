# # agent.py of flight_agent
# from google.adk.agents import Agent
# from google.adk.models.lite_llm import LiteLlm
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from google.genai import types
# import json
# from google.adk.models import Gemini
# import os
# print("Initializing flight agent...",os.environ.get('GOOGLE_API_KEY'))  

# flight_agent = Agent(
#     name="flight_agent",
#   model = Gemini(model="gemini-2.5-flash"),
#      description="Finds and suggests specific flight options for the user's travel plans.",
#     instruction=(
#         "Given the full travel details (origin, destination, dates, budget), your **ONLY** task is to suggest 2-3 flight options. "
#         "For each flight, provide the Airline, Departure Time, Arrival Time, Price Estimate, and Stops. "
#         "**YOUR ENTIRE RESPONSE MUST BE A SINGLE, VALID JSON OBJECT.** "
#         "**DO NOT INCLUDE ANY INTRODUCTORY, EXPLANATORY, OR CONVERSATIONAL TEXT WHATSOEVER.** "
#         "**YOU MUST USE THE TOP-LEVEL KEY 'flights'** with a list of flight objects as its value."
#     )
# )


# session_service = InMemorySessionService()
# runner = Runner(
#     agent=flight_agent,
#     app_name="flight_app",
#     session_service=session_service
# )
# USER_ID = "user_activities"
# SESSION_ID = "session_activities"




# async def execute(request):
#     await session_service.create_session(
#         app_name="flight_app",
#         user_id=USER_ID,
#         session_id=SESSION_ID
#     )
#     prompt = (
#         f"User is flying to {request['destination']} from {request['start_date']} to {request['end_date']}, "
#         f"with a budget of {request['budget']}. Suggest 2-3 activities, each with name, description, price estimate, and duration. "
#         f"Respond in JSON format using the key 'activities' with a list of activity objects."
#     )
#     message = types.Content(role="user", parts=[types.Part(text=prompt)])
#     async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
#         if event.is_final_response():
#             response_text = event.content.parts[0].text
#             try:
#                 parsed = json.loads(response_text)
#                 if "activities" in parsed and isinstance(parsed["activities"], list):
#                     return {"activities": parsed["activities"]}
#                 else:
#                     print("'activities' key missing or not a list in response JSON")
#                     return {"activities": response_text}  # fallback to raw text
#             except json.JSONDecodeError as e:
#                 print("JSON parsing failed:", e)
#                 print("Response content:", response_text)
#                 return {"activities": response_text}  # fallback to raw text


# agent.py of flight_agent
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.models import Gemini
import json
import os
import uuid  # <-- NEW: Import for unique session IDs

print("Initializing flight agent...", os.environ.get('GOOGLE_API_KEY'))

flight_agent = Agent(
    name="flight_agent",
    model=Gemini(model="gemini-2.5-flash"),
    description="Finds and suggests specific flight options for the user's travel plans.",
    instruction=(
        "Given the full travel details (origin, destination, dates, budget), your **ONLY** task is to suggest 2-3 flight options. "
        "For each flight, provide the Airline, Departure Time, Arrival Time, Price Estimate, and Stops. "
        "**YOUR ENTIRE RESPONSE MUST BE A SINGLE, VALID JSON OBJECT.** "
        "**DO NOT INCLUDE ANY INTRODUCTORY, EXPLANATORY, OR CONVERSATIONAL TEXT WHATSOEVER.** "
        "**YOU MUST USE THE TOP-LEVEL KEY 'flights'** with a list of flight objects as its value."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=flight_agent,
    app_name="flight_app",
    session_service=session_service
)
USER_ID = "flight_service_user" # Updated user ID for clarity


async def execute(request):
    # --- FIX 1: Use UUID for unique session to prevent 'Session not found' ---
    new_session_id = str(uuid.uuid4())
    app_name = "flight_app"
    
    # Try to create session explicitly, though runner often handles it
    try:
        await session_service.create_session(
            app_name=app_name,
            user_id=USER_ID,
            session_id=new_session_id
        )
    except SessionAlreadyExistsError:
        pass # Ignore if it somehow exists

    # --- FIX 2: Correct the prompt to ask for FLIGHTS (not activities) ---
    prompt = (
        f"Provide flight options for a trip from {request.get('origin', 'UNKNOWN')} to {request.get('destination', 'UNKNOWN')}, "
        f"departing on {request.get('start_date', 'UNKNOWN')} and returning on {request.get('end_date', 'UNKNOWN')}, "
        f"with a budget of {request.get('budget', 'UNKNOWN')}. "
        f"Strictly adhere to the instruction: Respond ONLY in JSON format using the key 'flights' with a list of flight objects."
    )
    
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    response_data = None
    
    try:
        # --- Run the Agent with the unique session ID ---
        async for event in runner.run_async(user_id=USER_ID, session_id=new_session_id, new_message=message):
            if event.is_final_response():
                response_text = event.content.parts[0].text
                
                try:
                    parsed = json.loads(response_text)
                    
                    # --- FIX 3: Look for the correct key 'flights' ---
                    if "flights" in parsed and isinstance(parsed["flights"], list):
                        response_data = {"flights": parsed["flights"]}
                    else:
                        print("Agent returned valid JSON but missing 'flights' key or not a list.")
                        response_data = {"flights": response_text} # Fallback
                
                except json.JSONDecodeError as e:
                    # Catch the conversational output error
                    print("JSON parsing failed (Agent outputted conversational text):", e)
                    print("Response content:", response_text)
                    response_data = {"flights": response_text} # Fallback to raw text for debugging
                
                break # Exit the loop after final response

    finally:
        # Clean up the session (optional but recommended for stateless runs)
        # try:
        #     await session_service.delete_session(app_name=app_name, user_id=USER_ID, session_id=new_session_id)
        # except Exception:
        #     pass

        # Return the collected data
        return response_data if response_data is not None else {"flights": "Agent failed to respond."}