import unittest
from tools.budget import calculate_rent_budget
from tools.scb_client import get_scb_municipality_stats, compare_scb_municipalities
from tools.commute import evaluate_commute, find_viable_areas_for_workplace
from tools.listings import search_verified_listings

class TestWorkNestTools(unittest.TestCase):
    def test_budget_calculator(self):
        res = calculate_rent_budget(net_income_sek=35000, fixed_expenses_sek=10000, buffer_percentage=15)
        self.assertNotIn("error", res)
        self.assertGreater(res["max_rent_sek"], 0)
        self.assertLessEqual(res["recommended_rent_prudent_sek"], res["max_rent_sek"])
        self.assertEqual(res["financial_health"], "comfortable")
        self.assertIn("explanation", res)

    def test_scb_client_stockholm(self):
        res = get_scb_municipality_stats("Stockholm")
        self.assertNotIn("error", res)
        self.assertEqual(res["scb_region_code"], "0180")
        self.assertIsNotNone(res["annual_rent_per_sqm_sek"])
        self.assertGreater(res["annual_rent_per_sqm_sek"], 1000)
        self.assertIsNotNone(res["municipal_tax_rate_percent"])

    def test_scb_client_solna(self):
        res = get_scb_municipality_stats("Solna")
        self.assertNotIn("error", res)
        self.assertEqual(res["scb_region_code"], "0184")
        self.assertIsNotNone(res["annual_rent_per_sqm_sek"])

    def test_commute_corridor(self):
        res = evaluate_commute(origin_area="Solna", workplace="Stockholm Central / City", max_commute_minutes=30)
        self.assertNotIn("error", res)
        self.assertTrue(res["is_viable"])
        self.assertLessEqual(res["estimated_transit_minutes"], 15)

    def test_find_viable_areas(self):
        areas = find_viable_areas_for_workplace("Kista Science City", max_commute_minutes=25)
        self.assertGreater(len(areas), 0)
        municipalities = [a["municipality"] for a in areas]
        self.assertTrue("Solna" in municipalities or "Sundbyberg" in municipalities)

    def test_verified_listings(self):
        res = search_verified_listings(municipality="Solna", max_rent_sek=15000)
        self.assertGreaterEqual(res["verified_listings_count"], 1)
        self.assertIn("official_municipal_queue", res)
        self.assertIn("transparency_notice", res)

if __name__ == "__main__":
    unittest.main()
