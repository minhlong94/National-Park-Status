# Specification: National Park Status

This file records all the requirements that the owner gave for this repository.
Add each new instruction from the owner to the "Requirements" list as a new item.
Do not remove an item. If a new instruction replaces an old one, write the new item and mark the old item as replaced.

Text rule: Write this file, the README and the page text in ASD-STE100 Simplified Technical English (see R5).

## Product

The product is one web page, `index.html`. The page shows the current conditions of all 63 U.S. national parks.

- Live page: https://minhlong94.github.io/National-Park-Status/
- Source of the first version: the "Park conditions board" artifact (https://claude.ai/artifact/Ko71Jdm9JFZkz49sRf7GYt).

## Requirements

### R0. Original instruction: park status page with weather and refresh

Original text from the owner:

> Pull me every road trail park status of every national park, build a html page on it, along with weather conditions, sorted by most visited parks top 20 only, and make a refresh button that pull new data on demand

Requirements:

- Get the status of the roads, trails and parks for each national park.
- Make an HTML page that shows this status.
- Show the weather conditions for each park.
- Sort the parks by the number of visits, with the most visited park first.
- Show only the 20 most visited parks.
- Add a "Refresh" button. When the reader clicks it, the page gets new data.
- Status: done, with a change from R13. The page shows all 63 parks in pages of 10. The first page shows the 10 most visited parks.

### R1. Keep the Park conditions board in the repository

- Get the HTML artifact about national park status.
- Keep the page in the repository as `index.html`.
- Status: done.

### R2. Publish the page on GitHub Pages

- Publish the page on GitHub Pages.
- GitHub Pages serves the site from the `gh-pages` branch.
- After each change to the page, push the change to `gh-pages`.
- Status: done.

### R3. Write the README with the page URL

- Write a README for the repository.
- The README must contain the URL of the live page.
- Status: done.

### R4. Keep this specification

- Put all the owner's requests in `spec.md`.
- Add each future instruction from the owner to `spec.md`.
- Commit `spec.md` to the repository.
- Status: done. Continues for each new instruction.

### R5. Use ASD-STE100 Simplified Technical English

- Write the text in ASD-STE100 Simplified Technical English.
- Reference: https://github.com/danyuchn/asd-ste100-skill
- The rule applies to the page text, the README and this file.
- Use these rules:
  - Use the active voice.
  - Write a maximum of 20 words in an instruction and 25 words in a description.
  - Do not use semicolons.
  - Do not use phrasal verbs.
  - Use simple tenses.
  - Use a verb for an action, not a noun.
  - Use one word for one meaning.
- Status: done.

### R6. Seasonal road history: last 10 years, newest first

- The seasonal road history must show only the last 10 calendar years.
- The table, the chart and the list of short closures must show the dates in descending order (newest first).
- The statistics (for example, average opening) use only the 10 years that the page shows.
- Status: done.

### R7. Show the GitHub link on the page

- The page must show a link to the GitHub repository: https://github.com/minhlong94/National-Park-Status
- The link is in the footer of the page.
- Status: done.

### R8. Merge the work into `main`

- Open a pull request from the work branch to `main`.
- Merge the pull request.
- Status: done.

### R9. Monthly visits and climate chart for each park

Original text from the owner:

> For each park, add an interactive graph detailing visitors by month when clicked in the past 3 years, vertical bar diff color, along with avg temp low-high, snow, and rain, according to historical data, that can have its separate or same graph depending on your choice so that it works best to the readers

Requirements:

- When the reader clicks a park, show an interactive chart of the visits in each month.
- Show the last 3 calendar years in the data file (see R11).
- Use vertical bars. Give each year a different color.
- Also show these historical monthly values:
  - the average low and high temperature
  - snow
  - rain
- Design choice: The page shows four separate charts with the same months (January to December). Each chart has one y-axis. When the reader points to a month in one chart, all charts show that month and one tooltip shows all the values for that month.
- A table view shows the same values.
- Data sources:
  - Visits: NPS Visitor Use Statistics (irmaservices.nps.gov).
  - Weather: Open-Meteo historical weather archive (archive-api.open-meteo.com). The page shows the average of each calendar month over the last 36 months.
- A GitHub Actions workflow gets the data and saves it in `data/park-history.js`. It runs each Monday (see R11). When it runs on `main`, it also pushes the data to `gh-pages`.
- Each year has a fixed color. The colors pass the palette check for color vision deficiency.
- The reader can click a year in the legend to show or hide that year.
- If almost no snow falls in a park, the page shows a short text instead of the snow chart.
- On small screens, the charts fit the visible width.
- Status: done.

### R10. Use timeouts in the data workflow

Original text from the owner:

> Workflow failed. Try again, and make sure to use timeouts

Requirements:

- Each network request has a timeout of 30 seconds for each step (connect, TLS handshake and each read).
- The script tries each request a maximum of 3 times.
- The script stops after 10 minutes.
- If 3 parks fail one after the other, the script stops the requests to that host.
- The "Get the data" step stops after 15 minutes. The job stops after 20 minutes.
- If one source fails, the workflow keeps the good data from the other source. The run then shows a failure.
- Status: done.

### R11. Store the monthly data and add only new months

Original text from the owner:

> Monthly data doesn't change much. Save it in a separate file so that it doesn't need constant refresh. You only need to refresh if future data comes. For example for now store it up to Sep 2026 (if available), refresh only if it's Nov, but attempt to get data for the first park and halt getting data for all parks if the first park returns null data for Oct

Requirements:

- Keep the monthly data in a separate file: `data/park-history.js`.
- The file keeps one value for each month, from January 2023 to the last month with data (for example, September 2026 if NPS published it).
- Old months do not change. The script does not get them again.
- The script requests a month only after the month ends. For example, it requests October 2026 from November 1, 2026.
- The script first requests the new month for the first park only. If the first park has no visits or no complete weather for that month, the script stops. It does not request data for the other parks.
- If the first park has data, the script gets the month for all parks and adds it.
- The page shows the visits for the last 3 calendar years in the file. The weather values are the averages of each calendar month over the last 36 months.
- The workflow runs each Monday. Most runs make no request or two requests.
- Status: done.

### R12. Fall foliage data

Original text from the owner:

> Can you also get fall foilage data?

The owner chose "Both" for the type of data.

Requirements:

- **Usual timing.** For each park, show when the fall color usually happens:
  - when the greenness starts to drop
  - the middle of the leaf change
  - when the leaves are off
- Source: NASA MODIS land surface phenology (MCD12Q2), from the ORNL DAAC MODIS web service. Each value is the median of the pixels in a 3 km box at the park point. The page shows the average of the last 5 years with data.
- NASA publishes one year at a time, 1 to 2 years late. The file `data/foliage.js` keeps each year. Old years do not change. The script first checks the first park for a new year. If the first park has no data, the script stops.
- If a park has no clear fall color change, the page tells the reader. Examples: deserts, tropical parks and evergreen parks. A clear change has all of these:
  - the park is north of 24° N
  - there are at least 3 years of data
  - the middle of the greenness drop is from Aug 25 to Nov 30
  - the change in greenness (EVI amplitude) is 0.15 or more
- The satellite data measures greenness, not leaf color. The page says that leaf color is usually best from the middle of the greenness drop to the day most leaves are off.
- The page links to the ExploreFall fall foliage map. Its maps and forecasts are the work of another company, with no public data service. The page does not copy them.
- If no park has this-season reports (the reports are not entered yet), the page does not show the this-season line.
- **This season.** Show the reports of "Colored leaves" and "Falling leaves" within 50 km of each park in the last 14 days.
- Source: USA National Phenology Network (USA-NPN). One request gets the reports for all parks. The file is `data/foliage-now.js`.
- The request must not send the bounding box parameters. With them, the service returns no reports. The script finds the reports near each park by distance.
- The script gets the reports for this season only from Aug 15 to Dec 15.
- The page shows a fall color strip with the same months as the other charts, and a short text.
- The workflow `.github/workflows/update-foliage.yml` runs each Monday. All data workflows use one queue, so two runs never push at the same time.
- Status: done.

### R12a. ExploreFall

Original text from the owner:

> Cant you get foliage map from https://www.explorefall.com/?

- ExploreFall has no public data service. Its maps and forecasts are its own work. The page does not copy them. Each park with a clear fall color change has a link to the ExploreFall map.
- Status: done.

### R13. Show all parks in pages of 10

Original text from the owner:

> Also do not need to show all 63 parks. Just show the top 20 and make it pages

Then the owner made it more exact:

> No what I mean is show all parks but only show top 10 first and make the rest in pages

The owner also said:

> What I want to refresh is just current park statuses and weather conditions.

The owner chose to keep the weekly refresh of the this-season leaf reports (R12).

Requirements:

- The park table shows all 63 parks.
- Each page shows 10 parks. The first page shows the 10 most visited parks.
- The page has "Previous" and "Next" buttons and a button for each page.
- A new search, filter or sort goes back to page 1.
- The totals at the top count all parks, not only the parks on the page.
- "Refresh data" refreshes only the current park statuses and weather conditions. The stored data (monthly visits, monthly weather, usual fall color timing) does not refresh. The scripts only add new months or years.
- Status: done.

### R14. Publish each request with a pull request

Original text from the owner:

> Make a PR to publish it. Do after completing each request unless explicitly told not to do so

Requirements:

- After each request is complete, open a pull request from the work branch to `main` and merge it.
- After the merge, push `main` to `gh-pages`, so the live page shows the change.
- Do not do this if the owner says not to.
- Status: done. Continues for each request.

### R15. Best time to visit each park

Original text from the owner:

> Can you find the best time to visit each parks?

Requirements:

- For each park and each month, calculate a visit score from 0 to 100. Use only the stored data:
  - weather comfort (45%): the average daily high. 60–80°F is best.
  - fewer visitors (25%): the visits of the month compared with the busiest month.
  - little rain (15%) and little snow (15%).
  - fall color: add 10 in the months when leaf color is usually best.
- If a month has less than 5% of the visits of the busiest month, access is probably limited. Its score is cut to 30%.
- The best months are a maximum of 2 windows of neighbor months, with a maximum of 3 months in each window, near the top score.
- The park table has a "Best time" column. The sort list has "Best to visit this month".
- The park details show the best months, the reasons, the months with limited access, the usual open dates of the seasonal road (if the park has one) and a score strip with the same months as the charts.
- The page tells the reader that the score does not include events, wildlife seasons or road openings.
- Status: changed by R21. The page does not show the score now.

### R16. Park details layout

Original text from the owner:

> Ok add it to the bottom of each park click like this. Additionally put Closure History as a column so that it does not overflow the opening section

Requirements:

- The "Best time to visit" block is at the bottom of the park details. (R21 removes this block.)
- The park details have three columns: alerts, 3-day forecast and closure history. On a narrow screen, the columns go one below the other.
- Status: done.

### R17. Fall color map from NASA data

Original text from the owner (the answer to "ExploreFall embed or a map from the NASA data?"):

> NASA data

Requirements:

- Show a map of the United States with one dot for each park. The map uses the stored NASA data (`data/foliage.js`). It does not need new data.
- A date slider (Aug 1 to Dec 15) starts at today. For the date, each dot shows the usual state of the park:
  - leaf color usually best (large fall-color dot)
  - greenness starts to drop (medium green dot)
  - not in the fall color period (small gray dot)
  - no clear fall color (hollow dot)
- The dots have different sizes, so the reader does not need the color to see the state. The colors pass the palette check in light and dark mode.
- A list next to the map shows the parks in each state on the date. A table shows the usual dates of all parks.
- Point to a dot to see its dates. Click a dot or a list item to open the park in the table.
- The base map is `us-atlas` (Albers USA, with Alaska and Hawaii). The libraries `d3-geo` and `topojson-client` load from the jsDelivr CDN. If they do not load, the list and the table still work.
- American Samoa and the Virgin Islands are not on the map. They have no clear fall color.
- Status: done.

### R18. Fix the this-season leaf reports

Original text from the owner:

> Yes fix it

Requirements:

- The USA-NPN request returned 0 reports, also for 2025. A test of 9 request formats showed the cause: the bounding box parameters. Without them, one week in October 2025 has 9,634 reports of colored and falling leaves.
- Remove the bounding box from the request.
- Status: done.

### R19. Fix the park details layout

Original text from the owner (with a screenshot of a cut-off closure history column):

> Broken. Maybe 3 days forecast can be vertical?

Requirements:

- When the park table scrolls sideways (a window narrower than the table), the park details use the visible width and stay in view. No column is cut off.
- The columns (alerts, forecast, closure history) go to the next line when there is not enough width.
- The 3-day forecast shows one row for each day: day, high and low, weather, precipitation.
- Links in the park details use the link color, so that they are easy to read in dark mode.
- Status: done.

### R20. Regional fall color map

Original text from the owner:

> I dont need park-specific details. Regional is fine to me, e.g., like one from explorefall

Requirements:

- The fall color map shows regions, not parks. The color fills the whole country, like the ExploreFall map. The park dots and the park list are removed from the map.
- Data: NASA MODIS land surface phenology (MCD12Q2) on a grid:
  - 438 points: every 1.5° in the lower 48 states, and every 2° of latitude and 4° of longitude in Alaska (`data/foliage-grid-cells.json`).
  - For each point: the median day in a 21 km box when greenness starts to drop, the middle of the drop and leaves down, averaged over the last 5 NASA years (`data/foliage-grid.js`).
- The script `scripts/fetch_foliage_grid.py` collects the grid in about 1,300 requests. It stops after 45 minutes, saves its progress, and the next run continues.
- The data changes once a year. When the grid is complete, the script checks for a new NASA year at one point in the Great Smoky Mountains. If that point has no data for the new year, the script stops.
- The page blends the 4 nearest grid points for each pixel and shows a stage for the chosen date:
  - no change yet
  - starting
  - partial
  - near peak
  - peak color (from the middle of the drop to 60% of the way to leaves down)
  - past peak
  - leaves down
  - no clear fall color
- A list shows the states at peak color, near peak and past peak on the date. A table shows the usual dates for each state.
- The fall color text in each park's details does not change.
- Status: reverted by R22. The grid collection took too long.

### R21. Best time to visit: banner and filter, no score

Original text from the owner:

> I do not need the best time to visit score. I want it as a banner below the park's name that encourages users to visit. Also I want the Best time to visit filter, and it should have best time to visit this month, or filter selected months

Requirements:

- The page does not show the visit score. It removes the score strip, the score in the tooltip, the score column and the "Best time to visit" block in the park details. The page still calculates the best months as in R15.
- Under the name of each park in the table, a banner shows the best months:
  - If this month is one of them: "Now is a great time to visit!" and the best months.
  - If not: "Best time to visit:" and the best months.
  - The reasons show when the reader puts the pointer on the banner.
- The "Best time" column and the "Best to visit this month" sort are removed.
- A "Best time to visit" filter has three choices:
  - Any time
  - This month
  - Choose months: a button for each month. The reader can select one or more months.
- The filter keeps the parks whose best months include a selected month. It works together with the search and the other filters.
- Status: done.

### R22. Stop the grid, go back to the park map, use the grid method for parks without data

Original text from the owner:

> The points grid run too long - stop it and revert back to the original. For parks without data, use this grid method

Requirements:

- Stop the grid collection. Revert the regional map (R20) and the grid script. The fall color map shows the park dots again (R17).
- Keep the best time banner and filter (R21).
- For parks without fall color data (fewer than 3 years with data in the 3 km box), use the grid method: get all years again with a 21 km box and use the pixels that have a growing cycle. In October 2026 this is 18 parks and 72 requests.
- Each park gets the wide box only once. The file `data/foliage.js` lists these parks in `wide`. New NASA years use the wide box for them.
- The park details tell the reader when a park uses the 21 km box.
- Status: done.

### R23. Short numbers for visits

Original text from the owner:

> Shorten the visits count and big numbers to 400K or 4M. No need to show exact numbers

Requirements:

- Show big numbers in a short form, not exact. Examples: 11.5M, 4.8M, 4M, 400K, 15K, 7.8K.
  - From 1 million: millions with one decimal (no decimal if it is 0, or from 100 million).
  - From 10,000: whole thousands.
  - From 1,000: thousands with one decimal.
  - Numbers under 1,000 do not change.
- This applies to the "2025 visits" column, the visits in the monthly tooltip, the monthly values table and the chart axis.
- Status: done.
