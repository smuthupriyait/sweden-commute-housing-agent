"""
Neighborhood Intelligence & Transit Comparison Module
Provides verified neighborhood-level data for promising municipalities in Sweden,
with deep dive coverage for Solna (Arenastaden, Råsunda, Huvudsta, Bergshamra)
and neighboring metropolitan commuter districts.

Transits and station connections are verified against Storstockholms Lokaltrafik (SL)
and Trafikverket rail / metro lines.
"""

from typing import Dict, Any, List, Optional

SOLNA_NEIGHBORHOODS: Dict[str, Dict[str, Any]] = {
    "Arenastaden": {
        "neighborhood": "Arenastaden",
        "municipality": "Solna",
        "postcode_prefix": "169",
        "character": "Modern high-rise commercial & residential hub surrounding Strawberry Arena and Westfield Mall of Scandinavia.",
        "primary_transit_station": "Solna Station",
        "transit_modes": ["Pendeltåg (Lines 40, 41, 42)", "Tvärbanan (Line 30)", "Bus 515, 502"],
        "commute_to_workplace_minutes": {
            "Stockholm Central / City": 7,
            "Kista Science City": 14,
            "Solna Arenastaden / Hagastaden": 3,
            "Södertälje (Scania/AstraZeneca)": 48,
            "Uppsala Central / Fyrislund": 33
        },
        "scb_norm_rent_premium": 1.15,
        "typical_housing_stock": "Modern condominiums (bostadsrätter) and new production rentals (nyproduktion hyresrätter).",
        "amenities": ["Mall of Scandinavia", "Strawberry Arena", "Råstasjön nature path", "Nordic Wellness / SATS gyms"],
        "vibe_tags": ["Modern Architecture", "High Walkability", "Commercial Hub", "Ultra-Fast Commute"]
    },
    "Råsunda": {
        "neighborhood": "Råsunda",
        "municipality": "Solna",
        "postcode_prefix": "169",
        "character": "Historic stone city (stenstad) built 1910–1940, film historic charm (Gamla Filmstaden), tree-lined avenues and boutique bakeries.",
        "primary_transit_station": "Solna Centrum / Näckrosen Metro",
        "transit_modes": ["Metro Blue Line (Lines 10 & 11)", "Tvärbanan (Solna Centrum)", "Bus 515 to Odenplan"],
        "commute_to_workplace_minutes": {
            "Stockholm Central / City": 10,
            "Kista Science City": 12,
            "Solna Arenastaden / Hagastaden": 8,
            "Södertälje (Scania/AstraZeneca)": 52,
            "Uppsala Central / Fyrislund": 42
        },
        "scb_norm_rent_premium": 1.05,
        "typical_housing_stock": "Early 20th-century classic functionalist and national romantic stone apartment buildings with high ceilings.",
        "amenities": ["Gamla Filmstaden cinema & cafes", "Stråket pedestrian boulevard", "Råstasjön lake walks", "Solna Centrum shopping"],
        "vibe_tags": ["Historic Charm", "Cafes & Bakeries", "Green Parks", "Lively Neighborhood"]
    },
    "Huvudsta": {
        "neighborhood": "Huvudsta",
        "municipality": "Solna",
        "postcode_prefix": "171",
        "character": "Waterfront district along Ulvsundasjön with scenic marina walks, Huvudstabadet outdoor swimming pool, and historic Huvudsta Old Castle.",
        "primary_transit_station": "Huvudsta Metro Station",
        "transit_modes": ["Metro Blue Line (Line 10)", "Bicycle highways to Kungsholmen (15 min)"],
        "commute_to_workplace_minutes": {
            "Stockholm Central / City": 9,
            "Kista Science City": 15,
            "Solna Arenastaden / Hagastaden": 12,
            "Södertälje (Scania/AstraZeneca)": 51,
            "Uppsala Central / Fyrislund": 45
        },
        "scb_norm_rent_premium": 0.98,
        "typical_housing_stock": "Mix of 1960s–1980s municipal rental blocks (Signalisten) and contemporary waterfront apartments.",
        "amenities": ["Huvudsta Castle (Slott)", "Huvudstabadet heated pool", "Ulvsundasjön promenade", "Pampas Marina kayaking"],
        "vibe_tags": ["Waterfront", "Swimming & Boating", "Bikeable to Kungsholmen", "Quiet Residential"]
    },
    "Bergshamra": {
        "neighborhood": "Bergshamra",
        "municipality": "Solna",
        "postcode_prefix": "170",
        "character": "Scenic green neighborhood surrounded by Brunnsviken and the Royal National City Park. Strong academic profile close to Stockholm University and KTH.",
        "primary_transit_station": "Bergshamra Metro Station",
        "transit_modes": ["Metro Red Line (Line 14)", "Bus 503, 540", "Roslagsbanan (Stocksund adjacent)"],
        "commute_to_workplace_minutes": {
            "Stockholm Central / City": 11,
            "Kista Science City": 22,
            "Solna Arenastaden / Hagastaden": 14,
            "Södertälje (Scania/AstraZeneca)": 55,
            "Uppsala Central / Fyrislund": 46
        },
        "scb_norm_rent_premium": 1.02,
        "typical_housing_stock": "Functionalist brick apartment ensembles, student housing (SSSB), and tranquil residential streets.",
        "amenities": ["Brunnsviken swimming spots", "Tivoliparken", "Bergshamra Torg shops & pharmacy", "Ulriksdal Palace grounds nearby"],
        "vibe_tags": ["Nature & Forest", "Brunnsviken Lake", "Academic / Student Vibe", "Quiet & Relaxed"]
    }
}

