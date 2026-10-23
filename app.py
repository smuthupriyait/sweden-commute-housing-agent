"""
WorkNest Sweden - FastAPI Application
Provides REST endpoints for calculation, multi-criteria ranking, and conversational AI agent.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from tools.budget import calculate_rent_budget
from tools.scb_client import get_scb_municipality_stats, compare_scb_municipalities, MUNICIPALITY_CODES
from tools.commute import evaluate_commute, find_viable_areas_for_workplace, WORKPLACE_HUBS, RESIDENTIAL_AREAS
from tools.ranking import score_and_rank_areas
from tools.strategy import generate_housing_strategy
from tools.listings import search_verified_listings
from agent import WorkNestAgent

app = FastAPI(
    title="WorkNest Sweden",
    description="Agent-first housing & commute advisory platform for workers in Sweden"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory agent sessions
sessions: Dict[str, WorkNestAgent] = {}

class BudgetRequest(BaseModel):
    net_income_sek: float = Field(..., description="Monthly take-home income in SEK")
    fixed_expenses_sek: float = Field(..., description="Monthly essential fixed expenses in SEK")
    buffer_percentage: float = Field(15.0, description="Emergency buffer %")
    household_adults: int = Field(1, description="Adults in household")
    household_children: int = Field(0, description="Children in household")

class CommuteRequest(BaseModel):
    origin_area: str
    workplace: str
    max_commute_minutes: int = 45

class AreaComparisonRequest(BaseModel):
    workplace: str
    max_commute_minutes: int = 45
    net_income_sek: Optional[float] = 38000
    fixed_expenses_sek: Optional[float] = 12000
    weight_commute: Optional[float] = 0.40
    weight_rent: Optional[float] = 0.35
    weight_tax: Optional[float] = 0.25

class StrategyRequest(BaseModel):
    net_income_sek: float
    fixed_expenses_sek: float
    workplace: str
    max_commute_minutes: int = 45
    household_adults: int = 1
    household_children: int = 0
    buffer_percentage: float = 15.0
    prioritize: str = "balanced"

class ChatRequest(BaseModel):
    session_id: str = "default_session"
    message: str

@app.get("/api/config")
def get_config():
    """Returns available workplaces and municipal regions."""
    return {
        "workplaces": list(WORKPLACE_HUBS.keys()),
        "residential_areas": list(RESIDENTIAL_AREAS.keys()),
        "municipalities": list(MUNICIPALITY_CODES.keys())
    }

@app.post("/api/budget/calculate")
def calculate_budget_endpoint(req: BudgetRequest):
    return calculate_rent_budget(
        net_income_sek=req.net_income_sek,
        fixed_expenses_sek=req.fixed_expenses_sek,
        buffer_percentage=req.buffer_percentage,
        household_adults=req.household_adults,
        household_children=req.household_children
    )

@app.post("/api/commute/evaluate")
def evaluate_commute_endpoint(req: CommuteRequest):
    return evaluate_commute(
        origin_area=req.origin_area,
        workplace=req.workplace,
        max_commute_minutes=req.max_commute_minutes
    )

@app.post("/api/areas/compare")
def compare_areas_endpoint(req: AreaComparisonRequest):
    """
    Finds viable areas for the workplace, joins them with authentic SCB data,
    and ranks them using multi-criteria configurable scoring.
    """
    viable_areas = find_viable_areas_for_workplace(
        workplace=req.workplace,
        max_commute_minutes=req.max_commute_minutes
    )
    
    budget_info = calculate_rent_budget(
        net_income_sek=req.net_income_sek or 38000,
        fixed_expenses_sek=req.fixed_expenses_sek or 12000
    )

    enriched = []
    for area in viable_areas:
        muni = area["municipality"]
        scb_data = get_scb_municipality_stats(muni)
        
        affordable_note = "Affordability depends on budget"
        if budget_info and "error" not in budget_info:
            max_rent = budget_info["max_rent_sek"]
            norm_studio = scb_data.get("scb_norm_rents", {}).get("studio_35sqm_sek", 0)
            norm_1bed = scb_data.get("scb_norm_rents", {}).get("1bed_55sqm_sek", 0)
            if max_rent >= norm_1bed:
                affordable_note = "Comfortably covers SCB average 1-2 room apartment"
            elif max_rent >= norm_studio:
                affordable_note = "Covers SCB average studio/small apartment"
            else:
                affordable_note = "Tight against SCB baseline; consider house-sharing"

        enriched.append({
            **area,
            "scb_stats": scb_data,
            "affordability_assessment": affordable_note
        })

    # Apply ranking
    ranked = score_and_rank_areas(
        viable_areas=enriched,
        user_budget_max_sek=budget_info.get("max_rent_sek", 15000),
        weight_commute=req.weight_commute or 0.40,
        weight_rent=req.weight_rent or 0.35,
        weight_tax=req.weight_tax or 0.25
    )

    return {
        "workplace": req.workplace,
        "max_commute_minutes": req.max_commute_minutes,
        "viable_areas_count": len(ranked),
        "areas": ranked
    }

@app.post("/api/strategy/generate")
def generate_strategy_endpoint(req: StrategyRequest):
    return generate_housing_strategy(
        net_income_sek=req.net_income_sek,
        fixed_expenses_sek=req.fixed_expenses_sek,
        workplace=req.workplace,
        max_commute_minutes=req.max_commute_minutes,
        household_adults=req.household_adults,
        household_children=req.household_children,
        buffer_percentage=req.buffer_percentage,
        prioritize=req.prioritize
    )

@app.get("/api/listings/search")
def search_listings_endpoint(municipality: Optional[str] = None, max_rent: Optional[float] = None, min_rooms: Optional[float] = None):
    return search_verified_listings(municipality=municipality, max_rent_sek=max_rent, min_rooms=min_rooms)

@app.post("/api/chat")
def chat_with_agent(req: ChatRequest):
    """Conversational endpoint with the autonomous WorkNest agent."""
    if req.session_id not in sessions:
        try:
            sessions[req.session_id] = WorkNestAgent()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize agent: {str(e)}")

    agent = sessions[req.session_id]
    try:
        reply = agent.send_message(req.message)
        return {"session_id": req.session_id, "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

# Mount static files
app.mount("/", StaticFiles(directory="/config/Desktop/BuildWithGemini/static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
