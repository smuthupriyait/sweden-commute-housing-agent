"""
Area Scoring and Ranking Module
Transparent, configurable multi-criteria ranking for Swedish residential areas
based on user preferences: Budget headroom, Commute time, SCB rent baseline, and Municipal tax.
"""

from typing import Dict, Any, List

def score_and_rank_areas(
    viable_areas: List[Dict[str, Any]],
    user_budget_max_sek: float,
    weight_commute: float = 0.40,
    weight_rent: float = 0.35,
    weight_tax: float = 0.25
) -> List[Dict[str, Any]]:
    """
    Ranks viable areas using a normalized weighted score [0..100].
    
    Formula:
    Score = (weight_commute * Commute_Score) + (weight_rent * Rent_Score) + (weight_tax * Tax_Score)
    - Commute Score: shorter commute = higher score.
    - Rent Score: lower SCB norm rent relative to budget = higher score (more financial headroom).
    - Tax Score: lower municipal tax rate = higher score (keeps more net income).
    """
    if not viable_areas:
        return []

    # Find min and max for normalization
    commutes = [a.get("estimated_transit_minutes", 30) for a in viable_areas]
    min_commute, max_commute = min(commutes), max(commutes)
    commute_span = (max_commute - min_commute) if max_commute > min_commute else 1.0

    rents = []
    taxes = []
    for a in viable_areas:
        scb = a.get("scb_stats", {})
        rents.append(scb.get("annual_rent_per_sqm_sek") or 1600.0)
        taxes.append(scb.get("municipal_tax_rate_percent") or 31.0)

    min_rent, max_rent = min(rents), max(rents)
    rent_span = (max_rent - min_rent) if max_rent > min_rent else 1.0

    min_tax, max_tax = min(taxes), max(taxes)
    tax_span = (max_tax - min_tax) if max_tax > min_tax else 1.0

    scored = []
    for a in viable_areas:
        commute = a.get("estimated_transit_minutes", 30)
        scb = a.get("scb_stats", {})
        rent_sqm = scb.get("annual_rent_per_sqm_sek") or 1600.0
        tax = scb.get("municipal_tax_rate_percent") or 31.0

        # Invert normalized metrics so that lower values yield higher scores (0 to 100)
        s_commute = 100.0 * (1.0 - (commute - min_commute) / commute_span)
        s_rent = 100.0 * (1.0 - (rent_sqm - min_rent) / rent_span)
        s_tax = 100.0 * (1.0 - (tax - min_tax) / tax_span)

        total_score = (weight_commute * s_commute) + (weight_rent * s_rent) + (weight_tax * s_tax)

        explanation = (
            f"Overall score {round(total_score, 1)}/100. "
            f"Commute: {commute} min (Score: {round(s_commute, 1)}/100). "
            f"SCB Rent: {rent_sqm} SEK/m² (Score: {round(s_rent, 1)}/100). "
            f"Municipal Tax: {tax}% (Score: {round(s_tax, 1)}/100)."
        )

        scored.append({
            **a,
            "overall_score": round(total_score, 1),
            "sub_scores": {
                "commute_score": round(s_commute, 1),
                "rent_score": round(s_rent, 1),
                "tax_score": round(s_tax, 1)
            },
            "ranking_explanation": explanation
        })

    # Sort descending by overall score
    scored.sort(key=lambda x: x["overall_score"], reverse=True)
    for rank, item in enumerate(scored, 1):
        item["rank"] = rank

    return scored