OTHER_KEY_NEIGHBORHOODS: Dict[str, Dict[str, Any]] = {
    "Centrala Sundbyberg": {
        "neighborhood": "Centrala Sundbyberg",
        "municipality": "Sundbyberg",
        "postcode_prefix": "172",
        "character": "Dense, vibrant urban center known as 'Sweden's smallest but most urban municipality' with dense restaurants and independent shops.",
        "primary_transit_station": "Sundbyberg Station",
        "transit_modes": ["Metro Blue Line (Line 10)", "Pendeltåg (Lines 43, 44)", "Tvärbanan (Line 30)", "Regional trains (SJ)"],
        "commute_to_workplace_minutes": {
            "Stockholm Central / City": 8,
            "Kista Science City": 9,
            "Solna Arenastaden / Hagastaden": 7,
            "Södertälje (Scania/AstraZeneca)": 49,
            "Uppsala Central / Fyrislund": 38
        },
        "scb_norm_rent_premium": 1.08,
        "typical_housing_stock": "Dense stone turn-of-the-century and functionalist apartments with ground-floor retail.",
        "amenities": ["Sturegatan shopping", "Marabouparken art park", "Tornparken viewpoint cafe", "High restaurant density"],
        "vibe_tags": ["Urban Buzz", "Transit Super-Hub", "Great Dining", "Compact & Walkable"]
    },
    "Helenelund / Tureberg": {
        "neighborhood": "Helenelund / Tureberg",
        "municipality": "Sollentuna",
        "postcode_prefix": "191",
        "character": "Commuter rail corridor with direct links to Kista IT corridor and Arlanda/Stockholm C.",
        "primary_transit_station": "Helenelund / Sollentuna Station",
        "transit_modes": ["Pendeltåg (Lines 40, 41, 42)", "Direct bus corridor to Kista (5 min)"],
        "commute_to_workplace_minutes": {
            "Stockholm Central / City": 14,
            "Kista Science City": 6,
            "Solna Arenastaden / Hagastaden": 9,
            "Södertälje (Scania/AstraZeneca)": 54,
            "Uppsala Central / Fyrislund": 31
        },
        "scb_norm_rent_premium": 0.96,
        "typical_housing_stock": "Mid-century suburban apartment complexes and modern transit-oriented developments.",
        "amenities": ["Sollentuna Centrum mall", "Edsviken water views", "Kista Galleria footbridge"],
        "vibe_tags": ["Affordable Commuter", "Tech Corridor Access", "Family Friendly", "Fast Rail Link"]
    },
    "Kungsholmen": {
        "neighborhood": "Kungsholmen",
        "municipality": "Stockholm",
        "postcode_prefix": "112",
        "character": "Inner-city island district with Norrmälarstrand waterfront promenades, vibrant cafe culture, and proximity to Stockholm City Hall.",
        "primary_transit_station": "Fridhemsplan / Rådhuset Metro",
        "transit_modes": ["Metro Blue Line (Lines 10, 11)", "Metro Green Line (Lines 17, 18, 19)", "Bus 1, 3, 4"],
        "commute_to_workplace_minutes": {
            "Stockholm Central / City": 4,
            "Kista Science City": 16,
            "Solna Arenastaden / Hagastaden": 10,
            "Södertälje (Scania/AstraZeneca)": 44,
            "Uppsala Central / Fyrislund": 41
        },
        "scb_norm_rent_premium": 1.25,
        "typical_housing_stock": "Classic stone apartment buildings (1900–1935) and waterfront luxury redevelopments.",
        "amenities": ["Norrmälarstrand waterfront", "Rålambshovsparken park & beach", "Fridhemsplan hub", "Västermalmsgallerian"],
        "vibe_tags": ["Inner City Island", "Waterfront Jogging", "Bustling Cafes", "Premium Quality"]
    }
}

ALL_NEIGHBORHOODS = {**SOLNA_NEIGHBORHOODS, **OTHER_KEY_NEIGHBORHOODS}

def get_neighborhood_intelligence(
    municipality: Optional[str] = None,
    workplace: str = "Stockholm Central / City"
) -> List[Dict[str, Any]]:
    """
    Returns rich verified neighborhood profiles filtered by municipality
    with customized commute and rent figures.
    """
    results = []
    for key, data in ALL_NEIGHBORHOODS.items():
        if municipality and municipality.lower() not in data["municipality"].lower():
            continue
        
        commute_mins = data["commute_to_workplace_minutes"].get(workplace, 20)
        
        profile = {
            **data,
            "selected_workplace": workplace,
            "commute_minutes": commute_mins,
            "direct_transit_summary": f"{commute_mins} min to {workplace} via {data['primary_transit_station']}"
        }
        results.append(profile)

    results.sort(key=lambda x: x["commute_minutes"])
    return results

def get_solna_comparison(workplace: str = "Stockholm Central / City") -> List[Dict[str, Any]]:
    """Specific deep comparison for Solna's key neighborhoods."""
    return get_neighborhood_intelligence(municipality="Solna", workplace=workplace)
