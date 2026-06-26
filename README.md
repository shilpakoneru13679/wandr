Wandr

A personalized travel planning web app that builds curated itineraries based on your vibe, budget, and travel style — not generic destination guides.

Live demo: wandr-5zvc.onrender.com


What it does

Most travel apps give you the same list of tourist spots. Wandr asks who you are first.

You tell it where you're flying from, where you want to go (or let it help you figure that out), and answer a short survey about your pace, priorities, and vibe. It then generates a day-by-day itinerary written like a recommendation from a friend who knows the city — plus a tailored packing list.


Features

Two discovery flows


Know where you're going — type a city, pick your dates on a calendar, fill out the vibe survey, get your itinerary
Don't know where to go — choose domestic or international, then:

Domestic: throw a dart on an interactive map of your country — Gemini finds real destinations near where it lands
International: spin a 3D globe, stop it anywhere — Gemini finds real destinations in that region
Or skip the map and take a short survey instead





Itinerary generation


Day-by-day structure with morning, afternoon, and evening plans
Tailored to pace (slow and immersive vs. pack it in), priorities (food, wellness, nightlife, etc.), accommodation style, and niche level (tourist classics vs. hidden gems)
Aware of your home country — adjusts context for domestic vs. international trips
Date-aware — uses your actual travel dates to inform seasonal recommendations
One-word vibe prompt that shapes the entire output


Packing list


Generated alongside the itinerary, categorized by clothes, shoes, toiletries, tech, documents, and extras
Tailored to destination, vibe, and trip length
Click items to check them off as you pack


Revision flow


Don't like something? Describe what you want changed and Wandr regenerates with your feedback in mind



Tech stack

LayerTechBackendPython, FastAPITemplatingJinja2AIGoogle Gemini API (gemini-3.5-flash)MapsLeaflet.js (dart map), Canvas API (globe)DeploymentRender


How it's built

State management — no database or sessions. Each step forwards accumulated user data as hidden form fields to the next route. Simple, stateless, easy to debug.

Structured AI outputs — destination suggestions and packing lists are prompted to return strict JSON, parsed and rendered as interactive UI components rather than raw text. Itineraries use a consistent format that gets parsed client-side into styled day blocks.

Globe — built with the Canvas API. Regions are mapped to real lat/lng coordinates, projected onto a sphere with a custom renderer. Clicking stop drops a pin on the nearest named region and sends it to Gemini.

Dart map — built with Leaflet.js and OpenStreetMap tiles. Country bounding boxes auto-zoom to the right area. Clicking anywhere drops a dart and sends coordinates to Gemini, which returns real nearby destinations within that country.


Running locally

bashgit clone https://github.com/shilpakoneru13679/wandr.git
cd wandr
pip install -r requirements.txt

Add a .env file:

GEMINI_API_KEY=your_key_here

Run:

bashuvicorn main:app --reload

Open http://127.0.0.1:8000


Project structure

wandr/
├── main.py                  # All FastAPI routes
├── requirements.txt
├── .env                     # Not committed
└── templates/
    ├── index.html           # Landing page
    ├── trip_length.html     # Calendar date picker
    ├── vibe.html            # Vibe survey (shared)
    ├── unknown_choice.html  # Domestic vs international fork
    ├── unknown_survey.html  # Manual survey flow
    ├── globe.html           # Spinning globe (international)
    ├── dart.html            # Dart map (domestic)
    ├── suggestions.html     # Destination cards
    └── itinerary.html       # Final itinerary + packing list


Built by Shilpa Koneru
