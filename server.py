"""
Sweden Commute & Affordable Housing Navigator - FastAPI Application
Provides REST endpoints for calculation, multi-criteria ranking, Long-term Memory Bank,
A2UI Card surfaces, Apartment Discovery, Neighborhood Intelligence, and conversational AI agent.
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
from tools.listings import search_apartment_listings
from tools.neighborhoods import get_neighborhood_intelligence, get_solna_comparison, ALL_NEIGHBORHOODS, SOLNA_NEIGHBORHOODS
from tools.memory_service import memory_bank
from tools.a2ui_builder import build_area_cards_a2ui, build_budget_a2ui, build_apartment_cards_a2ui, build_neighborhood_cards_a2ui
from agent import WorkNestAgent

app = FastAPI(
    title="Sweden Commute & Affordable Housing Finder",
    description="Agent-first housing & commute discovery platform with Memory Bank, A2UI cards, and verified listings"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class ApartmentSearchRequest(BaseModel):
    municipality: Optional[str] = None
    neighborhood: Optional[str] = None
    max_rent_sek: Optional[float] = None
    min_rooms: Optional[float] = None
    max_rooms: Optional[float] = None
    min_sqm: Optional[float] = None
    housing_type: Optional[str] = None
    workplace: Optional[str] = "Stockholm Central / City"
    max_commute_minutes: Optional[int] = 45
    user_net_income: Optional[float] = 38000
    user_prudent_rent_sek: Optional[float] = 12540

class StrategyRequest(BaseModel):
    net_income_sek: float
    fixed_expenses_sek: float
    workplace: str
    max_commute_minutes: int = 45
    household_adults: int = 1
    household_children: int = 0
    buffer_percentage: float = 15.0
    prioritize: str = "balanced"

class MemoryUpdateRequest(BaseModel):
    user_id: str = "default_user"
    key: str
    value: Any

class ProfileUpdateRequest(BaseModel):
    user_id: str = "default_user"
    profile: Dict[str, Any]

class ChatRequest(BaseModel):
    session_id: str = "default_session"
    user_id: str = "default_user"
    message: str

@app.get("/api/config")
def get_config():
    return {
        "workplace_hubs": list(WORKPLACE_HUBS.keys()),
        "residential_areas": list(RESIDENTIAL_AREAS.keys()),
        "supported_municipalities": list(MUNICIPALITY_CODES.keys()),
        "solna_neighborhoods": list(SOLNA_NEIGHBORHOODS.keys()),
        "all_neighborhoods": list(ALL_NEIGHBORHOODS.keys())
    }

@app.get("/api/memory/{user_id}")
def get_user_memory(user_id: str):
    return memory_bank.get_memories(user_id)

@app.post("/api/memory")
def save_user_memory(req: MemoryUpdateRequest):
    memory_bank.save_memory(req.user_id, req.key, req.value)
    return {"status": "saved", "memories": memory_bank.get_memories(req.user_id)}

@app.put("/api/memory")
def update_user_memory_profile(req: ProfileUpdateRequest):
    memory_bank.update_all_memories(req.user_id, req.profile)
    return {"status": "updated", "memories": memory_bank.get_memories(req.user_id)}

@app.delete("/api/memory/{user_id}")
def clear_user_memory(user_id: str):
    memory_bank.clear_memories(user_id)
    return {"status": "cleared", "memories": memory_bank.get_memories(user_id)}

@app.post("/api/budget/calculate")
def calculate_budget_endpoint(req: BudgetRequest):
    budget_data = calculate_rent_budget(
        net_income_sek=req.net_income_sek,
        fixed_expenses_sek=req.fixed_expenses_sek,
        buffer_percentage=req.buffer_percentage,
        household_adults=req.household_adults,
        household_children=req.household_children
    )
    budget_a2ui = build_budget_a2ui(budget_data)
    return {**budget_data, "a2ui_card": budget_a2ui}

@app.post("/api/commute/evaluate")
def evaluate_commute_endpoint(req: CommuteRequest):
    return evaluate_commute(
        origin_area=req.origin_area,
        workplace=req.workplace,
        max_commute_minutes=req.max_commute_minutes
    )

@app.get("/api/scb/stats/{municipality}")
def get_scb_stats_endpoint(municipality: str, year: str = "2026"):
    return get_scb_municipality_stats(municipality, year)

@app.post("/api/areas/compare")
def compare_areas_endpoint(req: AreaComparisonRequest):
    viable = find_viable_areas_for_workplace(
        workplace=req.workplace,
        max_commute_minutes=req.max_commute_minutes
    )
    
    for area in viable:
        muni = area.get("municipality", "")
        scb_data = get_scb_municipality_stats(muni)
        area["scb_stats"] = {
            "annual_rent_per_sqm_sek": scb_data.get("annual_rent_per_sqm_sek"),
            "monthly_rent_per_sqm_sek": scb_data.get("monthly_rent_per_sqm_sek"),
            "scb_norm_rents": scb_data.get("scb_norm_rents", {}),
            "municipal_tax_rate_percent": scb_data.get("municipal_tax_rate_percent"),
            "tax_rate_percent": scb_data.get("municipal_tax_rate_percent")
        }

    budget_info = calculate_rent_budget(
        net_income_sek=req.net_income_sek or 38000,
        fixed_expenses_sek=req.fixed_expenses_sek or 11000
    )
    prudent_budget = budget_info.get("recommended_rent_prudent_sek", 12500)

    ranked = score_and_rank_areas(
        viable_areas=viable,
        user_budget_max_sek=prudent_budget,
        weight_commute=req.weight_commute or 0.40,
        weight_rent=req.weight_rent or 0.35,
        weight_tax=req.weight_tax or 0.25
    )

    standardized = []
    for item in ranked:
        item["area_name"] = item.get("origin_area", item.get("area_name", "Area"))
        item["rank_score"] = item.get("overall_score", 0)
        item["commute_minutes"] = item.get("estimated_transit_minutes", 0)
        item["transit_mode"] = item.get("transit_line_type", "Public Transit")
        if "scb_stats" in item and "municipal_tax_rate_percent" in item["scb_stats"]:
            item["scb_stats"]["tax_rate_percent"] = item["scb_stats"]["municipal_tax_rate_percent"]
        standardized.append(item)

    a2ui_cards = build_area_cards_a2ui(standardized)

    return {
        "workplace": req.workplace,
        "max_commute_minutes": req.max_commute_minutes,
        "viable_areas_count": len(standardized),
        "areas": standardized,
        "a2ui_cards": a2ui_cards
    }

# 1. APARTMENT DISCOVERY ENDPOINT
@app.post("/api/apartments/search")
def search_apartments_endpoint(req: ApartmentSearchRequest):
    search_res = search_apartment_listings(
        municipality=req.municipality,
        neighborhood=req.neighborhood,
        max_rent_sek=req.max_rent_sek,
        min_rooms=req.min_rooms,
        max_rooms=req.max_rooms,
        min_sqm=req.min_sqm,
        housing_type=req.housing_type,
        workplace=req.workplace or "Stockholm Central / City",
        max_commute_minutes=req.max_commute_minutes,
        user_net_income=req.user_net_income,
        user_prudent_rent_sek=req.user_prudent_rent_sek
    )
    a2ui_apartments = build_apartment_cards_a2ui(search_res["listings"])
    return {
        **search_res,
        "a2ui_apartment_cards": a2ui_apartments
    }

# 3. NEIGHBORHOOD DISCOVERY ENDPOINT
@app.get("/api/neighborhoods")
def get_neighborhoods_endpoint(municipality: Optional[str] = None, workplace: str = "Stockholm Central / City"):
    nb_list = get_neighborhood_intelligence(municipality=municipality, workplace=workplace)
    a2ui_nb_cards = build_neighborhood_cards_a2ui(nb_list)
    return {
        "municipality_filter": municipality,
        "workplace": workplace,
        "neighborhoods_count": len(nb_list),
        "neighborhoods": nb_list,
        "a2ui_neighborhood_cards": a2ui_nb_cards
    }

@app.get("/api/neighborhoods/solna")
def get_solna_neighborhoods_endpoint(workplace: str = "Stockholm Central / City"):
    solna_list = get_solna_comparison(workplace=workplace)
    a2ui_solna_cards = build_neighborhood_cards_a2ui(solna_list)
    return {
        "municipality": "Solna",
        "workplace": workplace,
        "neighborhoods_count": len(solna_list),
        "neighborhoods": solna_list,
        "a2ui_neighborhood_cards": a2ui_solna_cards
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

@app.post("/api/chat")
def chat_with_agent(req: ChatRequest):
    memories = memory_bank.get_memories(req.user_id)
    memory_context = f"[Context: User long-term preferences: {memories}]"
    
    if req.session_id not in sessions:
        try:
            sessions[req.session_id] = WorkNestAgent()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize agent: {str(e)}")

    agent = sessions[req.session_id]
    try:
        combined_prompt = f"{memory_context}\nUser says: {req.message}"
        reply = agent.send_message(combined_prompt)
        
        # Check if user stated preference to persist to memory
        msg_lower = req.message.lower()
        if "prefer" in msg_lower or "budget is" in msg_lower or "work at" in msg_lower or "rooms" in msg_lower:
            notes = memories.get("notes", [])
            notes.append(req.message)
            memory_bank.save_memory(req.user_id, "notes", notes[-5:])
            
        return {
            "session_id": req.session_id,
            "user_id": req.user_id,
            "reply": reply,
            "recalled_memories": memories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

# Mount static files
app.mount("/", StaticFiles(directory="/config/Desktop/BuildWithGemini/static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
