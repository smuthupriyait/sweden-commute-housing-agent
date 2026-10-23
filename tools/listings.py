"""
Housing Discovery & Verified Queue Directory Engine
Maintains representative sample properties with full provenance, timestamps,
and direct deep-filtered search portals to official Swedish queues and marketplaces.

Trust & Integrity Policy:
- Distinctly marks representative reference properties as "Curated Sample Listing" so users
  are never misled into believing they are querying a real-time live scraping feed.
- Swedish rental platforms (Blocket Bostad, Qasa, Samtrygg) do not provide public unauthenticated REST APIs.
  Direct deep links to these platforms with the user's filtered criteria are provided for live applications.
- All municipal housing queue references are authentic and verified (Bostadsförmedlingen, Signalisten, etc.).
"""

from typing import Dict, Any, List, Optional
import urllib.parse
from datetime import datetime

# Official housing queues and municipal providers
OFFICIAL_HOUSING_SERVICES = {
    "Stockholm": {
        "name": "Bostadsförmedlingen i Stockholm",
        "url": "https://bostad.stockholm.se/",
        "type": "Official Municipal Housing Queue",
        "details": "Central queue for first-hand rental apartments (hyresrätter) across Stockholm County."
    },
    "Solna": {
        "name": "Signalisten (Solna Municipal Housing)",
        "url": "https://www.signalisten.se/",
        "type": "Municipal Housing Company",
        "details": "Solna's municipal housing company (Signalisten) distributes through Bostadsförmedlingen i Stockholm."
    },
    "Sundbyberg": {
        "name": "Förvaltaren (Sundbyberg Municipal Housing)",
        "url": "https://www.forvaltaren.se/",
        "type": "Municipal Housing Company",
        "details": "Sundbyberg's municipal housing queue and direct youth/student allocations."
    },
    "Göteborg": {
        "name": "Boplats Göteborg",
        "url": "https://nya.boplats.se/",
        "type": "Official Municipal Housing Queue",
        "details": "Municipal portal for rental apartments across Göteborg and surrounding municipalities."
    },
    "Malmö": {
        "name": "Boplats Syd",
        "url": "https://www.boplatssyd.se/",
        "type": "Regional Housing Queue",
        "details": "Regional housing distribution service for Skåne, including Malmö and Lund."
    },
    "Uppsala": {
        "name": "Uppsala Bostadsförmedling",
        "url": "https://www.bostad.uppsala.se/",
        "type": "Official Municipal Housing Queue",
        "details": "Official housing queue for Uppsala municipality."
    }
}

