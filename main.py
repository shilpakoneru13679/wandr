from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
from google import genai
from typing import List, Optional
import json

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

MODEL = "gemini-3.5-flash"


# ─── LANDING PAGE ───────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ─── FLOW A: KNOWN DESTINATION ──────────────────────────────────────────────────

@app.post("/flow/known", response_class=HTMLResponse)
async def known_destination(
    request: Request,
    city: str = Form(...),
    home_country: str = Form(...),
):
    return templates.TemplateResponse("trip_length.html", {
        "request": request,
        "city": city,
        "travel_type": "international",  # inferred; can be refined later
        "home_country": home_country,
    })


@app.post("/flow/vibe", response_class=HTMLResponse)
async def vibe_survey(
    request: Request,
    city: str = Form(...),
    duration: str = Form(...),
    budget: str = Form(...),
    travel_type: str = Form(...),
    home_country: str = Form(...),
    start_date: str = Form(default=""),
    end_date: str = Form(default=""),
):
    return templates.TemplateResponse("vibe.html", {
        "request": request,
        "city": city,
        "duration": duration,
        "budget": budget,
        "travel_type": travel_type,
        "home_country": home_country,
        "start_date": start_date,
        "end_date": end_date,
    })


# ─── FLOW B: UNKNOWN DESTINATION ────────────────────────────────────────────────

@app.post("/flow/unknown", response_class=HTMLResponse)
async def unknown_destination(
    request: Request,
    home_country: str = Form(...),
):
    return templates.TemplateResponse("unknown_choice.html", {
        "request": request,
        "home_country": home_country,
    })


@app.post("/flow/unknown-survey", response_class=HTMLResponse)
async def unknown_survey(
    request: Request,
    travel_type: str = Form(...),
    home_country: str = Form(...),
):
    return templates.TemplateResponse("unknown_survey.html", {
        "request": request,
        "travel_type": travel_type,
        "home_country": home_country,
    })


@app.post("/globe", response_class=HTMLResponse)
async def globe_page(
    request: Request,
    travel_type: str = Form(...),
    home_country: str = Form(...),
):
    return templates.TemplateResponse("globe.html", {
        "request": request,
        "travel_type": travel_type,
        "home_country": home_country,
    })


@app.post("/globe/pick", response_class=HTMLResponse)
async def globe_pick(
    request: Request,
    region: str = Form(...),
    lat: str = Form(...),
    lng: str = Form(...),
    travel_type: str = Form(...),
    home_country: str = Form(...),
):
    domestic_note = ""
    if travel_type == "domestic":
        domestic_note = f"IMPORTANT: Only suggest destinations within {home_country}."
    else:
        domestic_note = f"IMPORTANT: Only suggest destinations outside of {home_country}."

    prompt = f"""
The user spun a globe and it landed on the region: "{region}" (approximately lat {lat}, lng {lng}).

Suggest exactly 4 real travel destinations in or near that region.
{domestic_note}
Pick real cities or places actually in or very close to that geographic area.
Vary the popularity: include at least one well-known and one lesser-known option.

Return ONLY a JSON array with exactly 4 objects. No explanation, no markdown, no backticks.
Each object must have:
- "city": city or place name
- "country": country name
- "tagline": one punchy sentence (max 10 words) capturing its appeal
- "emoji": one relevant emoji

Example format:
[{{"city": "Porto", "country": "Portugal", "tagline": "Clifftop wine bars and crumbling beauty.", "emoji": "🍷"}}]
"""

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        destinations = json.loads(raw.strip())
    except Exception as e:
        destinations = [
            {"city": "Barcelona", "country": "Spain", "tagline": "Architecture, beaches, and late nights.", "emoji": "🏖️"},
            {"city": "Lisbon", "country": "Portugal", "tagline": "Sunny tiles, cheap wine, golden hour.", "emoji": "🌊"},
            {"city": "Rome", "country": "Italy", "tagline": "Every corner is a history lesson.", "emoji": "🏛️"},
            {"city": "Amsterdam", "country": "Netherlands", "tagline": "Canals, bikes, and effortless cool.", "emoji": "🚲"},
        ]

    return templates.TemplateResponse("suggestions.html", {
        "request": request,
        "destinations": destinations,
        "duration": "3 days",
        "budget": "mid-range",
        "travel_type": travel_type,
        "home_country": home_country,
    })




