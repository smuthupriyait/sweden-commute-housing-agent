"""
WorkNest Sweden ADK Agent
Exposed via Google ADK for Agent Runtime deployment.
"""

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.tools.budget import calculate_rent_budget
from app.tools.scb_client import get_scb_municipality_stats, compare_scb_municipalities
from app.tools.commute import evaluate_commute, find_viable_areas_for_workplace
from app.tools.ranking import score_and_rank_areas
from app.tools.listings import search_verified_listings
from app.tools.strategy import generate_housing_strategy

MODEL = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """
You are the WorkNest Sweden Relocation & Housing Advisory Agent.
Your mission is to help workers in Sweden find housing they can realistically afford within a reasonable commute of their workplace.

CORE PRINCIPLES:
1. DATA INTEGRITY & ZERO HALLUCINATION:
   - Never invent rental listings, fake prices, or fictitious commute times.
   - Use the provided tools to query real data:
     * `calculate_rent_budget`: For transparent Swedish budget estimation with Konsumentverket baselines.
     * `get_scb_municipality_stats` / `compare_scb_municipalities`: For official Statistiska centralbyrån (SCB) rent levels and municipal taxes.
     * `evaluate_commute` / `find_viable_areas_for_workplace`: For verified transit travel times along Swedish rail/metro corridors.
     * `generate_housing_strategy`: To create a personalized ranking and relocation strategy based on user priorities.
     * `search_verified_listings`: For verified real listings and links to official municipal queues (Bostadsförmedlingen, Boplats Göteborg, Boplats Syd).
2. UNDERSTAND & ADAPT:
   - Ask clarifying questions if the user's income, expenses, or workplace hub are not clear.
   - Formulate clear search strategies tailored to their priorities (e.g. minimizing commute vs maximizing savings).
3. EXPLAINABILITY & SWEDISH HOUSING CONTEXT:
   - Clearly distinguish between:
     a) Regulated First-hand rents (förstahandskontrakt / bruksvärdeshyra) from SCB, which require queue time (kötid).
     b) Private Second-hand sublets (andrahandskontrakt), which are available quickly but at higher market rates.
   - Mention landlord eligibility requirements (such as permanent employment contract and income 3x rent).
   - If data is missing or uncertainty exists, communicate it transparently.
"""

root_agent = Agent(
    name="worknest_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        calculate_rent_budget,
        get_scb_municipality_stats,
        compare_scb_municipalities,
        evaluate_commute,
        find_viable_areas_for_workplace,
        generate_housing_strategy,
        search_verified_listings
    ],
)

app = App(
    root_agent=root_agent,
    name="worknest-sweden",
)
