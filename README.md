# National-Park-Status

**Live page: https://minhlong94.github.io/National-Park-Status/**

This page shows the current conditions of all 63 U.S. national parks. The list sorts the parks by 2025 recreation visits.

## What the page shows

- **Status of each park**: open, partial closures or closed. The status comes from official NPS alerts.
- **Number of alerts** for roads, trails, facilities and other subjects. Click a park row to see all its alerts, its closure history and a 3-day forecast.
- **Current weather and the forecast for today.** The page also shows the active warnings from the National Weather Service.
- **Seasonal road history**: the opening and closing dates for Tioga Road, Glacier Point Road, Going-to-the-Sun Road and Trail Ridge Road. The page shows only the last 10 years, with the newest year first.
- **Closure history**: the major full and partial closures from the last 5 years. The list also shows shutdowns of all parks.

Click **Refresh data** to get the live data again.

## Data sources

| Data | Source |
| --- | --- |
| Park alerts and closures | [NPS API](https://www.nps.gov/subjects/developer/) (`developer.nps.gov`) |
| Current weather and forecast | [Open-Meteo](https://open-meteo.com/) |
| Weather warnings | [National Weather Service](https://www.weather.gov/documentation/services-web-api) (`api.weather.gov`) |
| Visits | NPS Visitor Use Statistics, calendar year 2025 |

If you do not give a key, the page uses the shared NPS `DEMO_KEY`. This key allows approximately 30 requests per hour from each IP address.

To use your own key:

1. Get a free key at [nps.gov/subjects/developer](https://www.nps.gov/subjects/developer/get-started.htm).
2. On the page, open **NPS API key**.
3. Paste the key and click **Save key**.

The page keeps your key only in your browser.

The page finds the type of each alert from keywords in the alert text. Read the alert text before you travel. The closure history and the road history are fixed data in the page. **Refresh data** does not change them.

## Run the page on your computer

All the code is in `index.html`. There is no build step. Open the file in a browser, or start a local server:

```sh
python3 -m http.server 8000
```

Then go to http://localhost:8000.

## Publish

GitHub Pages serves the site from the `gh-pages` branch. To publish a change, push it to `gh-pages`.

## Specification

The file [`spec.md`](spec.md) records all the requirements for this repository.