@app.post("/dart", response_class=HTMLResponse)
async def dart_page(
    request: Request,
    home_country: str = Form(...),
    travel_type: str = Form(default="domestic"),
):
    """Domestic: show the dart map."""
    return templates.TemplateResponse("dart.html", {
        "request": request,
        "home_country": home_country,
        "travel_type": travel_type,
    })


@app.post("/dart/pick", response_class=HTMLResponse)
async def dart_pick(
    request: Request,
    lat: str = Form(...),
    lng: str = Form(...),
    place_name: str = Form(...),
    home_country: str = Form(...),
    travel_type: str = Form(default="domestic"),
):
    """User threw a dart - find 3 destinations near that location within the country."""
    prompt = f"""
The user is planning a domestic trip within {home_country}.
They threw a dart on a map and it landed at coordinates: lat={lat}, lng={lng}.

Suggest exactly 3 real destinations within {home_country} that are near or in the same general region as those coordinates.
Include a mix: at least one well-known area and one more local or underrated spot.

Return ONLY a JSON array with exactly 3 objects. No explanation, no markdown, no backticks.
Each object must have:
- "city": city or region name
- "country": "{home_country}"
- "tagline": one punchy sentence (max 10 words) capturing its appeal
- "emoji": one relevant emoji

Example format:
[{{"city": "Asheville", "country": "United States", "tagline": "Mountain town with craft beer and live music.", "emoji": "🏔️"}}]
"""
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        destinations = json.loads(raw.strip())
    except Exception as e:
        destinations = [
            {"city": "Nearby City 1", "country": home_country, "tagline": "A great local destination.", "emoji": "📍"},
            {"city": "Nearby City 2", "country": home_country, "tagline": "Worth the drive.", "emoji": "🗺️"},
            {"city": "Nearby City 3", "country": home_country, "tagline": "Hidden gem close by.", "emoji": "✨"},
        ]

    return templates.TemplateResponse("suggestions.html", {
        "request": request,
        "destinations": destinations,
        "duration": "3 days",
        "budget": "mid-range",
        "travel_type": "domestic",
        "home_country": home_country,
    })

@app.post("/destinations", response_class=HTMLResponse)
async def suggest_destinations(
    request: Request,
    weather: str = Form(...),
    duration: str = Form(...),
    budget: str = Form(...),
    vibe_hint: str = Form(...),
    popularity: str = Form(...),
    home_country: str = Form(...),
    travel_type: str = Form(...),
):
    domestic_note = ""
    if travel_type == "domestic":
        domestic_note = f"IMPORTANT: Only suggest destinations within {home_country}."
    else:
        domestic_note = f"IMPORTANT: Only suggest destinations outside of {home_country}."

    popularity_note = {
        "well-known": "Suggest popular, well-known destinations that most travellers have heard of.",
        "mix": "Mix of one or two well-known spots and one or two lesser-known gems.",
        "niche": "Suggest off-the-beaten-path, niche, or underrated destinations most tourists skip.",
    }.get(popularity, "")

    prompt = f"""
Suggest exactly 4 travel destinations for someone with these preferences:
- Preferred weather: {weather}
- Trip length: {duration}
- Budget: {budget}
- Vibe they're going for: {vibe_hint}
- Popularity preference: {popularity}

{domestic_note}
{popularity_note}

Return ONLY a JSON array with exactly 4 objects. No explanation, no markdown, no backticks.
Each object must have:
- "city": city or place name
- "country": country name
- "tagline": one punchy sentence (max 10 words) capturing why it fits
- "emoji": one relevant emoji

Example format:
[{{"city": "Lisbon", "country": "Portugal", "tagline": "Sunny tiles, cheap wine, endless golden hour.", "emoji": "🌊"}}]
"""

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        destinations = json.loads(raw.strip())
    except Exception as e:
        destinations = [
            {"city": "Barcelona", "country": "Spain", "tagline": "Architecture, beaches, and late nights.", "emoji": "🏖️"},
            {"city": "Tokyo", "country": "Japan", "tagline": "Futuristic chaos meets ancient quiet.", "emoji": "🏯"},
            {"city": "Cape Town", "country": "South Africa", "tagline": "Mountains, ocean, and golden sunsets.", "emoji": "🌄"},
            {"city": "Medellín", "country": "Colombia", "tagline": "Eternal spring, art, and energy.", "emoji": "🌸"},
        ]

    return templates.TemplateResponse("suggestions.html", {
        "request": request,
        "destinations": destinations,
        "duration": duration,
        "budget": budget,
        "travel_type": travel_type,
        "home_country": home_country,
    })


