# ✈️ ADK-Powered Travel Planner (Travel_Planner)

The **ADK-Powered Travel Planner** is a multi-agent system designed to help you plan your dream vacation.  
Built with **Python**, **FastAPI**, and **Streamlit**, it leverages multiple agents that collaborate to generate a complete travel itinerary including flights, stays, and activities.  

---

## 📑 Table of Contents
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Available Agents](#available-agents)
- [Running the Project](#running-the-project)
- [Demo](#demo)
- [Contributing](#contributing)
- [License](#license)

---

## 🚀 Getting Started

### ✅ Prerequisites
Make sure you have the following installed:
- Python **3.8+**
- `pip` (Python package manager)
- `virtualenv` (recommended)

### 🔧 Setup
Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/Travel_Planner.git
cd Travel_Planner
```

### ��� Install Dependencies
Run the following command to install the required dependencies:
Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

Install dependencies:
```bash
pip install -r requirements.txt
```


📂 Project Structure
ADK_demo/
├── agents/
│   ├── host_agent/
│   │   ├── agent.py              # Core logic for host/orchestrator
│   │   ├── task_manager.py       # Manages tasks and delegation
│   │   ├── __main__.py           # Entry point for FastAPI service
│   │   └── .well-known/agent.json # Agent metadata
│   │
│   ├── flight_agent/
│   │   ├── agent.py              # Handles flight planning logic
│   │   ├── task_manager.py
│   │   ├── __main__.py
│   │   └── .well-known/agent.json
│   │
│   ├── stay_agent/
│   │   ├── agent.py              # Suggests hotels/stays
│   │   ├── task_manager.py
│   │   ├── __main__.py
│   │   └── .well-known/agent.json
│   │
│   └── activities_agent/
│       ├── agent.py              # Suggests activities & experiences
│       ├── task_manager.py
│       ├── __main__.py
│       └── .well-known/agent.json
│
├── common/
│   ├── a2a_client.py             # Utility to send requests to other agents
│   └── a2a_server.py             # Shared FastAPI A2A server template
│
├── shared/
│   └── schemas.py                # Shared Pydantic schema for consistency
│
├── streamlit_app.py              # Streamlit frontend for UI & response rendering
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation


🤖 Available Agents

* Host Agent → Orchestrates requests across other agents.

* Flight Agent → Finds and suggests flights.

* Stay Agent → Provides accommodation options.

* Activities Agent → Recommends activities, tours, and local experiences.

All agents follow an A2A (Agent-to-Agent) communication pattern, making the system modular and easily extendable.

▶️ Running the Project

Run each agent in a separate terminal:

```bash
uvicorn agents.host_agent.__main__:app --port 8000
uvicorn agents.flight_agent.__main__:app --port 8001
uvicorn agents.stay_agent.__main__:app --port 8002
uvicorn agents.activities_agent.__main__:app --port 8003
```
Finally, launch the Streamlit UI:

```bash
streamlit run streamlit_app.py

```
🎨 Demo

Enter your origin, destination, travel dates, and budget in the Streamlit app.

Click Plan My Trip ✨.

The system generates a beautiful HTML travel plan including:

🛫 Flights

🏨 Stays

🗺️ Activities

🤝 Contributing

We welcome contributions! To get started:

Fork this repository

Create a feature branch (git checkout -b feature-new-agent)

Commit your changes

Push to your branch

Submit a Pull Request 🚀