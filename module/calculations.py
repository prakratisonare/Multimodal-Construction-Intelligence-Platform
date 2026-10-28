TIER_MULTIPLIER = {"Tier 1": 1.35, "Tier 2": 1.0, "Tier 3": 0.82}
STRUCTURE_MULTIPLIER = {"Residential": 1.0, "Commercial": 1.18, "Industrial": 1.12, "Institutional": 1.08}
MARKET_MULTIPLIER = {"Tier 1": 1.65, "Tier 2": 1.30, "Tier 3": 1.08}

def estimate_project(structure, sqft, tier, completion, base_rate):
    budget = float(sqft) * float(base_rate) * TIER_MULTIPLIER[tier] * STRUCTURE_MULTIPLIER[structure]
    spent = budget * float(completion) / 100
    market = budget * MARKET_MULTIPLIER[tier]
    # Indicative thumb rules only; actual quantity depends on design and specifications.
    steel_tonnes = sqft * 3.8 / 1000
    cement_bags = round(sqft * 0.40)
    def money(value):
        if value >= 10_000_000:
            return f"₹{value / 10_000_000:.2f} crore"
        return f"₹{value / 100_000:.2f} lakh"
    return {
        "structure_type": structure, "built_up_sqft": int(sqft), "location_tier": tier,
        "completion_percent": int(completion), "budget_inr": round(budget),
        "budget_lakhs": budget / 100_000, "spent_inr": round(spent),
        "spent_lakhs": spent / 100_000, "market_value_inr": round(market),
        "market_value_display": money(market), "steel_tonnes": round(steel_tonnes, 2),
        "cement_bags": cement_bags,
        "assumptions": {
            "budget": "Built-up area × base rate × location and structure multipliers.",
            "market_value": "Indicative construction-budget-based multiplier; not a registered valuation.",
            "materials": "Concept-stage thumb rules only; not suitable for procurement or structural design."
        }
    }