@app.post("/flow/vibe-from-suggestion", response_class=HTMLResponse)
async def vibe_from_suggestion(
    request: Request,
    city: str = Form(...),
    duration: str = Form(...),
    budget: str = Form(...),
    travel_type: str = Form(...),
    home_country: str = Form(...),
):
    return templates.TemplateResponse("vibe.html", {
        "request": request,
        "city": city,
        "duration": duration,
        "budget": budget,
        "travel_type": travel_type,
        "home_country": home_country,
        "start_date": "",
        "end_date": "",
    })


# ─── FINAL ITINERARY GENERATION ─────────────────────────────────────────────────

def build_itinerary_prompt(city, duration, budget, pace, priorities, accommodation, one_word, travel_type, home_country, niche_level, edit_note=None, start_date="", end_date=""):
    niche_instruction = {
        "well-known": "Focus on the iconic, must-see spots: the classics that earned their reputation.",
        "mix": "Mix well-known highlights with a few lesser-known local spots.",
        "niche": "Prioritize hidden gems, local haunts, and underrated spots. Avoid tourist traps entirely.",
    }.get(niche_level, "")

    date_context = ""
    if start_date and end_date:
        date_context = f" Travel dates: {start_date} to {end_date}."
    travel_context = ""
    if travel_type == "domestic":
        travel_context = f"The traveler is from {home_country} and this is a domestic trip: they may already know some basics, so skip obvious cultural orientation.{date_context}"
    else:
        travel_context = f"The traveler is from {home_country} visiting abroad: include practical tips relevant to an international visitor.{date_context}"

    edit_section = ""
    if edit_note:
        edit_section = f"\n\nThe traveler reviewed a previous draft and requested these changes: \"{edit_note}\"\nRevise the itinerary to reflect this feedback specifically."

    return f"""
You are a curated travel guide writer. Create a {duration}-day itinerary for {city}.

Traveler profile:
- Budget level: {budget}
- Trip pace: {pace}
- Top priorities: {priorities}
- Accommodation style: {accommodation}
- The vibe in one word: {one_word}
- Place discovery style: {niche_level}: {niche_instruction}
- Travel context: {travel_context}
{edit_section}

FORMAT RULES (follow exactly):
- Start with a 2-sentence intro that captures the spirit of this specific trip
- For each day, use this format:
  DAY [N]: [a short evocative title for the day]
  Morning: [activity + why it fits this traveler]
  Afternoon: [activity + specific tip]
  Evening: [activity + vibe note]
  Local tip: [one insider detail]

- End with a "Don't Miss" section: 3 bullet points
- Keep language warm, specific, and editorial: like a friend who knows the city
- Avoid generic tourist advice. Be specific with names, neighborhoods, and details.
- Total length: around 400-500 words
"""


