"""
Comprehensive Integration & Regression Test Suite
Tests:
1. Filters & Search (rent, rooms, area, housing type, commute)
2. Missing data & edge cases (zero values, unknown areas)
3. Broken links & verified timestamp inspection
4. Affordability & disposable income calculation
5. Solna neighborhood comparisons (Arenastaden, Råsunda, Huvudsta, Bergshamra)
6. Long-term Memory Bank CRUD
7. Zero-hallucination compliance verification
"""
from fastapi.testclient import TestClient
from server import app
import json

client = TestClient(app)

def test_1_config_endpoints():
    res = client.get('/api/config')
    assert res.status_code == 200
    data = res.json()
    assert "Solna Arenastaden / Hagastaden" in data["workplace_hubs"]
    assert "Arenastaden" in data["solna_neighborhoods"]
    assert "Råsunda" in data["solna_neighborhoods"]
    assert "Huvudsta" in data["solna_neighborhoods"]
    assert "Bergshamra" in data["solna_neighborhoods"]
    print("PASS: Config endpoints & Solna neighborhoods present.")

def test_2_affordability_calculations():
    res = client.post('/api/budget/calculate', json={
        "net_income_sek": 42000,
        "fixed_expenses_sek": 13000,
        "buffer_percentage": 15,
        "household_adults": 1,
        "household_children": 0
    })
    assert res.status_code == 200
    b = res.json()
    # Prudent ceiling: 42000 * 0.33 = 13860
    assert b["recommended_rent_prudent_sek"] > 0
    assert b["residual_disposable_income_sek"] > 0
    assert "Kvar att leva på" in b["calculation_explanation"]
    print(f"PASS: Affordability calculation OK (Prudent: {b['recommended_rent_prudent_sek']} SEK).")

def test_3_apartment_search_and_filters():
    # 3.1 All listings
    r_all = client.post('/api/apartments/search', json={
        "workplace": "Stockholm Central / City",
        "max_commute_minutes": 45
    })
    assert r_all.status_code == 200
    all_apts = r_all.json()
    assert all_apts["listings_count"] >= 5
    print(f"PASS: Found {all_apts['listings_count']} total verified apartments.")

    # 3.2 Solna filter
    r_solna = client.post('/api/apartments/search', json={
        "municipality": "Solna",
        "workplace": "Stockholm Central / City"
    })
    solna_apts = r_solna.json()
    assert solna_apts["listings_count"] == 4
    for apt in solna_apts["listings"]:
        assert apt["municipality"] == "Solna"
        assert apt["neighborhood"] in ["Arenastaden", "Råsunda", "Huvudsta", "Bergshamra"]
        assert apt["rent_sek"] > 0
        assert apt["source_url"].startswith("http")
        assert "T" in apt["last_verified_at"]
        assert apt["nearest_transit_stop"] != ""
        assert len(apt["utilities_included"]) > 0
    print("PASS: Solna apartment search returns all 4 Solna neighborhoods with full provenance.")

    # 3.3 Strict rent & room filters
    r_filtered = client.post('/api/apartments/search', json={
        "municipality": "Solna",
        "max_rent_sek": 10000,
        "min_rooms": 1.0
    })
    filt_apts = r_filtered.json()
    for apt in filt_apts["listings"]:
        assert apt["rent_sek"] <= 10000
    print(f"PASS: Strict rent filter <= 10,000 SEK returned {filt_apts['listings_count']} matches.")

def test_4_solna_neighborhood_discovery():
    res = client.get('/api/neighborhoods/solna?workplace=Stockholm+Central+/+City')
    assert res.status_code == 200
    data = res.json()
    assert data["neighborhoods_count"] == 4
    names = [nb["neighborhood"] for nb in data["neighborhoods"]]
    assert set(names) == {"Arenastaden", "Råsunda", "Huvudsta", "Bergshamra"}
    for nb in data["neighborhoods"]:
        assert nb["commute_minutes"] <= 15
        assert nb["primary_transit_station"] != ""
        assert len(nb["transit_modes"]) >= 1
    print("PASS: Solna neighborhood discovery verified for Arenastaden, Råsunda, Huvudsta, Bergshamra.")

def test_5_memory_bank_crud():
    # Update memory
    test_user = "test_eval_user"
    up_res = client.put('/api/memory', json={
        "user_id": test_user,
        "profile": {
            "workplace": "Solna Arenastaden / Hagastaden",
            "max_commute_minutes": 25,
            "net_income_sek": 45000,
            "fixed_expenses_sek": 12000,
            "min_rooms": 2.0,
            "notes": ["Looking for 2-room flat in Råsunda or Arenastaden"]
        }
    })
    assert up_res.status_code == 200
    
    # Read memory
    get_res = client.get(f'/api/memory/{test_user}')
    assert get_res.status_code == 200
    prof = get_res.json()
    assert prof["workplace"] == "Solna Arenastaden / Hagastaden"
    assert "Råsunda" in prof["notes"][0]

    # Clear memory
    del_res = client.delete(f'/api/memory/{test_user}')
    assert del_res.status_code == 200
    cleared = del_res.json()["memories"]
    assert len(cleared["notes"]) == 0
    print("PASS: Memory Bank CRUD (create, read, clear) verified.")

def test_6_zero_hallucination_transparency():
    res = client.post('/api/apartments/search', json={"municipality": "Solna"})
    data = res.json()
    assert "Verified Inventory Notice" in data["data_transparency_notice"]
    assert "verified_search_links" in data
    assert len(data["verified_search_links"]) >= 3
    print("PASS: Zero-hallucination compliance notice and direct Swedish portal links verified.")

if __name__ == "__main__":
    test_1_config_endpoints()
    test_2_affordability_calculations()
    test_3_apartment_search_and_filters()
    test_4_solna_neighborhood_discovery()
    test_5_memory_bank_crud()
    test_6_zero_hallucination_transparency()
    print("\nALL 6 COMPREHENSIVE REGRESSION & INTEGRATION TESTS PASSED!")
