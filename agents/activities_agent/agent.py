# from google.adk.agents import Agent
# from google.adk.models.lite_llm import LiteLlm
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from google.genai import types
# import json
# from google.adk.models import Gemini

# activities_agent = Agent(
#     name="activities_agent",
#    model = Gemini(model="gemini-2.5-flash"),
#     description="Suggests interesting activities for the user at a destination.",
#     instruction=(
#         "Given a destination, dates, and budget, suggest 2-3 engaging tourist or cultural activities. "
#         "For each activity, provide a name, a short description, price estimate, and duration in hours. "
#         "Respond in plain English. Keep it concise and well-formatted."
#     )
# )


# session_service = InMemorySessionService()
# runner = Runner(
#     agent=activities_agent,
#     app_name="activities_app",
#     session_service=session_service
# )
# USER_ID = "user_activities"
# SESSION_ID = "session_activities"


# async def execute(request):
#     await session_service.create_session(
#         app_name="activities_app",
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


from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.models import Gemini
import json
import uuid

# Agent and Runner Definitions remain at the module level
activities_agent = Agent(
    name="activities_agent",
    model=Gemini(model="gemini-2.5-flash"),
    description="Suggests interesting activities for the user at a destination.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 engaging tourist or cultural activities. "
        "For each activity, provide a name, a short description, price estimate, and duration in hours. "
        "Respond in plain English. Keep it concise and well-formatted."
    ),
)

session_service = InMemorySessionService()
runner = Runner(
    agent=activities_agent, app_name="activities_app", session_service=session_service
)
# USER_ID can be staticw
USER_ID = "travel_planner_user"

# Assuming the global variables (agent, runner, service) are defined above...
USER_ID = "travel_planner_user"


async def execute(request):

    # 1. Generate unique session ID for this request
    current_session_id = str(uuid.uuid4())
    app_name = "activities_app"

    # 2. Explicitly create the session
    try:
        await session_service.create_session(
            app_name=app_name, user_id=USER_ID, session_id=current_session_id
        )
    except SessionAlreadyExistsError:
        # This shouldn't happen with a UUID, but keep it for robustness
        pass

    response_data = None

    try:
        prompt = (
            f"User is flying to {request['destination']} from {request['start_date']} to {request['end_date']}, "
            f"with a budget of {request['budget']}. Suggest 2-3 activities, each with name, description, price estimate, and duration. "
            f"Respond in JSON format using the key 'activities' with a list of activity objects."
        )
        message = types.Content(role="user", parts=[types.Part(text=prompt)])

        # 3. Run the Agent
        # The runner.run_async call MUST NOT be commented out.
        async for event in runner.run_async(
            user_id=USER_ID, session_id=current_session_id, new_message=message
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text

                # 4. JSON Parsing and return
                try:
                    parsed = json.loads(response_text)
                    if "activities" in parsed and isinstance(
                        parsed["activities"], list
                    ):
                        response_data = {"activities": parsed["activities"]}
                    else:
                        print("'activities' key missing or not a list in response JSON")
                        response_data = {
                            "activities": response_text
                        }  # fallback to raw text
                except json.JSONDecodeError as e:
                    print("JSON parsing failed:", e)
                    print("Response content:", response_text)
                    response_data = {
                        "activities": response_text
                    }  # fallback to raw text

                # We break the loop after receiving the final response
                break

    finally:
        # 5. Explicitly delete the session for cleanup 🧹
        try:
            await session_service.delete_session(
                app_name=app_name, user_id=USER_ID, session_id=current_session_id
            )
        except SessionNotFoundError:
            # Session might have been cleared by runner if run failed early, safe to ignore
            pass

    # Ensure a response is always returned after cleanup
    if response_data is not None:
        return response_data

    # Fallback return if the run_async loop finished without a final response
    return {"error": "Agent did not return a final response."}
