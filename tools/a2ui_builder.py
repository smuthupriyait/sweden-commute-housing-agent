"""
A2UI Surface Builder for Sweden Housing & Commute Navigator.
Builds v0.8 A2UI Component trees that render natively as cards and interactive surfaces.
Supports Area Cards, Budget Cards, Apartment Listing Cards, and Neighborhood Comparison Cards.
"""

from typing import List, Dict, Any

def build_area_cards_a2ui(ranked_areas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Builds A2UI v0.8 card representations for ranked Swedish municipalities/areas."""
    components = []
    
    for area in ranked_areas[:6]:
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
            "type": "AreaCard",
            "id": f"card_{name.lower().replace(' ', '_').replace('(', '').replace(')', '')}",
            "title": f"#{area.get('rank', 1)} {name} ({muni})",
            "score": rank_score,
            "badge": f"{time_m} min via {mode}",
            "metrics": [
                {"label": "SCB Avg 1-2 Room Rent", "val": f"{rent_1bed:,} SEK/mo" if isinstance(rent_1bed, (int, float)) else str(rent_1bed)},
                {"label": "Municipal Tax Rate", "val": f"{tax}%"},
                {"label": "Commute to Workplace", "val": f"{time_m} mins ({mode})"},
                {"label": "Corridor Highlights", "val": area.get("corridor_notes", "Fast commuter connection")}
            ],
            "tags": [muni, mode, f"Score: {rank_score}/100"],
            "action": {
                "type": "explore_neighborhoods",
                "municipality": muni,
                "label": f"Explore {muni} Neighborhoods →"
            }
        }
        components.append(card)
        
    return components

def build_apartment_cards_a2ui(listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Builds A2UI v0.8 card representations for verified apartment listings."""
    components = []
    
    for apt in listings:
        card = {
            "type": "ApartmentCard",
            "id": apt["id"],
            "title": apt["title"],
            "match_score": apt.get("match_score", 85.0),
            "rent_sek": apt["rent_sek"],
            "rooms": apt["rooms"],
            "size_sqm": apt["size_sqm"],
            "housing_type": apt["housing_type"],
            "municipality": apt["municipality"],
            "neighborhood": apt["neighborhood"],
            "address": apt["address"],
            "nearest_transit_stop": apt["nearest_transit_stop"],
            "commute_minutes": apt.get("calculated_commute_minutes", 15),
            "workplace": apt.get("workplace_destination", "Workplace"),
            "deposit": f"{apt['deposit_sek']:,} SEK ({apt['deposit_terms']})",
            "utilities_included": apt["utilities_included"],
            "utilities_excluded": apt.get("utilities_excluded", []),
            "available_from": apt["available_from"],
            "lease_duration": apt["lease_duration"],
            "source": apt.get("source", "Market Reference"),
            "source_url": apt.get("source_url", "#"),
            "sample_data_note": apt.get("sample_data_note", "Illustrative sample property"),
            "match_explanation": apt.get("match_explanation", ""),
            "budget_delta_sek": apt.get("budget_delta_sek", 0),
            "features": apt.get("features", [])
        }
        components.append(card)

    return components

def build_neighborhood_cards_a2ui(neighborhoods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Builds A2UI v0.8 card representations for neighborhood comparisons."""
    components = []

    for nb in neighborhoods:
        card = {
            "type": "NeighborhoodCard",
            "id": f"nb_{nb['neighborhood'].lower().replace(' ', '_')}",
            "neighborhood": nb["neighborhood"],
            "municipality": nb["municipality"],
            "character": nb["character"],
            "primary_station": nb["primary_transit_station"],
            "transit_modes": nb["transit_modes"],
            "commute_minutes": nb.get("commute_minutes", 15),
            "selected_workplace": nb.get("selected_workplace", "Stockholm Central"),
            "amenities": nb.get("amenities", []),
            "vibe_tags": nb.get("vibe_tags", []),
            "typical_housing": nb.get("typical_housing_stock", "")
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
