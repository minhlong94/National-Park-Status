# National-Park-Status

**Live page: https://minhlong94.github.io/National-Park-Status/**

This page shows the current conditions of all 63 U.S. national parks. The list sorts the parks by 2025 recreation visits.

## What the page shows

- **Status of each park**: open, partial closures or closed. The status comes from official NPS alerts.
- **Number of alerts** for roads, trails, facilities and other subjects. Click a park row to see all its alerts, its closure history and a 3-day forecast.
- **Current weather and the forecast for today.** The page also shows the active warnings from the National Weather Service.
- **Seasonal road history**: the opening and closing dates for Tioga Road, Glacier Point Road, Going-to-the-Sun Road and Trail Ridge Road. The page shows only the last 10 years, with the newest year first.
- **Visits and climate by month**: click a park to see four charts with the same months:
  - recreation visits in each month of the last 3 calendar years, with one color for each year
  - the average daily low and high temperature
  - the average monthly rain
  - the average monthly snow

  Put the pointer on a month to see all the values for that month. A table shows the same values.
- **Fall color**: the usual dates when the leaves change, from satellite data, and reports of colored leaves near the park in this season.
- **Best time to visit**: a score from 0 to 100 for each month. It uses the weather, the number of visitors, rain, snow and fall color. The table shows the best months, and the park details show the reasons and a score strip.
- **Closure history**: the major full and partial closures from the last 5 years. The list also shows shutdowns of all parks.

The table shows 10 parks on each page. The first page shows the 10 most visited parks.

Click **Refresh data** to get the current park statuses and weather again. The monthly data and the fall color data are stored in files and do not refresh with this button.

## Data sources

| Data | Source |
| --- | --- |
| Park alerts and closures | [NPS API](https://www.nps.gov/subjects/developer/) (`developer.nps.gov`) |
| Current weather and forecast | [Open-Meteo](https://open-meteo.com/) |
| Weather warnings | [National Weather Service](https://www.weather.gov/documentation/services-web-api) (`api.weather.gov`) |
| Visits (ranking) | NPS Visitor Use Statistics, calendar year 2025 |
| Monthly visits | [NPS Visitor Use Statistics](https://irma.nps.gov/Stats/) (`irmaservices.nps.gov`) |
| Monthly climate | [Open-Meteo historical weather](https://open-meteo.com/en/docs/historical-weather-api) (`archive-api.open-meteo.com`) |
| Fall color, usual timing | [NASA MODIS land surface phenology (MCD12Q2)](https://lpdaac.usgs.gov/products/mcd12q2v061/), from the [ORNL DAAC MODIS web service](https://modis.ornl.gov/data/modis_webservice.html) |
| Fall color, this season | [USA National Phenology Network](https://www.usanpn.org/) (`services.usanpn.org`) |

If you do not give a key, the page uses the shared NPS `DEMO_KEY`. This key allows approximately 30 requests per hour from each IP address.

To use your own key:

1. Get a free key at [nps.gov/subjects/developer](https://www.nps.gov/subjects/developer/get-started.htm).
2. On the page, open **NPS API key**.
3. Paste the key and click **Save key**.

The page keeps your key only in your browser.

The page finds the type of each alert from keywords in the alert text. Read the alert text before you travel. The closure history and the road history are fixed data in the page. **Refresh data** does not change them.

## Monthly data

The monthly visits and weather data is in a separate file, `data/park-history.js`. The file keeps one value for each month from January 2023 to the last month with data. Old months do not change.

The script `scripts/fetch_history.py` adds only new months:

1. The script requests a month only after the month ends. For example, it requests October from November 1.
2. The script requests the new month for the first park only.
3. If the first park has no data for that month, the script stops. It does not request data for the other parks, and the file does not change.
4. If the first park has data, the script gets the month for all parks and adds it to the file.

The page shows the visits for the last 3 calendar years in the file. The weather values are the averages of each calendar month over the last 36 months.

The workflow `.github/workflows/update-data.yml` runs the script and commits the file. The workflow runs:

- each Monday
- when the script or the workflow changes
- when you start it from the **Actions** tab

## Fall foliage data

The script `scripts/fetch_foliage.py` keeps two files:

- `data/foliage.js`: the usual timing of the fall color. For each park and year, it keeps the day when the greenness starts to drop, the middle of the leaf change and the day when the leaves are off. NASA publishes one year at a time, 1 to 2 years late. The script adds only new years, and it checks the first park first.
- `data/foliage-now.js`: the reports of colored and falling leaves within 50 km of each park in the last 14 days. The script gets these reports only from Aug 15 to Dec 15.

The workflow `.github/workflows/update-foliage.yml` runs the script each Monday.

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