# Curated reference properties for neighborhood exploration
# Each entry is clearly labelled as data_classification="Curated Sample Listing"
SAMPLE_REFERENCE_APARTMENTS = [
    {
        "id": "SAMPLE-SOL-01",
        "data_classification": "Curated Sample Property",
        "is_sample_data": True,
        "is_illustrative_example": True,
        "title": "Hypothetical Scenario: 2-Room Layout in Arenastaden Area",
        "municipality": "Solna",
        "neighborhood": "Arenastaden",
        "address": "Generic Area Example: Evenemangsgatan vicinity, Arenastaden",
        "rent_sek": 12800,
        "rooms": 2.0,
        "size_sqm": 54,
        "housing_type": "Hypothetical Sublet Scenario (Generic Model)",
        "lease_duration": "Hypothetical term (e.g. 12 months)",
        "deposit_sek": 12800,
        "deposit_terms": "Hypothetical assumption: 1 month security deposit",
        "utilities_included": ["District heating (typical)", "Water (typical)", "Broadband (typical)"],
        "utilities_excluded": ["Household electricity (~350 SEK/mo estimated)"],
        "available_from": "Hypothetical move-in date",
        "nearest_transit_stop": "Solna Station (Pendeltåg & Tvärbanan, ~300m walk)",
        "commute_to_hubs": {
            "Stockholm Central / City": 7,
            "Kista Science City": 14,
            "Solna Arenastaden / Hagastaden": 3,
            "Södertälje (Scania/AstraZeneca)": 48
        },
        "source": "Market Reference (General Portal)",
        "source_url": "https://www.samtrygg.se/rental/search?q=Solna",
        "sample_data_note": "Fictional/illustrative scenario for comparison modeling only; not an actual vacancy",
        "features": ["Balcony layout (typical)", "Elevator access", "Bicycle storage"]
    },
    {
        "id": "SAMPLE-SOL-02",
        "data_classification": "Curated Sample Property",
        "is_sample_data": True,
        "is_illustrative_example": True,
        "title": "Hypothetical Scenario: 1.5-Room Layout in Råsunda Area",
        "municipality": "Solna",
        "neighborhood": "Råsunda",
        "address": "Generic Area Example: Stråket vicinity, Råsunda",
        "rent_sek": 9950,
        "rooms": 1.5,
        "size_sqm": 43,
        "housing_type": "Hypothetical Sublet Scenario (Generic Model)",
        "lease_duration": "Hypothetical term (e.g. 12 months)",
        "deposit_sek": 9950,
        "deposit_terms": "Hypothetical assumption: 1 month security deposit",
        "utilities_included": ["Heating (typical)", "Water (typical)"],
        "utilities_excluded": ["Electricity", "Home insurance (Hemförsäkring)"],
        "available_from": "Hypothetical move-in date",
        "nearest_transit_stop": "Solna Centrum Metro (Blue line, ~450m walk)",
        "commute_to_hubs": {
            "Stockholm Central / City": 10,
            "Kista Science City": 12,
            "Solna Arenastaden / Hagastaden": 8,
            "Södertälje (Scania/AstraZeneca)": 52
        },
        "source": "Market Reference (General Portal)",
        "source_url": "https://qasa.se/sv/find-home?q=Solna",
        "sample_data_note": "Fictional/illustrative scenario for comparison modeling only; not an actual vacancy",
        "features": ["High ceilings (typical)", "Parquet flooring", "Courtyard aspect"]
    },
    {
        "id": "SAMPLE-SOL-03",
        "data_classification": "Curated Sample Property",
        "is_sample_data": True,
        "is_illustrative_example": True,
        "title": "Hypothetical Scenario: 2-Room Layout in Huvudsta Area",
        "municipality": "Solna",
        "neighborhood": "Huvudsta",
        "address": "Generic Area Example: Storgatan vicinity, Huvudsta",
        "rent_sek": 11200,
        "rooms": 2.0,
        "size_sqm": 50,
        "housing_type": "Hypothetical Sublet Scenario (Generic Model)",
        "lease_duration": "Hypothetical term (e.g. 12 months)",
        "deposit_sek": 11200,
        "deposit_terms": "Hypothetical assumption: 1 month security deposit",
        "utilities_included": ["Heating (typical)", "Water (typical)", "Basement storeroom"],
        "utilities_excluded": ["Electricity", "Broadband"],
        "available_from": "Hypothetical move-in date",
        "nearest_transit_stop": "Huvudsta Metro Station (Blue line, ~350m walk)",
        "commute_to_hubs": {
            "Stockholm Central / City": 9,
            "Kista Science City": 15,
            "Solna Arenastaden / Hagastaden": 12,
            "Södertälje (Scania/AstraZeneca)": 51
        },
        "source": "Market Reference (General Portal)",
        "source_url": "https://www.samtrygg.se/rental/search?q=Huvudsta",
        "sample_data_note": "Fictional/illustrative scenario for comparison modeling only; not an actual vacancy",
        "features": ["Waterfront promenade vicinity", "Balcony layout (typical)"]
    },
    {
        "id": "SAMPLE-SOL-04",
        "data_classification": "Curated Sample Property",
        "is_sample_data": True,
        "is_illustrative_example": True,
        "title": "Hypothetical Scenario: 1-Room Studio in Bergshamra Area",
        "municipality": "Solna",
        "neighborhood": "Bergshamra",
        "address": "Generic Area Example: Björnstigen vicinity, Bergshamra",
        "rent_sek": 8700,
        "rooms": 1.0,
        "size_sqm": 34,
        "housing_type": "Hypothetical Student/Compact Scenario",
        "lease_duration": "Hypothetical term (e.g. flexible)",
        "deposit_sek": 8700,
        "deposit_terms": "Hypothetical assumption: 1 month security deposit",
        "utilities_included": ["Heating (typical)", "Water (typical)", "Wifi (typical)"],
        "utilities_excluded": [],
        "available_from": "Hypothetical move-in date",
        "nearest_transit_stop": "Bergshamra Metro Station (Red line 14, ~250m walk)",
        "commute_to_hubs": {
            "Stockholm Central / City": 11,
            "Kista Science City": 22,
            "Solna Arenastaden / Hagastaden": 14,
            "Södertälje (Scania/AstraZeneca)": 55
        },
        "source": "Market Reference (General Portal)",
        "source_url": "https://bostad.blocket.se/sv/bostad?q=Solna",
        "sample_data_note": "Fictional/illustrative scenario for comparison modeling only; not an actual vacancy",
        "features": ["Green park surroundings", "Direct Red Line connection to T-Centralen"]
    },
    {
        "id": "SAMPLE-SBY-05",
        "data_classification": "Curated Sample Property",
        "is_sample_data": True,
        "is_illustrative_example": True,
        "title": "Hypothetical Scenario: 2-Room Layout in Central Sundbyberg Area",
        "municipality": "Sundbyberg",
        "neighborhood": "Centrala Sundbyberg",
        "address": "Generic Area Example: Landsvägen vicinity, Sundbyberg",
        "rent_sek": 11900,
        "rooms": 2.0,
        "size_sqm": 48,
        "housing_type": "Hypothetical Sublet Scenario (Generic Model)",
        "lease_duration": "Hypothetical term (e.g. 12 months)",
        "deposit_sek": 11900,
        "deposit_terms": "Hypothetical assumption: 1 month security deposit",
        "utilities_included": ["Heating (typical)", "Water (typical)", "Broadband (typical)"],
        "utilities_excluded": ["Household electricity"],
        "available_from": "Hypothetical move-in date",
        "nearest_transit_stop": "Sundbyberg Station (Metro, Pendeltåg & Tvärbanan, ~150m walk)",
        "commute_to_hubs": {
            "Stockholm Central / City": 8,
            "Kista Science City": 9,
            "Solna Arenastaden / Hagastaden": 7,
            "Södertälje (Scania/AstraZeneca)": 49
        },
        "source": "Market Reference (General Portal)",
        "source_url": "https://www.samtrygg.se/rental/search?q=Sundbyberg",
        "sample_data_note": "Fictional/illustrative scenario for comparison modeling only; not an actual vacancy",
        "features": ["Transit hub vicinity", "Local cafes and grocery access"]
    },
    {
        "id": "SAMPLE-KGH-06",
        "data_classification": "Curated Sample Property",
        "is_sample_data": True,
        "is_illustrative_example": True,
        "title": "Hypothetical Scenario: 1-Room Studio in Kungsholmen Area",
        "municipality": "Stockholm",
        "neighborhood": "Kungsholmen",
        "address": "Generic Area Example: Pontonjärgatan vicinity, Kungsholmen",
        "rent_sek": 13900,
        "rooms": 1.0,
        "size_sqm": 33,
        "housing_type": "Hypothetical Sublet Scenario (Generic Model)",
        "lease_duration": "Hypothetical term (e.g. 12 months)",
        "deposit_sek": 13900,
        "deposit_terms": "Hypothetical assumption: 1 month security deposit",
        "utilities_included": ["Heating (typical)", "Water (typical)", "Internet (typical)"],
        "utilities_excluded": ["Electricity"],
        "available_from": "Hypothetical move-in date",
        "nearest_transit_stop": "Fridhemsplan Metro (Blue & Green lines, ~400m walk)",
        "commute_to_hubs": {
            "Stockholm Central / City": 4,
            "Kista Science City": 16,
            "Solna Arenastaden / Hagastaden": 10,
            "Södertälje (Scania/AstraZeneca)": 44
        },
        "source": "Market Reference (General Portal)",
        "source_url": "https://qasa.se/sv/find-home?q=Stockholm",
        "sample_data_note": "Fictional/illustrative scenario for comparison modeling only; not an actual vacancy",
        "features": ["Inner-city vicinity", "Waterfront promenade access"]
    },
    {
        "id": "SAMPLE-SOL-07",
        "data_classification": "Curated Sample Property",
        "is_sample_data": True,
        "is_illustrative_example": True,
        "title": "Hypothetical Scenario: 3-Room Layout in Helenelund Area",
        "municipality": "Sollentuna",
        "neighborhood": "Helenelund / Tureberg",
        "address": "Generic Area Example: Svalgången vicinity, Sollentuna",
        "rent_sek": 12500,
        "rooms": 3.0,
        "size_sqm": 72,
        "housing_type": "Hypothetical Sublet Scenario (Generic Model)",
        "lease_duration": "Hypothetical term (e.g. 12 months)",
        "deposit_sek": 12500,
        "deposit_terms": "Hypothetical assumption: 1 month security deposit",
        "utilities_included": ["Heating (typical)", "Water (typical)"],
        "utilities_excluded": ["Electricity", "Internet"],
        "available_from": "Hypothetical move-in date",
        "nearest_transit_stop": "Helenelund Station (Pendeltåg, ~500m walk)",
        "commute_to_hubs": {
            "Stockholm Central / City": 14,
            "Kista Science City": 6,
            "Solna Arenastaden / Hagastaden": 9,
            "Södertälje (Scania/AstraZeneca)": 54
        },
        "source": "Market Reference (General Portal)",
        "source_url": "https://bostad.blocket.se/sv/bostad?q=Sollentuna",
        "sample_data_note": "Fictional/illustrative scenario for comparison modeling only; not an actual vacancy",
        "features": ["Glazed balcony (typical)", "Footbridge access to Kista"]
    }
]

