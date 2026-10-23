"""
Commute & Transit Assessment Module
Calculates realistic commute times and distances between workplace centers
and residential areas in Sweden using verified public transit networks and corridors.
"""

from typing import Dict, Any, List, Optional
import math

# Key employment hubs and transit nodes in Sweden with GPS coordinates
WORKPLACE_HUBS = {
    "Stockholm Central / City": {"lat": 59.3308, "lon": 18.0583, "region": "Stockholm"},
    "Kista Science City": {"lat": 59.4042, "lon": 17.9497, "region": "Stockholm"},
    "Solna Arenastaden / Hagastaden": {"lat": 59.3702, "lon": 18.0035, "region": "Stockholm"},
    "Södertälje (Scania/AstraZeneca)": {"lat": 59.1955, "lon": 17.6253, "region": "Stockholm"},
    "Göteborg Central / Lindholmen": {"lat": 57.7089, "lon": 11.9746, "region": "Göteborg"},
    "Malmö Central / Västra Hamnen": {"lat": 55.6090, "lon": 12.9999, "region": "Malmö"},
    "Uppsala Central / Fyrislund": {"lat": 59.8586, "lon": 17.6467, "region": "Uppsala"}
}

# Residential areas / Municipalities with transit nodes
RESIDENTIAL_AREAS = {
    # Stockholm Region
    "Stockholm (Inner City)": {"municipality": "Stockholm", "lat": 59.3326, "lon": 18.0649, "transit_type": "Metro / Walk"},
    "Solna": {"municipality": "Solna", "lat": 59.3599, "lon": 18.0030, "transit_type": "Metro Blue / Commuter Train"},
    "Sundbyberg": {"municipality": "Sundbyberg", "lat": 59.3621, "lon": 17.9735, "transit_type": "Metro Blue / Commuter Train"},
    "Sollentuna": {"municipality": "Sollentuna", "lat": 59.4285, "lon": 17.9509, "transit_type": "Commuter Train 40/41/42"},
    "Järfälla (Jakobsberg)": {"municipality": "Järfälla", "lat": 59.4239, "lon": 17.8336, "transit_type": "Commuter Train 43"},
    "Täby": {"municipality": "Täby", "lat": 59.4439, "lon": 18.0687, "transit_type": "Roslagsbanan / Bus"},
    "Huddinge": {"municipality": "Huddinge", "lat": 59.2366, "lon": 17.9818, "transit_type": "Commuter Train 40/41"},
    "Nacka": {"municipality": "Nacka", "lat": 59.3160, "lon": 18.1633, "transit_type": "Saltsjöbanan / Bus direct"},
    "Botkyrka (Tumba)": {"municipality": "Botkyrka", "lat": 59.1994, "lon": 17.8333, "transit_type": "Commuter Train 40/41"},
    "Södertälje": {"municipality": "Södertälje", "lat": 59.1955, "lon": 17.6253, "transit_type": "Commuter Train 40/41 / Regional"},
    "Uppsala": {"municipality": "Uppsala", "lat": 59.8586, "lon": 17.6467, "transit_type": "SJ / Mälartåg / Pendeltåg 40"},
    # Göteborg Region
    "Göteborg (Centrum)": {"municipality": "Göteborg", "lat": 57.7089, "lon": 11.9746, "transit_type": "Tram / Bus"},
    "Mölndal": {"municipality": "Mölndal", "lat": 57.6554, "lon": 12.0138, "transit_type": "Västtågen / Tram 4"},
    "Partille": {"municipality": "Partille", "lat": 57.7397, "lon": 12.1065, "transit_type": "Pendeltåg / Bus"},
    # Malmö Region
    "Malmö (Centrum)": {"municipality": "Malmö", "lat": 55.6050, "lon": 13.0038, "transit_type": "Citytunneln / Bus"},
    "Lund": {"municipality": "Lund", "lat": 55.7047, "lon": 13.1910, "transit_type": "Pågatåg / Öresundståg (10-12 min)"}
}

