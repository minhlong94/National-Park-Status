# National-Park-Status

**Live page: https://minhlong94.github.io/National-Park-Status/**

A single-page board of current conditions for all 63 U.S. national parks, ranked by 2025 recreation visits.

## What it shows

- **Status per park**: open, partial closures, or closed, based on official NPS alerts.
- **Alert counts** for roads, trails, facilities and other issues. Click a park row to read every alert, the park's closure history and a 3-day forecast.
- **Weather now and today's forecast**, plus active National Weather Service warnings.
- **Seasonal road history**: year-by-year opening and closing dates for Tioga Road, Glacier Point Road, Going-to-the-Sun Road and Trail Ridge Road.
- **Closure history**: major full and partial closures from the last 5 years, including system-wide shutdowns.

Press **Refresh data** to load the live data.

## Data sources

| Data | Source |
| --- | --- |
| Park alerts and closures | [NPS API](https://www.nps.gov/subjects/developer/) (`developer.nps.gov`) |
| Current weather and forecast | [Open-Meteo](https://open-meteo.com/) |
| Weather warnings | [National Weather Service](https://www.weather.gov/documentation/services-web-api) (`api.weather.gov`) |
| Visitation | NPS Visitor Use Statistics, calendar year 2025 |

The page uses the shared NPS `DEMO_KEY` by default, which allows about 30 requests per hour per IP. You can paste a free personal key from [nps.gov/subjects/developer](https://www.nps.gov/subjects/developer/get-started.htm) under **NPS API key** on the page; it is stored only in your browser.

Park status is classified from alert text by keyword, so read the alert itself before you travel. The closure and seasonal road history is researched data built into the page and does not change on refresh.

## Running locally

Everything is in `index.html`, with no build step. Open it in a browser, or serve the folder:

```sh
python3 -m http.server 8000
```

then visit http://localhost:8000.

## Publishing

The site is served by GitHub Pages from the `gh-pages` branch.
