# National-Park-Status

**Live page: https://minhlong94.github.io/National-Park-Status/**

This page shows the current conditions of all 63 U.S. national parks. The list sorts the parks by 2025 recreation visits.

## What the page shows

- **Status of each park**: open, partial closures or closed. The status comes from official NPS alerts.
- **Number of alerts** for roads, trails, facilities and other subjects. Click a park row to see all its alerts, its closure history and a 3-day forecast.
- **Current weather and the forecast for today.** The page also shows the active warnings from the National Weather Service.
- **Seasonal road history**: the opening and closing dates for Tioga Road, Glacier Point Road, Going-to-the-Sun Road and Trail Ridge Road. The page shows only the last 10 years, with the newest year first.
- **Visits and climate by month**: click a park to see four charts with the same months:
  - recreation visits in each month of the last 3 complete years, with one color for each year
  - the average daily low and high temperature
  - the average monthly rain
  - the average monthly snow

  Put the pointer on a month to see all the values for that month. A table shows the same values.
- **Closure history**: the major full and partial closures from the last 5 years. The list also shows shutdowns of all parks.

Click **Refresh data** to get the live data again.

## Data sources

| Data | Source |
| --- | --- |
| Park alerts and closures | [NPS API](https://www.nps.gov/subjects/developer/) (`developer.nps.gov`) |
| Current weather and forecast | [Open-Meteo](https://open-meteo.com/) |
| Weather warnings | [National Weather Service](https://www.weather.gov/documentation/services-web-api) (`api.weather.gov`) |
| Visits (ranking) | NPS Visitor Use Statistics, calendar year 2025 |
| Monthly visits | [NPS Visitor Use Statistics](https://irma.nps.gov/Stats/) (`irmaservices.nps.gov`) |
| Monthly climate | [Open-Meteo historical weather](https://open-meteo.com/en/docs/historical-weather-api) (`archive-api.open-meteo.com`) |

If you do not give a key, the page uses the shared NPS `DEMO_KEY`. This key allows approximately 30 requests per hour from each IP address.

To use your own key:

1. Get a free key at [nps.gov/subjects/developer](https://www.nps.gov/subjects/developer/get-started.htm).
2. On the page, open **NPS API key**.
3. Paste the key and click **Save key**.

The page keeps your key only in your browser.

The page finds the type of each alert from keywords in the alert text. Read the alert text before you travel. The closure history and the road history are fixed data in the page. **Refresh data** does not change them.

## Monthly data

The monthly visits and climate data is in `data/park-history.js`. The script `scripts/fetch_history.py` makes this file. It uses the last 3 complete calendar years.

The workflow `.github/workflows/update-data.yml` runs the script and commits the file. The workflow runs:

- on day 3 of each month
- when the script or the workflow changes
- when you start it from the **Actions** tab

## Run the page on your computer

All the page code is in `index.html`. There is no build step. Start a local server, because the page loads `data/park-history.js` when you open a park:

```sh
python3 -m http.server 8000
```

Then go to http://localhost:8000.

## Publish

GitHub Pages serves the site from the `gh-pages` branch. To publish a change, push it to `gh-pages`.

## Specification

The file [`spec.md`](spec.md) records all the requirements for this repository.
