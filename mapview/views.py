from django.shortcuts import render
from django.http import JsonResponse
from cart.models import Item
from django.db.models import Count
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# --- Geopy setup ---
geolocator = Nominatim(user_agent="moviesstore")

def get_coords(city, state, country):
    """Fetch coordinates for a location using GeoPy (Nominatim)."""
    try:
        # Build a simple location query string
        query = ", ".join(filter(None, [city, state, country]))
        location = geolocator.geocode(query)
        if location:
            return {"lat": location.latitude, "lng": location.longitude}
    except (GeocoderTimedOut, GeocoderUnavailable):
        return None
    return None


def gt_map(request):
    """Render the map page."""
    return render(request, "mapview/gt_map.html")


def movie_locations_api(request, movie_id):
    geolocator = Nominatim(user_agent="movies_app")

    results = (
        Item.objects.filter(movie_id=movie_id, order__location__isnull=False)
        .values("order__location__city", "order__location__state", "order__location__country")
        .annotate(count=Count("id"))
    )

    # --- normalization mapping for consistent grouping ---
    def normalize_country(country):
        if not country:
            return ""
        country = country.strip().lower()
        if country in ["us", "u.s.", "usa", "united states of america", "united states"]:
            return "USA"
        elif country in ["uk", "united kingdom", "england", "great britain"]:
            return "UK"
        elif country in ["canada"]:
            return "Canada"
        return country.title()

    def normalize_state(state):
        if not state:
            return ""
        return state.strip().title()

    # aggregate by normalized values
    aggregated = {}
    for r in results:
        city = (r["order__location__city"] or "").strip().title()
        state = normalize_state(r["order__location__state"])
        country = normalize_country(r["order__location__country"])
        key = (city, state, country)
        aggregated[key] = aggregated.get(key, 0) + r["count"]

    data = []
    for (city, state, country), total in aggregated.items():
        if not city or not country:
            continue
        query = f"{city}, {state}, {country}".strip(", ")
        try:
            location = geolocator.geocode(query, timeout=5)
        except Exception as e:
            print("Geocode error:", e)
            continue

        if location:
            data.append({
                "city": city,
                "state": state,
                "country": country,
                "count": total,
                "lat": location.latitude,
                "lng": location.longitude,
            })

    return JsonResponse(data, safe=False)

from django.views.decorators.http import require_GET

@require_GET
def continent_popularity_api(request):
    """Return total purchase counts aggregated by continent."""
    results = (
        Item.objects.filter(order__location__isnull=False)
        .values("order__location__country")
        .annotate(count=Count("id"))
    )

    # --- Normalize and map countries to continents ---
    def normalize_country(country):
        if not country:
            return ""
        c = country.strip().lower()
        if c in ["us", "usa", "united states", "united states of america"]:
            return "USA"
        if c in ["uk", "england", "great britain", "united kingdom"]:
            return "UK"
        return country.title()

    continent_map = {
        "North America": ["USA", "Canada", "Mexico"],
        "South America": [
            "Brazil", "Argentina", "Chile", "Peru", "Colombia", "Venezuela"
        ],
        "Europe": [
            "UK", "France", "Germany", "Italy", "Spain", "Netherlands",
            "Sweden", "Norway", "Poland", "Greece", "Ireland", "Portugal"
        ],
        "Asia": [
            "China", "Japan", "India", "South Korea", "Indonesia",
            "Thailand", "Singapore", "Malaysia", "Philippines", "Saudi Arabia"
        ],
        "Africa": [
            "Egypt", "South Africa", "Nigeria", "Kenya", "Morocco", "Ghana"
        ],
        "Oceania": ["Australia", "New Zealand"],
    }

    def country_to_continent(country):
        for continent, countries in continent_map.items():
            if country in countries:
                return continent
        return "Other"

    # Aggregate counts by continent
    continent_counts = {}
    for r in results:
        country = normalize_country(r["order__location__country"])
        if not country:
            continue
        continent = country_to_continent(country)
        continent_counts[continent] = continent_counts.get(continent, 0) + r["count"]

    # Approximate continent center coordinates
    continent_coords = {
        "North America": {"lat": 54.5260, "lng": -105.2551},
        "South America": {"lat": -8.7832, "lng": -55.4915},
        "Europe": {"lat": 54.5260, "lng": 15.2551},
        "Asia": {"lat": 34.0479, "lng": 100.6197},
        "Africa": {"lat": 1.9577, "lng": 17.8498},
        "Oceania": {"lat": -22.7359, "lng": 140.0188},
        "Other": {"lat": 0, "lng": 0},
    }

    data = []
    for continent, total in continent_counts.items():
        coords = continent_coords.get(continent, {"lat": 0, "lng": 0})
        data.append({
            "region": continent,
            "count": total,
            "lat": coords["lat"],
            "lng": coords["lng"],
        })

    return JsonResponse(data, safe=False)

@require_GET
def country_popularity_api(request):
    """Return total purchase counts aggregated by country."""
    results = (
        Item.objects.filter(order__location__isnull=False)
        .values("order__location__country")
        .annotate(count=Count("id"))
    )

    # Normalize country names
    def normalize_country(country):
        if not country:
            return ""
        c = country.strip().lower()
        aliases = {
            "us": "United States of America",
            "u.s.": "United States of America",
            "usa": "United States of America",
            "united states": "United States of America",
            "uk": "United Kingdom",
            "england": "United Kingdom",
            "great britain": "United Kingdom",
        }
        return aliases.get(c, country.title())

    aggregated = {}
    for r in results:
        country = normalize_country(r["order__location__country"])
        if country:
            aggregated[country] = aggregated.get(country, 0) + r["count"]

    data = [{"country": k, "count": v} for k, v in aggregated.items()]
    return JsonResponse(data, safe=False)

from movies.models import Movie

@require_GET
def trending_movies_api(request):
    """Return top 5 most purchased movies globally with one sample region (fixed normalization)."""
    items = Item.objects.filter(order__location__isnull=False).select_related(
        "movie", "order__location"
    )

    def normalize_country(country):
        if not country:
            return ""
        c = country.strip().lower()
        aliases = {
            "us": "United States of America",
            "u.s.": "United States of America",
            "usa": "United States of America",
            "united states": "United States of America",
            "united states of america": "United States of America",
            "america": "United States of America",
            "uk": "United Kingdom",
            "england": "United Kingdom",
            "great britain": "United Kingdom",
        }
        return aliases.get(c, country.title())

    # manually aggregate so normalization happens first
    movie_country_counts = {}
    for item in items:
        movie_name = item.movie.name
        country = normalize_country(item.order.location.country if item.order.location else None)
        movie_country_counts.setdefault(movie_name, {})
        movie_country_counts[movie_name][country] = movie_country_counts[movie_name].get(country, 0) + 1

    # build global totals and top region for each movie
    movie_totals = []
    for movie, regions in movie_country_counts.items():
        total = sum(regions.values())
        top_region = max(regions, key=regions.get)
        movie_totals.append({
            "movie": movie,
            "total": total,
            "region": top_region,
            "region_count": regions[top_region],
        })

    # top 5 globally
    movie_totals.sort(key=lambda x: x["total"], reverse=True)
    return JsonResponse(movie_totals[:5], safe=False)

