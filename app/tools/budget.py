"""
WorkNest Sweden - Budget Calculator Module
Implements transparent, explainable rent budgeting tailored to Sweden.
Adheres to Swedish cost of living baselines (Konsumentverket guidelines)
and the prudent 30-35% rule with safety buffers.
"""

from typing import Dict, Any

def calculate_rent_budget(
    net_income_sek: float,
    fixed_expenses_sek: float,
    buffer_percentage: float = 15.0,
    household_adults: int = 1,
    household_children: int = 0,
) -> Dict[str, Any]:
    """
    Calculates an explainable recommended rent budget based on Swedish norms.
    """
    if net_income_sek is None or net_income_sek <= 0:
        return {
            "error": "Net income must be a positive number.",
            "max_rent_sek": 0,
            "recommended_rent_min_sek": 0,
            "recommended_rent_prudent_sek": 0,
            "financial_health": "deficit"
        }
    
    fixed_expenses_sek = max(0.0, float(fixed_expenses_sek or 0.0))
    buffer_percentage = max(0.0, min(50.0, float(buffer_percentage or 15.0)))
    household_adults = max(1, int(household_adults or 1))
    household_children = max(0, int(household_children or 0))

    # 1. Standard rules: 33% prudent, 42% upper ceiling
    prudent_ceiling = net_income_sek * 0.33
    maximum_ceiling = net_income_sek * 0.42
    
    # 2. Residual income calculation ('Kvar att leva på' - Swedish financial baseline)
    buffer_amount = net_income_sek * (buffer_percentage / 100.0)
    residual_capacity = net_income_sek - fixed_expenses_sek - buffer_amount
    
    affordable_max = max(0.0, min(maximum_ceiling, residual_capacity))
    affordable_prudent = max(0.0, min(prudent_ceiling, residual_capacity * 0.85))
    affordable_min = max(0.0, min(net_income_sek * 0.20, affordable_prudent * 0.70))
    
    # Swedish reference baseline check (Konsumentverket reference values)
    # Konsumentverket sets minimum reasonable living expenses for single adult ~8,500 SEK (excl. rent)
    reference_living_cost = (household_adults * 8500) + (household_children * 4000)
    left_after_rent_max = net_income_sek - affordable_max - fixed_expenses_sek
    left_after_rent_prudent = net_income_sek - affordable_prudent - fixed_expenses_sek
    
    health_status = "comfortable"
    if left_after_rent_max < reference_living_cost:
        health_status = "tight"
    if residual_capacity <= 0:
        health_status = "deficit"

    explanation = (
        f"With a monthly net income of {net_income_sek:,.0f} SEK and {fixed_expenses_sek:,.0f} SEK in fixed costs, "
        f"a {buffer_percentage:.0f}% savings buffer reserves {buffer_amount:,.0f} SEK. "
        f"Recommended prudent rent is {affordable_prudent:,.0f} SEK/month (max {affordable_max:,.0f} SEK/month). "
        f"After paying recommended rent, you retain ~{left_after_rent_prudent:,.0f} SEK for living expenses and discretionary savings."
    )

    disclaimer = (
        "Note: This is a suggested budgetary guideline based on Swedish living standards. "
        "Landlords in Sweden often enforce strict eligibility requirements (such as permanent employment "
        "and gross income at least 3x the monthly rent)."
    )

    return {
        "net_income_sek": round(net_income_sek, 2),
        "fixed_expenses_sek": round(fixed_expenses_sek, 2),
        "buffer_percentage": buffer_percentage,
        "buffer_amount_sek": round(buffer_amount, 2),
        "recommended_rent_min_sek": round(affordable_min, 0),
        "recommended_rent_prudent_sek": round(affordable_prudent, 0),
        "max_rent_sek": round(affordable_max, 0),
        "left_to_live_on_prudent_sek": round(left_after_rent_prudent, 0),
        "left_to_live_on_max_sek": round(left_after_rent_max, 0),
        "swedish_baseline_reference_sek": reference_living_cost,
        "financial_health": health_status,
        "explanation": explanation,
        "eligibility_disclaimer": disclaimer
    }
