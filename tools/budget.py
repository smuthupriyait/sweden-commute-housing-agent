"""
Sweden Housing & Commute Navigator - Financial Budget Calculator
Implements transparent, mathematically rigorous rent budgeting tailored to Sweden.
Evaluates:
  - Net monthly take-home income
  - Fixed monthly obligations (student loans, debt, insurance, daycare)
  - Recommended rent (prudent guideline: ~33% of net income, capped by disposable capacity)
  - Maximum suggested rent (upper bound before severe financial distress, capped by residual capacity)
  - Emergency savings contribution (user-defined reserve %, default 15%)
  - Remaining disposable amount before setting aside savings ('Kvar att leva på' brutto)
  - Remaining disposable amount after setting aside savings ('Kvar att leva på' netto)
  - Konsumentverket baseline cost-of-living evaluation
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
    Calculates an explainable, audited rent budget adhering to Swedish living standards.
    """
    if net_income_sek is None or net_income_sek <= 0:
        return {
            "error": "Monthly net income must be a positive number.",
            "net_income_sek": 0.0,
            "fixed_expenses_sek": float(fixed_expenses_sek or 0.0),
            "buffer_percentage": float(buffer_percentage or 15.0),
            "buffer_amount_sek": 0.0,
            "recommended_rent_prudent_sek": 0.0,
            "prudent_rent_sek": 0.0,
            "max_rent_sek": 0.0,
            "remaining_before_savings_sek": 0.0,
            "remaining_after_savings_sek": 0.0,
            "left_to_live_on_prudent_sek": 0.0,
            "residual_disposable_income_sek": 0.0,
            "konsumentverket_baseline_sek": 8500,
            "financial_health": "deficit",
            "calculation_explanation": "Net income must be greater than 0 to evaluate housing affordability."
        }
    
    net_income = float(net_income_sek)
    fixed_expenses = max(0.0, float(fixed_expenses_sek or 0.0))
    buffer_pct = max(0.0, min(50.0, float(buffer_percentage if buffer_percentage is not None else 15.0)))
    adults = max(1, int(household_adults or 1))
    children = max(0, int(household_children or 0))

    # 1. Emergency savings contribution
    buffer_amount = net_income * (buffer_pct / 100.0)

    # 2. Recommended rent calculation:
    # Standard rule: 33% of net income (e.g. 38,000 * 0.33 = 12,540 SEK)
    # Must not exceed disposable capacity (net_income - fixed_expenses - buffer_amount)
    raw_prudent = round(net_income * 0.33, 2)
    disposable_cap_after_savings = max(0.0, net_income - fixed_expenses - buffer_amount)
    affordable_prudent = min(raw_prudent, disposable_cap_after_savings)

    # 3. Maximum suggested rent calculation:
    # Upper bound before critical budget strain:
    # 42% of net income or remaining capacity before cutting into survival essentials.
    raw_max = round(net_income * 0.42, 2)
    disposable_cap_before_savings = max(0.0, net_income - fixed_expenses)
    affordable_max = min(raw_max, disposable_cap_before_savings)

    # 4. Step-by-step remaining amounts ('Kvar att leva på'):
    # a. Remaining after fixed expenses and recommended rent (BEFORE setting aside reserve):
    # For 38,000 income, 11,000 fixed, 12,540 rent -> 38,000 - 11,000 - 12,540 = 14,460 SEK.
    remaining_before_savings = round(net_income - fixed_expenses - affordable_prudent, 2)

    # b. Remaining after fixed expenses, recommended rent, AND reserve savings (AFTER setting aside reserve):
    # 14,460 - 5,700 = 8,760 SEK.
    remaining_after_savings = round(remaining_before_savings - buffer_amount, 2)

    # 5. Living cost reference cross-check (Konsumentverket Swedish standards)
    # Konsumentverket baseline ~8,500 SEK per adult, ~4,000 SEK per child (food, SL card, clothes, hygiene, leisure)
    reference_living_cost = (adults * 8500) + (children * 4000)

    # Financial health status
    if remaining_after_savings >= reference_living_cost:
        health_status = "comfortable"
    elif remaining_before_savings >= reference_living_cost:
        health_status = "moderate"
    elif remaining_before_savings > 0:
        health_status = "tight"
    else:
        health_status = "deficit"

    explanation = (
        f"With a monthly net income of {net_income:,.0f} SEK and fixed obligations of {fixed_expenses:,.0f} SEK, "
        f"recommended rent is {affordable_prudent:,.0f} SEK/month (approx. 33% of take-home pay). "
        f"This leaves {remaining_before_savings:,.0f} SEK for all other monthly living costs. "
        f"Allocating a {buffer_pct:.0f}% emergency reserve ({buffer_amount:,.0f} SEK) leaves {remaining_after_savings:,.0f} SEK "
        f"as net disposable headroom ('Kvar att leva på'). "
        f"This remaining amount must cover groceries (~4,000 SEK), SL public transit (1,020 SEK), utilities, and insurance."
    )

    max_rent_explanation = (
        f"Maximum suggested rent of {affordable_max:,.0f} SEK represents an upper boundary (~42% of take-home pay) "
        f"under the assumption that discretionary spending and savings are minimized. It is not universally affordable "
        f"and increases vulnerability to interest rate hikes, inflation, and unexpected expenses."
    )

    disclaimer = (
        "Cost of Living Guidance: Remaining disposable income must cover food & groceries (~4,000 SEK/adult), "
        "SL public transport (1,020 SEK/month), home insurance (hemförsäkring ~150-300 SEK), household electricity, "
        "and mobile/broadband. Furthermore, landlords in Sweden often enforce strict income requirements "
        "(typically demanding gross income equal to 3x monthly rent)."
    )

    return {
        "net_income_sek": round(net_income, 2),
        "fixed_expenses_sek": round(fixed_expenses, 2),
        "buffer_percentage": buffer_pct,
        "buffer_amount_sek": round(buffer_amount, 2),
        "emergency_buffer_sek": round(buffer_amount, 2),
        "recommended_rent_prudent_sek": round(affordable_prudent, 0),
        "prudent_rent_sek": round(affordable_prudent, 0),
        "max_rent_sek": round(affordable_max, 0),
        "remaining_before_savings_sek": round(remaining_before_savings, 0),
        "remaining_after_savings_sek": round(remaining_after_savings, 0),
        "left_to_live_on_prudent_sek": round(remaining_after_savings, 0),
        "residual_disposable_income_sek": round(remaining_after_savings, 0),
        "konsumentverket_baseline_sek": reference_living_cost,
        "swedish_baseline_reference_sek": reference_living_cost,
        "financial_health": health_status,
        "explanation": explanation,
        "calculation_explanation": explanation,
        "max_rent_explanation": max_rent_explanation,
        "eligibility_disclaimer": disclaimer
    }
