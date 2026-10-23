"""
A2UI Surface Builder for Sweden Housing & Commute Navigator.
Builds v0.8 A2UI Component trees that render natively as cards and tables.
"""

from typing import List, Dict, Any

def build_area_cards_a2ui(ranked_areas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Builds A2UI v0.8 card representations for ranked Swedish areas."""
    components = []
    
    for area in ranked_areas[:4]:
        name = area.get("area_name", "Area")
        muni = area.get("municipality", "")
        time_m = area.get("commute_minutes", 0)
        mode = area.get("transit_mode", "Transit")
        rank_score = area.get("rank_score", 0)
        scb = area.get("scb_stats", {})
        norm_rents = scb.get("scb_norm_rents", {})
        rent_1bed = norm_rents.get("1bed_55sqm_sek", "N/A")
        tax = scb.get("tax_rate_percent", "N/A")
        
        card = {
            "type": "Card",
            "id": f"card_{name.lower().replace(' ', '_')}",
            "title": f"#{area.get('rank', 1)} {name} ({muni})",
            "score": rank_score,
            "badge": f"{time_m} min via {mode}",
            "metrics": [
                {"label": "SCB Avg 1-2 Room Rent", "val": f"{rent_1bed:,} SEK/mo" if isinstance(rent_1bed, (int, float)) else str(rent_1bed)},
                {"label": "Municipal Tax Rate", "val": f"{tax}%"},
                {"label": "Commute to Workplace", "val": f"{time_m} mins ({mode})"},
                {"label": "Corridor Highlights", "val": area.get("corridor_notes", "Fast commuter connection")}
            ],
            "tags": [muni, mode, f"Score: {rank_score}/100"]
        }
        components.append(card)
        
    return components

def build_budget_a2ui(budget_info: Dict[str, Any]) -> Dict[str, Any]:
    """Builds A2UI card representation for Swedish rent affordability."""
    return {
        "type": "BudgetCard",
        "prudent_rent": budget_info.get("prudent_rent_sek", 0),
        "max_rent": budget_info.get("max_rent_sek", 0),
        "buffer_sek": budget_info.get("emergency_buffer_sek", 0),
        "residual_sek": budget_info.get("residual_disposable_income_sek", 0),
        "baseline_sek": budget_info.get("konsumentverket_baseline_sek", 0),
        "affordability_tier": budget_info.get("affordability_tier", "Prudent"),
        "verdict": budget_info.get("calculation_explanation", "")
    }
