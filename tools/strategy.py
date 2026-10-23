"""
Search Strategy & Trade-off Advisor Module
Builds structured relocation strategies for workers in Sweden,
balancing budget headroom, queue registration timelines, and commute viability.
"""

from typing import Dict, Any, List
from tools.budget import calculate_rent_budget
from tools.scb_client import get_scb_municipality_stats
from tools.commute import find_viable_areas_for_workplace
from tools.ranking import score_and_rank_areas
from tools.listings import search_verified_listings

def generate_housing_strategy(
    net_income_sek: float,
    fixed_expenses_sek: float,
    workplace: str,
    max_commute_minutes: int = 40,
    household_adults: int = 1,
    household_children: int = 0,
    buffer_percentage: float = 15.0,
    prioritize: str = "balanced"  # 'commute', 'budget', or 'balanced'
) -> Dict[str, Any]:
    """
    Generates a structured, evidence-based housing strategy for the user.
    """
    budget = calculate_rent_budget(
        net_income_sek=net_income_sek,
        fixed_expenses_sek=fixed_expenses_sek,
        buffer_percentage=buffer_percentage,
        household_adults=household_adults,
        household_children=household_children
    )

    if "error" in budget:
        return {"error": budget["error"]}

    # Set weights according to preference
    if prioritize == "commute":
        w_commute, w_rent, w_tax = 0.60, 0.25, 0.15
    elif prioritize == "budget":
        w_commute, w_rent, w_tax = 0.20, 0.55, 0.25
    else:
        w_commute, w_rent, w_tax = 0.40, 0.35, 0.25

    viable_raw = find_viable_areas_for_workplace(workplace, max_commute_minutes)
    
    # Enrich with SCB data
    enriched = []
    for area in viable_raw:
        scb = get_scb_municipality_stats(area["municipality"])
        enriched.append({
            **area,
            "scb_stats": scb
        })

    ranked_areas = score_and_rank_areas(
        viable_areas=enriched,
        user_budget_max_sek=budget["max_rent_sek"],
        weight_commute=w_commute,
        weight_rent=w_rent,
        weight_tax=w_tax
    )

    top_3 = ranked_areas[:3] if ranked_areas else []
    
    # Verified listings in top areas
    relevant_listings = []
    for top in top_3:
        muni_listings = search_verified_listings(
            municipality=top["municipality"],
            max_rent_sek=budget["max_rent_sek"]
        )
        if muni_listings.get("verified_listings"):
            relevant_listings.extend(muni_listings["verified_listings"])

    # Actionable advice tailored to Swedish rental realities
    recommendations = [
        "1. Immediate/Short-term: Focus on verified subleases (andrahand) via Samtrygg or Blocket Bostad in your top ranked areas while adhering to the rent ceiling.",
        "2. Long-term Security: Register immediately in the municipal housing queue (Bostadsförmedlingen / Boplats) to accumulate queue days (kötid) for regulated first-hand leases (bruksvärdeshyra).",
        "3. Eligibility Check: Most professional landlords require a monthly gross income of 3x the rent or verified permanent employment contract (tillsvidareanställning).",
        "4. Deposit Protection: Never transfer deposits before lease signing and keys verification. Use escrow services."
    ]

    return {
        "budget_summary": budget,
        "workplace": workplace,
        "max_commute_minutes": max_commute_minutes,
        "strategy_priority": prioritize,
        "total_viable_areas": len(ranked_areas),
        "top_recommended_areas": top_3,
        "all_ranked_areas": ranked_areas,
        "matched_verified_listings": relevant_listings,
        "strategic_action_plan": recommendations
    }
