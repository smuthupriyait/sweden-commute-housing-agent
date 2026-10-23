"""
Comprehensive Automated Test Suite & Evaluator for WorkNest Sweden
Tests:
- Edge case budget inputs (zero, negative, high fixed expenses, family size).
- SCB client data fidelity & missing municipality handling.
- Commute matrix calculations & corridor accuracy.
- Multi-criteria area ranking determinism.
- Relocation search strategy generator.
- Verified listings zero-hallucination compliance.
"""

import unittest
from tools.budget import calculate_rent_budget
from tools.scb_client import get_scb_municipality_stats, MUNICIPALITY_CODES
from tools.commute import evaluate_commute, find_viable_areas_for_workplace, WORKPLACE_HUBS
from tools.ranking import score_and_rank_areas
from tools.strategy import generate_housing_strategy
from tools.listings import search_verified_listings

class TestWorkNestExtended(unittest.TestCase):
    # 1. Budget Edge Cases
    def test_budget_negative_income(self):
        res = calculate_rent_budget(-1000, 5000)
        self.assertIn("error", res)
        self.assertEqual(res["max_rent_sek"], 0)

    def test_budget_zero_income(self):
        res = calculate_rent_budget(0, 5000)
        self.assertIn("error", res)

    def test_budget_high_expenses_deficit(self):
        # Income 20,000 SEK, expenses 19,000 SEK -> deficit
        res = calculate_rent_budget(20000, 19000, buffer_percentage=10)
        self.assertEqual(res["financial_health"], "deficit")

    def test_budget_family_household(self):
        # 2 adults, 2 children
        res = calculate_rent_budget(55000, 15000, household_adults=2, household_children=2)
        self.assertEqual(res["swedish_baseline_reference_sek"], (2*8500)+(2*4000))
        self.assertGreater(res["recommended_rent_prudent_sek"], 10000)

    # 2. SCB Client Verification
    def test_scb_invalid_municipality(self):
        res = get_scb_municipality_stats("Atlantis")
        self.assertIn("error", res)
        self.assertIn("supported", res)

    def test_scb_goteborg(self):
        res = get_scb_municipality_stats("Göteborg")
        self.assertNotIn("error", res)
        self.assertEqual(res["scb_region_code"], "1480")
        self.assertIsNotNone(res["annual_rent_per_sqm_sek"])

    def test_scb_malmo(self):
        res = get_scb_municipality_stats("Malmö")
        self.assertNotIn("error", res)
        self.assertEqual(res["scb_region_code"], "1280")
        self.assertIsNotNone(res["annual_rent_per_sqm_sek"])

    # 3. Commute Corridor Evaluation
    def test_commute_invalid_hub(self):
        res = evaluate_commute("Solna", "Tokyo Central Station")
        self.assertIn("error", res)

    def test_commute_goteborg_corridor(self):
        res = evaluate_commute("Mölndal", "Göteborg Central / Lindholmen", max_commute_minutes=30)
        self.assertTrue(res["is_viable"])
        self.assertLessEqual(res["estimated_transit_minutes"], 20)

    # 4. Multi-criteria Ranking
    def test_area_ranking_order(self):
        viable = [
            {"origin_area": "Solna", "estimated_transit_minutes": 10, "scb_stats": {"annual_rent_per_sqm_sek": 1783, "municipal_tax_rate_percent": 29.7}},
            {"origin_area": "Södertälje", "estimated_transit_minutes": 41, "scb_stats": {"annual_rent_per_sqm_sek": 1450, "municipal_tax_rate_percent": 32.1}}
        ]
        # Commute priority: Solna should rank #1
        ranked = score_and_rank_areas(viable, user_budget_max_sek=15000, weight_commute=0.7, weight_rent=0.2, weight_tax=0.1)
        self.assertEqual(ranked[0]["origin_area"], "Solna")
        self.assertEqual(ranked[0]["rank"], 1)

    # 5. Relocation Strategy Generator
    def test_strategy_generation(self):
        strat = generate_housing_strategy(
            net_income_sek=38000,
            fixed_expenses_sek=12000,
            workplace="Stockholm Central / City",
            max_commute_minutes=35,
            prioritize="balanced"
        )
        self.assertNotIn("error", strat)
        self.assertGreater(strat["total_viable_areas"], 0)
        self.assertGreaterEqual(len(strat["top_recommended_areas"]), 1)
        self.assertGreaterEqual(len(strat["strategic_action_plan"]), 3)

    # 6. Listing Integrity
    def test_no_invented_listings(self):
        # Calling without filters should only return verified instances and official channels
        res = search_verified_listings()
        for item in res["verified_listings"]:
            self.assertIn("url", item)
            self.assertIn("source", item)
            self.assertTrue(item["url"].startswith("http"))
        self.assertIn("official_municipal_queue", res)

if __name__ == "__main__":
    unittest.main()