def build_packing_prompt(city, duration, budget, priorities, one_word, travel_type):
    return f"""
Create a practical packing list for a {duration}-day trip to {city}.
Trip context: budget={budget}, priorities={priorities}, vibe={one_word}, type={travel_type}.

Return ONLY a JSON object with these exact keys. No markdown, no backticks.
Each key maps to an array of short item strings (max 5 words each).
Keep each list to 4-7 items. Tailor to the destination and vibe.

{{"Clothes": ["..."], "Shoes": ["..."], "Toiletries": ["..."], "Tech": ["..."], "Documents": ["..."], "Extras": ["..."]}}
"""


def generate_packing_list(city, duration, budget, priorities, one_word, travel_type):
    try:
        prompt = build_packing_prompt(city, duration, budget, priorities, one_word, travel_type)
        response = client.models.generate_content(model=MODEL, contents=prompt)
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception:
        return {
            "Clothes": ["Comfortable walking shoes", "Layers for evenings", "One nicer outfit"],
            "Toiletries": ["Sunscreen", "Travel-size essentials"],
            "Tech": ["Phone charger", "Power bank", "Adapter if needed"],
            "Documents": ["Passport / ID", "Booking confirmations", "Travel insurance"],
            "Extras": ["Reusable water bottle", "Day bag / tote"],
        }


@app.post("/generate", response_class=HTMLResponse)
async def generate_itinerary(
    request: Request,
    city: str = Form(...),
    duration: str = Form(...),
    budget: str = Form(...),
    pace: str = Form(...),
    priorities: List[str] = Form(...),
    accommodation: str = Form(...),
    one_word: str = Form(...),
    travel_type: str = Form(...),
    home_country: str = Form(...),
    niche_level: str = Form(...),
    start_date: str = Form(default=""),
    end_date: str = Form(default=""),
):
    priorities_str = ", ".join(priorities)
    prompt = build_itinerary_prompt(city, duration, budget, pace, priorities_str, accommodation, one_word, travel_type, home_country, niche_level, start_date=start_date, end_date=end_date)

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        itinerary = response.text
    except Exception as e:
        itinerary = f"Error generating itinerary: {str(e)}"

    packing_list = generate_packing_list(city, duration, budget, priorities_str, one_word, travel_type)

    return templates.TemplateResponse("itinerary.html", {
        "request": request,
        "city": city,
        "duration": duration,
        "start_date": start_date,
        "end_date": end_date,
        "one_word": one_word,
        "itinerary": itinerary,
        "packing_list": packing_list,
        "budget": budget,
        "pace": pace,
        "priorities": priorities_str,
        "accommodation": accommodation,
        "travel_type": travel_type,
        "home_country": home_country,
        "niche_level": niche_level,
    })


@app.post("/regenerate", response_class=HTMLResponse)
async def regenerate_itinerary(
    request: Request,
    city: str = Form(...),
    duration: str = Form(...),
    budget: str = Form(...),
    pace: str = Form(...),
    priorities: str = Form(...),
    accommodation: str = Form(...),
    one_word: str = Form(...),
    travel_type: str = Form(...),
    home_country: str = Form(...),
    niche_level: str = Form(...),
    edit_note: str = Form(...),
):
    prompt = build_itinerary_prompt(city, duration, budget, pace, priorities, accommodation, one_word, travel_type, home_country, niche_level, edit_note=edit_note)

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        itinerary = response.text
    except Exception as e:
        itinerary = f"Error generating itinerary: {str(e)}"

    packing_list = generate_packing_list(city, duration, budget, priorities, one_word, travel_type)

    return templates.TemplateResponse("itinerary.html", {
        "request": request,
        "city": city,
        "duration": duration,
        "one_word": one_word,
        "itinerary": itinerary,
        "packing_list": packing_list,
        "budget": budget,
        "pace": pace,
        "priorities": priorities,
        "accommodation": accommodation,
        "travel_type": travel_type,
        "home_country": home_country,
        "niche_level": niche_level,
    })