# Empirical transit matrix for high-speed commuter corridors (one-way transit time in minutes)
CORRIDOR_TRANSIT_MINUTES = {
    ("Stockholm Central / City", "Stockholm (Inner City)"): 8,
    ("Stockholm Central / City", "Solna"): 10,
    ("Stockholm Central / City", "Sundbyberg"): 11,
    ("Stockholm Central / City", "Sollentuna"): 16,
    ("Stockholm Central / City", "Järfälla (Jakobsberg)"): 21,
    ("Stockholm Central / City", "Huddinge"): 16,
    ("Stockholm Central / City", "Täby"): 24,
    ("Stockholm Central / City", "Nacka"): 18,
    ("Stockholm Central / City", "Botkyrka (Tumba)"): 26,
    ("Stockholm Central / City", "Södertälje"): 41,
    ("Stockholm Central / City", "Uppsala"): 38,

    ("Kista Science City", "Solna"): 12,
    ("Kista Science City", "Sundbyberg"): 9,
    ("Kista Science City", "Sollentuna"): 12,
    ("Kista Science City", "Järfälla (Jakobsberg)"): 18,
    ("Kista Science City", "Stockholm Central / City"): 17,
    ("Kista Science City", "Täby"): 28,
    ("Kista Science City", "Huddinge"): 35,
    ("Kista Science City", "Uppsala"): 35,

    ("Göteborg Central / Lindholmen", "Göteborg (Centrum)"): 8,
    ("Göteborg Central / Lindholmen", "Mölndal"): 18,
    ("Göteborg Central / Lindholmen", "Partille"): 20,

    ("Malmö Central / Västra Hamnen", "Malmö (Centrum)"): 7,
    ("Malmö Central / Västra Hamnen", "Lund"): 16
}

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two GPS coordinates."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c

def evaluate_commute(
    origin_area: str,
    workplace: str,
    max_commute_minutes: int = 45
) -> Dict[str, Any]:
    """
    Evaluates commute viability between an origin residential area and a workplace hub.
    """
    origin_info = RESIDENTIAL_AREAS.get(origin_area)
    workplace_info = WORKPLACE_HUBS.get(workplace)

    if not origin_info:
        # Match fuzzy
        for name, info in RESIDENTIAL_AREAS.items():
            if origin_area.lower() in name.lower() or origin_area.lower() == info["municipality"].lower():
                origin_area = name
                origin_info = info
                break

    if not workplace_info:
        for name, info in WORKPLACE_HUBS.items():
            if workplace.lower() in name.lower():
                workplace = name
                workplace_info = info
                break

    if not origin_info or not workplace_info:
        return {
            "error": "Origin area or workplace hub not recognized.",
            "available_workplaces": list(WORKPLACE_HUBS.keys()),
            "available_residential_areas": list(RESIDENTIAL_AREAS.keys())
        }

    # Determine transit time
    commute_mins = CORRIDOR_TRANSIT_MINUTES.get((workplace, origin_area)) or CORRIDOR_TRANSIT_MINUTES.get((origin_area, workplace))
    
    dist_km = haversine_distance_km(origin_info["lat"], origin_info["lon"], workplace_info["lat"], workplace_info["lon"])

    if commute_mins is None:
        # Fallback estimation based on Swedish suburban transit corridors (~35 km/h average with stops & transfer)
        commute_mins = round(10 + (dist_km / 35.0) * 60)

    within_limit = commute_mins <= max_commute_minutes

    return {
        "origin_area": origin_area,
        "municipality": origin_info["municipality"],
        "workplace": workplace,
        "distance_km": round(dist_km, 1),
        "estimated_transit_minutes": commute_mins,
        "transit_line_type": origin_info["transit_type"],
        "max_commute_allowed": max_commute_minutes,
        "is_viable": within_limit,
        "commute_delta_minutes": commute_mins - max_commute_minutes
    }

def find_viable_areas_for_workplace(workplace: str, max_commute_minutes: int = 45) -> List[Dict[str, Any]]:
    """Returns all residential areas viable within the max commute limit."""
    results = []
    for area in RESIDENTIAL_AREAS.keys():
        eval_res = evaluate_commute(area, workplace, max_commute_minutes)
        if "error" not in eval_res and eval_res["is_viable"]:
            results.append(eval_res)
    results.sort(key=lambda x: x["estimated_transit_minutes"])
    return results
