from google.adk.agents import Agent
from google.adk.models.lite_llm import (
    LiteLlm,
)  # This import is likely unused but kept for parity
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json
from google.adk.models import Gemini
import os

print("Initializing stay agent...", os.environ.get("GOOGLE_API_KEY"))

# 1. Define the Stay Agent
stay_agent = Agent(
    name="stay_agent",
    # Keeping the same working model as the flight agent
    model=Gemini(model="gemini-2.5-flash"),
    # Updated description
    description="Suggests 2-3 suitable accommodation options (hotels, rentals) for the user.",
    # Updated instruction for stay recommendations
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 specific and highly-rated accommodation options. "
        "For each option, provide a name, a short description, estimated nightly price range, and a suggested star rating or type (e.g., luxury, budget, apartment). "
        "Respond in plain English. Keep it concise and well-formatted."
    ),
)

# 2. Update Session and Runner Configuration
session_service = InMemorySessionService()
# Updated app_name and agent
runner = Runner(
    agent=stay_agent, app_name="accommodations_app", session_service=session_service
)
# Updated user and session IDs
USER_ID = "user_stays"
SESSION_ID = "session_stays"
# Using a key like 'stays' for the final JSON output
JSON_OUTPUT_KEY = "stays"


# 3. Update the execute function
async def execute(request):
    await session_service.create_session(
        app_name="accommodations_app", user_id=USER_ID, session_id=SESSION_ID
    )
    # Updated prompt for accommodation search
    prompt = (
        f"User needs accommodation in {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}. Suggest 2-3 accommodations, each with name, description, nightly price range, and type/rating. "
        f"Respond ONLY in JSON format using the key '{JSON_OUTPUT_KEY}' with a list of stay objects."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                # Updated parsing logic to use the new key 'stays'
                parsed = json.loads(response_text)
                if JSON_OUTPUT_KEY in parsed and isinstance(
                    parsed[JSON_OUTPUT_KEY], list
                ):
                    return {JSON_OUTPUT_KEY: parsed[JSON_OUTPUT_KEY]}
                else:
                    print(
                        f"'{JSON_OUTPUT_KEY}' key missing or not a list in response JSON"
                    )
                    return {JSON_OUTPUT_KEY: response_text}  # fallback to raw text
            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {JSON_OUTPUT_KEY: response_text}  # fallback to raw text
