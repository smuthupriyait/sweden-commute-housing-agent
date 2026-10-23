"""
WorkNest Sweden AI Agent Core
Employs Google GenAI (Vertex AI gemini-2.5-flash) with tool calling to:
1. Understand the user's housing and financial situation.
2. Formulate a personalized relocation and housing search strategy.
3. Query authentic SCB data for rent baselines and municipal taxes.
4. Calculate transit corridors and commute viability.
5. Provide verified listings and links without fabrication.
6. Clearly communicate uncertainties, rent control context, and landlord eligibility rules.
"""

import os
from typing import List, Dict, Any
from google import genai
from google.genai import types

from tools.budget import calculate_rent_budget
from tools.scb_client import get_scb_municipality_stats, compare_scb_municipalities
from tools.commute import evaluate_commute, find_viable_areas_for_workplace
from tools.ranking import score_and_rank_areas
from tools.listings import search_verified_listings
from tools.strategy import generate_housing_strategy

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-04-ad104c792922")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

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

def get_agent_client() -> genai.Client:
    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION
    )

class WorkNestAgent:
    def __init__(self):
        self.client = get_agent_client()
        self.tools = [
            calculate_rent_budget,
            get_scb_municipality_stats,
            compare_scb_municipalities,
            evaluate_commute,
            find_viable_areas_for_workplace,
            generate_housing_strategy,
            search_verified_listings
        ]
        self.config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2,
            tools=self.tools
        )
        self.chat = self.client.chats.create(
            model="gemini-2.5-flash",
            config=self.config
        )

    def send_message(self, user_message: str) -> str:
        response = self.chat.send_message(user_message)
        return response.text
