"""
SCB (Statistiska centralbyrån) Client
Fetches official Swedish open statistics for municipal rents (BO0406Tab01)
and municipal tax rates (Kommunalskatter2000).
"""

import json
import urllib.request
from typing import Dict, Any, List, Optional

# Municipal code mappings for major Swedish job centers and surroundings
MUNICIPALITY_CODES = {
    # Greater Stockholm
    "Stockholm": "0180",
    "Solna": "0184",
    "Sundbyberg": "0183",
    "Huddinge": "0126",
    "Sollentuna": "0163",
    "Nacka": "0182",
    "Järfälla": "0123",
    "Täby": "0160",
    "Botkyrka": "0127",
    "Södertälje": "0181",
    "Haninge": "0136",
    "Uppsala": "0380",
    # Greater Göteborg
    "Göteborg": "1480",
    "Mölndal": "1481",
    "Partille": "1402",
    "Kungälv": "1482",
    "Borås": "1490",
    # Greater Malmö / Skåne
    "Malmö": "1280",
    "Lund": "1281",
    "Helsingborg": "1283"
}

SCB_RENT_URL = "https://api.scb.se/OV0104/v1/doris/sv/ssd/BO/BO0406/BO0406E/BO0406Tab01"
SCB_TAX_URL = "https://api.scb.se/OV0104/v1/doris/sv/ssd/OE/OE0101/Kommunalskatter2000"

def get_scb_municipality_stats(municipality_name: str, year: str = "2026") -> Dict[str, Any]:
    """
    Retrieves authentic SCB rent per square meter and municipal tax rate.
    
    Args:
        municipality_name: Swedish municipality name (e.g., 'Stockholm', 'Solna', 'Huddinge').
        year: Statistical year (defaults to latest available '2026').
    """
    code = MUNICIPALITY_CODES.get(municipality_name.strip().title())
    if not code:
        # Fallback search matching lower-case
        for name, c in MUNICIPALITY_CODES.items():
            if name.lower() == municipality_name.strip().lower():
                code = c
                municipality_name = name
                break

    if not code:
        return {
            "error": f"Municipality '{municipality_name}' not found in supported index.",
            "supported": list(MUNICIPALITY_CODES.keys())
        }

    # 1. Query Official SCB Rent (Annual SEK/m²)
    rent_query = {
        "query": [
            {"code": "Region", "selection": {"filter": "item", "values": [code]}},
            {"code": "Hyresuppg", "selection": {"filter": "item", "values": ["Ah_kvm"]}},
            {"code": "ContentsCode", "selection": {"filter": "item", "values": ["000000RZ"]}}, # Medelhyra
            {"code": "Tid", "selection": {"filter": "item", "values": [year, str(int(year)-1)]}}
        ],
        "response": {"format": "json"}
    }

    annual_rent_sqm = None
    stat_year = year
    try:
        req = urllib.request.Request(
            SCB_RENT_URL,
            data=json.dumps(rent_query).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("data"):
                # Take latest available year returned
                latest_item = data["data"][-1]
                stat_year = latest_item["key"][2]
                annual_rent_sqm = float(latest_item["values"][0])
    except Exception as e:
        annual_rent_sqm = None

    # 2. Query Official SCB Municipal Tax Rate
    tax_query = {
        "query": [
            {"code": "Region", "selection": {"filter": "item", "values": [code]}},
            {"code": "ContentsCode", "selection": {"filter": "item", "values": ["OE0101D1"]}}, # Total kommunalskattesats
            {"code": "Tid", "selection": {"filter": "item", "values": [year, str(int(year)-1)]}}
        ],
        "response": {"format": "json"}
    }
    tax_rate = None
    try:
        req = urllib.request.Request(
            SCB_TAX_URL,
            data=json.dumps(tax_query).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            tdata = json.loads(resp.read().decode("utf-8"))
            if tdata.get("data"):
                tax_rate = float(tdata["data"][-1]["values"][0])
    except Exception:
        tax_rate = None

    # Calculate typical monthly apartment rent estimates based on SCB sq meter baseline
    # 1 room (~35 sqm), 2 rooms (~55 sqm), 3 rooms (~75 sqm)
    monthly_estimates = {}
    if annual_rent_sqm:
        monthly_sqm = annual_rent_sqm / 12.0
        monthly_estimates = {
            "studio_35sqm_sek": round(monthly_sqm * 35),
            "1bed_55sqm_sek": round(monthly_sqm * 55),
            "2bed_75sqm_sek": round(monthly_sqm * 75),
        }

    return {
        "municipality": municipality_name,
        "scb_region_code": code,
        "source": "Statistiska centralbyrån (SCB) Doris Open API",
        "statistic_year": stat_year,
        "annual_rent_per_sqm_sek": annual_rent_sqm,
        "monthly_rent_per_sqm_sek": round(annual_rent_sqm / 12.0, 1) if annual_rent_sqm else None,
        "scb_norm_rents": monthly_estimates,
        "municipal_tax_rate_percent": tax_rate,
        "notes": "Values reflect official SCB negotiated first-hand rent averages (bruksvärdeshyra). Private second-hand rents typically command a premium."
    }

def compare_scb_municipalities(municipalities: List[str]) -> List[Dict[str, Any]]:
    """Compares multiple municipalities using real SCB data."""
    results = []
    for m in municipalities:
        res = get_scb_municipality_stats(m)
        if "error" not in res:
            results.append(res)
    return results
