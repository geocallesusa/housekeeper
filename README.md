# CasaCerca prototype

A small React + Python prototype for finding housekeepers in San Salvador. It uses no Python packages, build step, API key, or database.

## Run it

1. Open a terminal in this folder.
2. Run `python server.py` (use `py server.py` on some Windows installations).
3. Open [http://localhost:8000](http://localhost:8000).

The interface uses React and Leaflet from public CDNs. The map uses OpenStreetMap tiles, so an internet connection is needed to load the map and sample profile images.

## What is included

- Ten hardcoded housekeeping providers distributed around San Salvador.
- An interactive, Airbnb-style map with photo-and-price map markers plus detailed popups.
- Date and time search. It shows every provider initially; after searching it filters availability by the selected weekday and time range.
- Provider cards showing service area, rating, rate, offered work, and weekly/time availability.

Provider data is all in `server.py` and can be replaced with a database later.