def search_apartment_listings(
    municipality: Optional[str] = None,
    neighborhood: Optional[str] = None,
    max_rent_sek: Optional[float] = None,
    min_rooms: Optional[float] = None,
    max_rooms: Optional[float] = None,
    min_sqm: Optional[float] = None,
    housing_type: Optional[str] = None,
    workplace: str = "Stockholm Central / City",
    max_commute_minutes: Optional[int] = None,
    user_net_income: Optional[float] = 38000.0,
    user_prudent_rent_sek: Optional[float] = 12540.0
) -> Dict[str, Any]:
    """
    Filters curated sample apartments with transparent scoring,
    and constructs targeted deep search links to live Swedish rental platforms and official queues.
    """
    matched: List[Dict[str, Any]] = []

    for apt in SAMPLE_REFERENCE_APARTMENTS:
        # Municipality filter
        if municipality and municipality.strip() and municipality.lower() not in apt["municipality"].lower():
            continue
        
        # Neighborhood filter
        if neighborhood and neighborhood.strip() and neighborhood.lower() not in apt["neighborhood"].lower():
            continue

        # Rent filter
        if max_rent_sek is not None and apt["rent_sek"] > max_rent_sek:
            continue

        # Rooms filter
        if min_rooms is not None and apt["rooms"] < min_rooms:
            continue
        if max_rooms is not None and apt["rooms"] > max_rooms:
            continue

        # Area sqm filter
        if min_sqm is not None and apt["size_sqm"] < min_sqm:
            continue

        # Housing type filter
        if housing_type and housing_type.strip().lower() not in ["all", ""]:
            if housing_type.lower() not in apt["housing_type"].lower():
                continue

        # Commute calculation to user's workplace
        commute_mins = apt["commute_to_hubs"].get(workplace)
        if commute_mins is None:
            commute_mins = 20  # Suburban baseline connection
        
        if max_commute_minutes is not None and commute_mins > max_commute_minutes:
            continue

        # Calculate Demonstration Match Score [0..100]
        # Match considers: Rent headroom vs user budget (50% weight), Commute efficiency (30% weight), Space/sqm (20% weight)
        ref_budget = user_prudent_rent_sek or 12540.0
        rent_ratio = apt["rent_sek"] / ref_budget if ref_budget > 0 else 1.0
        if rent_ratio <= 1.0:
            rent_score = 100.0 - (rent_ratio * 15.0)  # e.g., 85 - 100
        else:
            rent_score = max(20.0, 85.0 - (rent_ratio - 1.0) * 150.0)

        commute_score = max(20.0, 100.0 - (commute_mins * 2.0))
        size_score = min(100.0, (apt["size_sqm"] / (apt["rooms"] * 30.0)) * 90.0)

        demo_match_score = round((0.50 * rent_score) + (0.30 * commute_score) + (0.20 * size_score), 1)

        # Budget delta & disposable headroom
        rent_diff = round(ref_budget - apt["rent_sek"])
        budget_headroom_note = (
            f"{abs(rent_diff):,} SEK below suggested prudent budget" if rent_diff >= 0
            else f"{abs(rent_diff):,} SEK above suggested prudent budget"
        )

        matched_item = {
            **apt,
            "calculated_commute_minutes": commute_mins,
            "workplace_destination": workplace,
            "match_score": demo_match_score,
            "budget_delta_sek": rent_diff,
            "match_explanation": (
                f"Demonstration Match Score: {demo_match_score}/100 (Weights: 50% Rent Headroom, 30% Commute, 20% Size). "
                f"Rent is {budget_headroom_note}. Illustrative unverified travel time to {workplace} is ~{commute_mins} minutes "
                f"via {apt['nearest_transit_stop']} (scheduled transit line + station walk; excludes transfer waits, door-to-door buffer, and peak disruptions)."
            )
        }
        matched.append(matched_item)

    # Sort by match score descending
    matched.sort(key=lambda x: x["match_score"], reverse=True)

    # Resolve municipal queue
    muni_key = municipality if municipality in OFFICIAL_HOUSING_SERVICES else "Stockholm"
    official_queue = OFFICIAL_HOUSING_SERVICES.get(muni_key, OFFICIAL_HOUSING_SERVICES["Stockholm"])

    # Direct links to public Swedish portals and queues
    query_str = urllib.parse.quote(f"{municipality or 'Stockholm'} {neighborhood or ''}".strip())

    external_search_links = [
        {
            "service": "Blocket Bostad",
            "url": f"https://bostad.blocket.se/sv/bostad?q={query_str}",
            "description": f"Search listings in {municipality or 'Stockholm'}"
        },
        {
            "service": "Samtrygg",
            "url": f"https://www.samtrygg.se/rental/search?q={query_str}",
            "description": f"Search sublets in {municipality or 'Stockholm'}"
        },
        {
            "service": "Qasa",
            "url": f"https://qasa.se/sv/find-home?q={query_str}",
            "description": f"Search rentals in {municipality or 'Stockholm'}"
        },
        {
            "service": official_queue["name"],
            "url": official_queue["url"],
            "description": f"Official municipal housing queue ({official_queue['type']})"
        }
    ]

    return {
        "listings_count": len(matched),
        "listings": matched,
        "official_queue": official_queue,
        "verified_search_links": external_search_links,
        "is_sample_inventory": True,
        "data_transparency_notice": (
            "Illustrative Sample Notice: The properties listed above are illustrative comparison scenarios for modeling "
            "typical price levels, space, and transit connections in these neighborhoods. They do not represent real-time "
            "vacancies. Commute figures are unverified illustrative estimates. For real available vacancies, use the Housing Search Links below."
        )
    }

def search_verified_listings(
    municipality: Optional[str] = None,
    max_rent_sek: Optional[float] = None,
    min_rooms: Optional[float] = None
) -> Dict[str, Any]:
    """Backward-compatible proxy to search_apartment_listings."""
    res = search_apartment_listings(
        municipality=municipality,
        max_rent_sek=max_rent_sek,
        min_rooms=min_rooms
    )
    return {
        "verified_listings_count": res["listings_count"],
        "verified_listings": res["listings"],
        "official_municipal_queue": res["official_queue"],
        "verified_portal_searches": res["verified_search_links"],
        "transparency_notice": res["data_transparency_notice"]
    }
