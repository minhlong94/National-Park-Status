# Specification: National Park Status

This file records all the requirements that the owner gave for this repository.
Add each new instruction from the owner to the "Requirements" list as a new item.
Do not remove an item. If a new instruction replaces an old one, write the new item and mark the old item as replaced.
The request of the owner in each item is edited for clarity: correct spelling and grammar, full names, and clear meaning. It does not need to be the exact words of the owner (see R59).

Text rule: Write this file, the README and the page text in ASD-STE100 Simplified Technical English (see R5).

## Product

The product is one web page, `index.html`. The page shows the current conditions of all 64 U.S. national parks (63 until 2026; see R47).

- Live page: https://minhlong94.github.io/National-Park-Status/
- Source of the first version: the "Park conditions board" artifact (https://claude.ai/artifact/Ko71Jdm9JFZkz49sRf7GYt).

## Requirements

### R0. Original instruction: park status page with weather and refresh

Request from the owner (edited for clarity):

> Get the road, trail and park status of every national park. Build an HTML page with this status and the weather conditions. Sort the parks by visits and show only the 20 most visited parks. Add a refresh button that gets new data on demand.

Requirements:

- Get the status of the roads, trails and parks for each national park.
- Make an HTML page that shows this status.
- Show the weather conditions for each park.
- Sort the parks by the number of visits, with the most visited park first.
- Show only the 20 most visited parks.
- Add a "Refresh" button. When the reader clicks it, the page gets new data.
- Status: done, with a change from R13. The page shows all parks (64 since R47) in pages of 10. The first page shows the 10 most visited parks.

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
- The link is in the footer of the page. (Replaced by R57: the link is at the top of the page.)
- Status: done.

### R8. Merge the work into `main`

- Open a pull request from the work branch to `main`.
- Merge the pull request.
- Status: done.

### R9. Monthly visits and climate chart for each park

Request from the owner (edited for clarity):

> When I click a park, show an interactive chart of its visitors by month for the last 3 years (vertical bars, one color for each year). Also show the average low and high temperature, snow and rain from historical data. Use one chart or separate charts, as works best for the reader.

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

Request from the owner (edited for clarity):

> The workflow failed. Try again, and make sure to use timeouts.

Requirements:

- Each network request has a timeout of 30 seconds for each step (connect, TLS handshake and each read).
- The script tries each request a maximum of 3 times.
- The script stops after 10 minutes.
- If 3 parks fail one after the other, the script stops the requests to that host.
- The "Get the data" step stops after 15 minutes. The job stops after 20 minutes.
- If one source fails, the workflow keeps the good data from the other source. The run then shows a failure.
- Status: done.

### R11. Store the monthly data and add only new months

Request from the owner (edited for clarity):

> The monthly data changes very little. Save it in a separate file, so that it does not need a refresh every time. Refresh it only when new data is available. For example, store the data up to Sep 2026 (if available), and refresh it only in November. Try the first park first. If the first park has no data for October, stop and do not get data for the other parks.

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

Request from the owner (edited for clarity):

> Can you also get fall foliage data?

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

Request from the owner (edited for clarity):

> Can you get the foliage map from https://www.explorefall.com/?

- ExploreFall has no public data service. Its maps and forecasts are its own work. The page does not copy them. Each park with a clear fall color change has a link to the ExploreFall map.
- Status: done.

### R13. Show all parks in pages of 10

Request from the owner (edited for clarity):

> It is not necessary to show all 63 parks. Show the top 20 and put the list on pages.

Then the owner made the request more exact:

> To be clear: show all parks, but show only the top 10 first and put the other parks on more pages.

The owner also said:

> Refresh only the current park statuses and the weather conditions.

The owner chose to keep the weekly refresh of the this-season leaf reports (R12).

Requirements:

- The park table shows all parks (63 at that time, 64 since R47).
- Each page shows 10 parks. The first page shows the 10 most visited parks.
- The page has "Previous" and "Next" buttons and a button for each page.
- A new search, filter or sort goes back to page 1.
- The totals at the top count all parks, not only the parks on the page.
- "Refresh data" refreshes only the current park statuses and weather conditions. The stored data (monthly visits, monthly weather, usual fall color timing) does not refresh. The scripts only add new months or years.
- Status: done.

### R14. Publish each request with a pull request

Request from the owner (edited for clarity):

> Open a pull request to publish the work. Do this after each completed request, unless I tell you not to.

Requirements:

- After each request is complete, open a pull request from the work branch to `main` and merge it.
- After the merge, push `main` to `gh-pages`, so the live page shows the change.
- Do not do this if the owner says not to.
- Status: done. Continues for each request.

### R15. Best time to visit each park

Request from the owner (edited for clarity):

> Can you find the best time to visit each park?

Requirements:

- For each park and each month, calculate a visit score from 0 to 100. Use only the stored data:
  - weather comfort (45%): the average daily high. 60–80°F is best.
  - visitors (25%): the visits of the month compared with the busiest month. Changed by R33 and R34: now a balance (see R34).
  - little rain (15%) and little snow (15%).
  - fall color: add 10 in the months when leaf color is usually best.
- If a month has less than 5% of the visits of the busiest month, access is probably limited. Its score is cut to 30%.
- The best months are a maximum of 2 windows of neighbor months, with a maximum of 3 months in each window, near the top score.
- The park table has a "Best time" column. The sort list has "Best to visit this month".
- The park details show the best months, the reasons, the months with limited access, the usual open dates of the seasonal road (if the park has one) and a score strip with the same months as the charts.
- The page tells the reader that the score does not include events, wildlife seasons or road openings.
- Status: changed by R21. The page does not show the score now.

### R16. Park details layout

Request from the owner (edited for clarity):

> Add it to the bottom of the park details, as in this example. Also put the closure history in a column, so that it does not push down the top section.

Requirements:

- The "Best time to visit" block is at the bottom of the park details. (R21 removes this block.)
- The park details have three columns: alerts, 3-day forecast and closure history. On a narrow screen, the columns go one below the other. (Replaced by R56: two columns, and the closure history is at the end.)
- Status: done.

### R17. Fall color map from NASA data

Request from the owner, edited for clarity (the answer to "ExploreFall embed or a map from the NASA data?"):

> Use the NASA data.

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

Request from the owner (edited for clarity):

> Yes, fix the this-season leaf reports.

Requirements:

- The USA-NPN request returned 0 reports, also for 2025. A test of 9 request formats showed the cause: the bounding box parameters. Without them, one week in October 2025 has 9,634 reports of colored and falling leaves.
- Remove the bounding box from the request.
- Status: done.

### R19. Fix the park details layout

Request from the owner, edited for clarity (with a screenshot of a cut-off closure history column):

> The layout is broken. Can the 3-day forecast be vertical?

Requirements:

- When the park table scrolls sideways (a window narrower than the table), the park details use the visible width and stay in view. No column is cut off.
- The columns (alerts, forecast, closure history) go to the next line when there is not enough width.
- The 3-day forecast shows one row for each day: day, high and low, weather, precipitation. (Replaced by R55: one column for each day, side by side.)
- Links in the park details use the link color, so that they are easy to read in dark mode.
- Status: done.

### R20. Regional fall color map

Request from the owner (edited for clarity):

> I do not need details for each park. A regional map is sufficient, for example like the map from ExploreFall.

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

Request from the owner (edited for clarity):

> I do not need the best time to visit score. Show it as a banner below the park name that encourages people to visit. Also add a "Best time to visit" filter, with the options "this month" and "selected months".

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

Request from the owner (edited for clarity):

> The grid of points runs too long. Stop it and go back to the original method. Use this grid method only for the parks without data.

Requirements:

- Stop the grid collection. Revert the regional map (R20) and the grid script. The fall color map shows the park dots again (R17).
- Keep the best time banner and filter (R21).
- For parks without fall color data (fewer than 3 years with data in the 3 km box), use the grid method: get all years again with a 21 km box and use the pixels that have a growing cycle. In October 2026 this is 18 parks and 72 requests.
- Each park gets the wide box only once. The file `data/foliage.js` lists these parks in `wide`. New NASA years use the wide box for them.
- The park details tell the reader when a park uses the 21 km box.
- Status: done.

### R23. Short numbers for visits

Request from the owner (edited for clarity):

> Shorten the visit counts and other large numbers, for example to 400K or 4M. Exact numbers are not necessary.

Requirements:

- Show big numbers in a short form, not exact. Examples: 11.5M, 4.8M, 4M, 400K, 15K, 7.8K.
  - From 1 million: millions with one decimal (no decimal if it is 0, or from 100 million).
  - From 10,000: whole thousands.
  - From 1,000: thousands with one decimal.
  - Numbers under 1,000 do not change.
- This applies to the "2025 visits" column, the visits in the monthly tooltip, the monthly values table and the chart axis.
- Status: done.

### R24. Separate banners for the best time and the best fall color

Request from the owner, edited for clarity (with a screenshot of the banners):

> Do not show a star for a month that is not the current month. Remove fall foliage from the best time calculation, and add a separate banner for the best fall foliage months next to the best time to visit.

Requirements:

- The star (★) shows only on a banner that is about now. A "Best time to visit" banner for other months has no star.
- The best time to visit does not use fall color now. It uses only weather comfort (45%), visitors (25%, a balance, see R34), little rain (15%) and little snow (15%).
- Parks with a clear fall color change get a second banner:
  - "Best fall color:" and the months. A month counts if it has 10 or more days of the usual best color window (the middle of the greenness drop to leaves off). If no month has 10 days, the page uses the month of the middle of the window.
  - If today is in the window: "Fall color is at its best now!" with a star.
  - The usual dates show when the reader puts the pointer on the banner.
- The fall color banner uses the fall color. The best time banner uses green.
- Status: done.

### R25. A different color for a best time that is not this month

Request from the owner (edited for clarity):

> If the best time to visit is not the current month, use a different color.

Requirements:

- If the best months do not include the current month, the "Best time to visit" banner is neutral gray.
- If they include the current month, the banner ("Now is a great time to visit!") stays green.
- The fall color banner does not change.
- Status: done.

### R26. Short banners

Request from the owner (edited for clarity):

> Make the banners short, for example "Best: Oct–Nov" and "Fall: Oct–Dec".

Requirements:

- The best time banner shows "Best:" and the months. The fall color banner shows "Fall:" and the months.
- The color and the star show if it is now:
  - "Best:" is gray when the best months do not include this month, and green with a star when they do.
  - "Fall:" uses the fall color, with a star when today is in the usual best color window.
- The full meaning shows when the reader puts the pointer on the banner. Screen readers also get it.
- The banners are on one line when there is space. A month range does not break across two lines.
- Status: done.

### R27. Nearby airports

Request from the owner (edited for clarity):

> For each park, add the nearby airports (more than one) with their IATA codes.

Requirements:

- For each park, show 2 or more nearby airports with their IATA codes.
- Use only medium and large airports with scheduled passenger flights and an IATA code, in the United States and its territories.
- For each park:
  - the 3 nearest airports
  - the nearest large airport, if it is not one of the 3
  - Airports farther than 500 miles are left out, but each park keeps at least 2 airports.
- The distance is the straight-line distance in miles from the park point.
- The table shows the codes under the banners (for example "✈ TYS · AVL · TRI · CLT"). The park details show a list with the code, the airport name, the distance and a "Large airport" tag.
- Source: OurAirports (public domain). The script `scripts/build_airports.py` makes `data/airports.js`. Airports change very little, so the page does not refresh this file.
- Status: done.

### R28. Remove the closures column, add °C and mm

Request from the owner (edited for clarity):

> Remove the park closures column from the table.
>
> Add °C and mm for temperature, rain and snow.

Requirements:

- The park table does not have the "Past closures" column. The closure history is still in the park details.
- Temperatures show °F and °C. Rain and snow show inches and mm. This applies to:
  - the current weather and the forecast for today in the table
  - the 3-day forecast
  - the monthly tooltip and the monthly values table (new columns for °C and mm)
  - the reasons on the best time banner
- The chart axes stay in °F and inches. One axis has one unit.
- Wind speeds stay in mph.
- Note: R54 replaces the two units side by side with a Units button (one unit system at a time).
- Status: done.

### R29. Save the statuses and weather in the browser

Request from the owner (edited for clarity):

> Save the park status and the weather in the browser, and refresh them only when I ask.

Requirements:

- The page saves the last park statuses (NPS alerts), the weather and the NWS warnings in the browser (localStorage).
- When the page opens, it shows the saved data and does not send requests. The top of the page shows the time of the saved data.
- The page gets new data only when the reader clicks "Refresh data".
- On the first visit (no saved data), the page gets the data one time.
- If one source fails during a refresh, the page keeps the saved data of that source and shows its time.
- If the browser blocks the storage, the page still works without saved data.
- Status: done.

### R30. Highlight the current month in the charts

Request from the owner (edited for clarity):

> Add a light highlight of the current month to the charts.

Requirements:

- In the monthly charts of each park (visits, fall color strip, temperature, rain and snow), the current month has a light green band behind the marks.
- The label of the current month is bold, so the highlight does not use color only.
- The band is lighter than the gray band that shows the month under the pointer. Both can show at the same time.
- Status: done.

### R31. Live road status and road work pages

Request from the owner (edited for clarity):

> In Glacier, Two Medicine Road is closed. Discuss with me (chat only) how to best capture this and similar information.
>
> It shows as a red line on this page: https://www.nps.gov/glac/planyourvisit/directions.htm
>
> I also found https://www.nps.gov/glac/planyourvisit/projectwork.htm. Do other parks have pages like it?
>
> OK, do it.

Requirements:

- Some parks publish the status of each road in a live map database. The NPS alerts do not always include these closures.
- Glacier: on "Refresh data", the page reads the closed roads and the roads with construction from the park road map database (`carto.nps.gov/user/glaclive`, table `glac_road_nds`).
- In the park details, a "Live road status" list shows each road, its status (Closed or Construction), its reasons and its usual season. Closed roads are first. A link opens the park road status map.
- The number of closed roads is added to the Roads count of the park. If the NPS alerts show no closures but a road is closed, the park status is "Partial closures".
- The page saves the road status in the browser with the other data (R29). If the request fails, the page keeps the saved road status.
- The code keeps the live sources in one list (`LIVE_ROADS`), so more parks can be added later. Only Glacier has such a source now.
- Some parks have a page about road construction and project work. These pages are text only, so the page shows a link to them in the park details. Now: Glacier, Yosemite, Grand Teton, Arches, Sequoia and Kings Canyon.
- Status: done.

### R32. Flood alerts for the whole park

Request from the owner (edited for clarity):

> (Chat) Is it possible to show flash flood warnings for the parks?
>
> OK, do it.

Requirements:

- The page finds the NWS alerts for the whole park, not only for one point.
  - The file `data/park-bounds.js` keeps a simple outline of each park (from the NPS boundary data) and the NWS zones inside the park.
  - On "Refresh data", the page gets the active alerts one time for each state or territory that has a park.
  - An alert with a polygon (for example a Flash Flood Warning) applies if the polygon touches the park outline.
  - An alert without a polygon (for example a Flood Watch) applies if one of its zones is in the park.
  - If the outline file does not load, or a park has no zones, the page uses one point for that park.
- Flood alerts are easy to see:
  - The park row shows the strongest flood alert under the status. A warning or emergency is red. A watch, advisory or statement is orange.
  - A "Flood alerts" filter shows only the parks with a flood alert.
  - The park details show the flood alerts first, with the text from NWS, the end time and a safety note.
- The script `scripts/build_bounds.py` makes the outline file. The workflow `.github/workflows/build-bounds.yml` runs it when the script changes, or from the Actions tab. Park boundaries and NWS zones change very little, so no schedule runs it.
- Status: done.

### R33. Many visitors count for the best time to visit

Request from the owner (edited for clarity):

> For the best time to visit, a high visitor count should also be a positive factor. For example, the visits to Great Smoky Mountains peak in October for a reason: fall foliage.

Requirements:

- In the best time to visit, a month with more visitors gets a higher score. People come at the best times, for example for the fall color in Great Smoky Mountains in October.
- The weights do not change: weather comfort 45%, visitors 25%, little rain 15%, little snow 15%.
- A month with less than 5% of the visits of the busiest month still gets a low score, because access is probably limited.
- If most visitors come in the best months, the reason text says "most visitors come at this time".
- Status: changed by R34. The visitor part is now a balance.

### R34. A balance for visitors in the best time to visit

Request from the owner (edited for clarity):

> (Chat) It should be a balance. I do not want to go where it is too crowded. But if very few people visit, there is usually a reason not to visit.
>
> Option A.

Requirements:

- The visitor part of the best-time score (25%) is a balance:
  - Less than 5% of the visits of the busiest month: the visitor part is 0, and the month score is cut (access is probably limited).
  - From 5% to 55%: the visitor part increases. Few visitors usually have a reason, for example closed roads, heat or snow.
  - From 55% to 80% (the shoulder season): the visitor part is full.
  - From 80% to 100%: the visitor part decreases a little, to 75% for the busiest month, because of the crowds.
- Fall color stays separate (option A). The "Fall:" banner shows the fall color months. The "Best:" banner does not use fall color.
- Status: done.

### R35. Seasonal closure dates

Request from the owner (edited for clarity):

> Some seasonal closure dates are missing, for example for Yosemite: https://www.nps.gov/yose/planyourvisit/seasonal.htm

Requirements:

- The park details show a "Seasonal closures" section (in the third column, above the closure history):
  - "Closed now": the campgrounds and visitor centers that are closed for the season now, and the date they open again.
  - "Next closures": the seasonal closures that start in the next 12 months, with the start and end dates.
  - Closures shorter than 7 days (for example Christmas Day) are not shown.
  - The source is the NPS API (operating hours of campgrounds and visitor centers).
- For parks with a seasonal dates page with history datasets (now: Yosemite), the section shows the usual open dates of each campground and trail. The usual dates are the median of the last 10 years. Each row also shows the last season and the years that it did not open.
- The seasonal road history has Mariposa Grove Road (Yosemite), from the Yosemite roads dataset.
- The script `scripts/fetch_seasonal.py` makes `data/seasonal.js`. The workflow `.github/workflows/update-seasonal.yml` runs it each Monday. It uses the `NPS_API_KEY` secret if it exists, or DEMO_KEY.
- Status: changed by R36. The closures are now in a separate section of the page.

### R36. A separate section for campgrounds and visitor centers

Request from the owner (edited for clarity):

> Put campgrounds and visitor centers in a separate section, after the seasonal road section and before the fall foliage section.

Requirements:

- The seasonal closures of campgrounds and visitor centers (R35) are in a separate section of the page: "Campgrounds and visitor centers".
- The order of the sections is: seasonal road history, campgrounds and visitor centers, fall color map, closure history. The fall color map moved below the new section.
- A "Park" list selects the park. Each park in the list shows the number of closures now.
- The section shows "Closed for the season now" and "Next closures" side by side (one column on a phone), and for Yosemite the usual open dates.
- The park details do not show the closures. They show one line with the number of closures and a link to the section, with the park selected.
- Status: done.

### R37. A calendar for campgrounds and visitor centers

Request from the owner (edited for clarity):

> Make "Campgrounds and visitor centers" easy to see, for example as a calendar.

Requirements:

- The "Campgrounds and visitor centers" section shows a calendar of the next 12 months for the selected park:
  - One row for each campground or visitor center, with its kind, its name and a short note (for example "Closed until Jul 3, 2027").
  - Green bars show open times. Gray bars with lines show seasonal closures. A dark line shows today. A legend explains the marks.
  - The rows that are closed now come first, then the rows by their next closure date.
  - Put the pointer on a bar, or move to it with the Tab key, to see the dates.
- For Yosemite, a second calendar shows the usual open dates of each campground and trail (from the last 10 years).
- A summary line shows the number of places that are closed now and that close in the next 12 months.
- The same data is also available as a list and as a table (in "Show ..." sections), for screen readers and print.
- On a phone, the name is above the bar, and the month labels do not show the year.
- Status: done.

### R38. Highlight storms and heavy snow in the forecast

Request from the owner (edited for clarity):

> A storm is coming to Great Smoky Mountains, but the 3-day forecast does not highlight it enough. Fix this, and do the same for heavy snow.

Requirements:

- The page finds the dangerous days in the 3-day forecast from the amounts, not only from the weather code. (For Great Smoky Mountains on Oct 10, 2026, the code said "rain showers", but the forecast had 1.25 in of rain and gusts to 58 mph.)
- Rules for one day:
  - Heavy snow: 4 in or more of snow, or the code for heavy snow. Red at 8 in or more.
  - Freezing rain: the code for freezing rain. Red.
  - Thunderstorms: the code for thunderstorms. Red with hail.
  - Heavy rain: 1 in or more of rain, or the code for heavy rain. Red at 2 in or more.
  - Strong wind: gusts of 40 mph or more. Red at 58 mph or more.
  - Storm: heavy rain or thunderstorms together with strong wind. Red when the gusts are 50 mph or more.
- The forecast card of that day has a colored frame and background (orange or red), the kind of danger (for example "Storm") and the values.
- The "Today" column of the park row shows a badge with the strongest day, for example "Storm Sat". The badge tooltip lists all the days.
- A "Storm or heavy snow" filter shows only the parks with such a day.
- The page gets the daily wind gusts from Open-Meteo for these rules.
- Status: done.

### R39. Show the names of the closures, and find more trail closures

Request from the owner (edited for clarity):

> The Zion status today does not show "The Virgin River Narrows and all slot canyons closed": https://www.nps.gov/zion/planyourvisit/conditions.htm

Requirements:

- The NPS alert was in the data, but the page did not show it clearly:
  - Its text has no trail keyword, so the page put it in "Other", not in "Trails".
  - The park row showed only "Partial closures", with no names.
- The trail keywords now also include: hikers, wilderness, narrows, slot canyon(s), canyoneering, river hike(s).
- The park row shows the names of up to 3 closures under the status, and "+N more closures" if there are more. The full name is in the tooltip. Changed by R42: the names are now only in the tooltip of the status badge.
- In the park details, the alert groups that have a closure come first.
- Status: done.

### R40. Flash flood potential rating

Request from the owner (edited for clarity):

> Include the flash flood potential ratings from this product for its parks, and for other parks too: https://forecast.weather.gov/product.php?site=NWS&product=RRA&issuedby=SLC

Requirements:

- On "Refresh data", the page gets the latest NWS Salt Lake City "Flash Flood Potential Rating" (product RRA, office SLC) from api.weather.gov. It reads the rating of each day (for example today and tomorrow) for Arches, Bryce Canyon, Canyonlands, Capitol Reef and Zion. The ratings are: Not expected, Possible, Probable, Expected.
- No other NWS office publishes this rating. For the other parks, the page makes an estimate for the 3 forecast days:
  - Expected: an active NWS Flash Flood Warning or Emergency (today).
  - Probable: an active Flood Watch or Flash Flood Watch, thunderstorms, or 1 in of rain or more.
  - Possible: 0.5 in of rain or more, or rain showers with 0.25 in or more.
  - The page always labels the estimate as an estimate. It is not an NWS rating.
- The park row shows a "Flash flood" badge with the highest rating and its day: red for Expected, orange for Probable. An official rating also shows at Possible. An estimate shows only at Probable or Expected.
- The park details show "Flash flood potential" first, with the rating of each day, the source, the issue time and the meaning of the rating.
- The "Flood alerts" filter also shows the parks with a rating of Probable or Expected.
- The page does not use an official rating that is older than 36 hours. The page saves the rating in the browser with the other data (R29).
- Status: changed by R48. The rating now covers all 3 forecast days.

### R41. Show live road closures in the park row, and old saved data

Request from the owner (edited for clarity):

> Going-to-the-Sun Road is closed, but the page did not show it. (Screenshot of the Glacier road map: "Going-to-the-Sun Road Closed, Winter Weather".)

Requirements:

- The live road data of Glacier had the closure, but the page did not show it clearly:
  - The park row showed only the number of roads, not their names.
  - The road is closed only in part (the ends stay open), and the page did not show this.
  - The page shows the data from the last refresh (R29). Old saved data did not have the closure, and the page did not tell the reader that the data was old.
- The page reads all the road parts that have a status. A road is "Closed" when all its parts with a status are closed, and "Partly closed" when some parts are still open.
- The park row lists the live road closures with the NPS closures (up to 3 names; changed by R42: now in the tooltip of the status badge). Main roads come first, for example "Going-to-the-Sun Road partly closed (winter weather)". Campground loops come after the NPS closures. Road parts with no name are not counted or listed.
- The seasonal road history shows the live status of the road now, if the park has a live road map ("Now: Partly closed · Winter Weather").
- If the saved data is older than 6 hours, the time at the top is red and says "Click Refresh data for the current status". The page still gets new data only when the reader clicks the button.
- Status: done.

### R42. Only badges in the status column

Request from the owner (edited for clarity):

> Show only badges in the status column, because it has too much information. (Screenshot of the Status column of Great Smoky Mountains.)

Requirements:

- The status column of the park row shows only badges: the status ("Open", "Partial closures", "Closed"), the flood alert and the flash flood rating.
- The names of the closures (NPS alerts and live road closures, main roads first) are not shown as a list in the row. They are in the tooltip of the status badge. The park details show all the closures.
- Status: done.

### R43. Planned road dates of other parks in the seasonal road section

Request from the owner (edited for clarity):

> Include the seasonal road closures of other parks in the lower section, for example Yellowstone: https://www.nps.gov/yell/planyourvisit/parkroads.htm

Requirements:

- The weekly seasonal workflow (`scripts/fetch_seasonal.py`) reads the planned road dates of this year from the roads page (`parkroads.htm`) and the hours page (`hours.htm`) of each park. It knows two forms:
  - "Open April 17 - October 31, 2026: West Entrance to Madison, Madison to Old Faithful" (Yellowstone). One row for each road section. "Open year-round" is a road that is open all year. The dates for oversnow vehicles (snowmobiles and snowcoaches) are not used.
  - "May 1, Spring opening of Teton Park Road" and "October 31, Winter closure of Teton Park Road" (Grand Teton).
- The pages of the other parks do not give the dates in a form that a program can read. A park is added when its page uses one of the two forms.
- The seasonal road section has a "Road dates" tab for each park with planned dates. The tab shows a calendar of the year: one row for each road section, green when open, gray with lines when closed, and a line for today. A summary line shows how many road sections are open today on the plan.
- The park details have a link to the tab ("Seasonal roads").
- Status: done.

### R44. Seasonal area closures (wildlife, trails, areas) for all parks

Request from the owner (edited for clarity):

> The closures for Grand Teton are missing: https://www.nps.gov/grte/learn/management/wildlife-closures.htm. Make sure that no park is missing.

Requirements:

- Each week, for every park, the seasonal workflow (`scripts/fetch_seasonal.py`) reads the pages where parks post seasonal closures:
  - the Plan Your Visit and Management index pages, hours, conditions and seasonal pages, wildlife closure and closure pages, laws and policies pages, and the Superintendent's Compendium (also as PDF);
  - the links on these pages about closures, the compendium, bear management, wildlife protection, raptors and nesting (two link levels, at most 30 pages for each park).
- The script keeps a sentence or a short list item when it closes something between two dates of the year, for example "closed to all public entry from December 15 through March 31". A "Seasonal Closures" heading above a list also counts. "Voluntarily avoid" zones are kept and marked as voluntary.
- The script leaves out: rules that are not closures of a place (food storage, smoking, vehicles, boats, fishing, camping rules, surfing), opening hours, reservations, notes about past years, dates when something is open, rules for all year, and repeated closures.
- When the sentence has a general subject ("Area is closed …"), the page uses the heading above it as the name (for example "Hayden Valley Bear Management Area").
- The "Campgrounds, visitor centers and seasonal closures" section shows these closures in the same calendar (kinds: Wildlife area, Voluntary area, Climbing, Trail, Road, Area). They repeat every year. The list view shows the full text and a link to the NPS page.
- For each park, the section links to the Superintendent's Compendium, the official list of all closures and rules, when the script finds it.
- Coverage now: dated closures in 26 parks. Compendium links for 51 of the 62 park sites (Sequoia and Kings Canyon share one). The script cannot find a compendium for Acadia, Carlsbad Caverns, Denali, Death Valley, Gates of the Arctic, Glacier Bay, Katmai, Kobuk Valley, Lake Clark, American Samoa and White Sands.
- Status: done.

### R45. Past snow in the current weather

Request from the owner (edited for clarity):

> In the current weather of each park, also show the recent snow accumulation.

Requirements:

- On "Refresh data", the page also gets from Open-Meteo the daily snowfall of the last 30 days and the snow depth now, for all parks in one request. If this request fails, the rest of the weather still shows.
- The "Weather now" column of the park row shows a snow line when there was snow in the last 7 days or there is snow on the ground, for example "Snow: 5.4 in (137 mm) in 7 days · 4 in (100 mm) on the ground".
- The park details show a "Past snow" table: today (so far), yesterday, the last 7 days, the last 30 days and the snow on the ground now. The values are for one point near the main visitor area.
- The page saves the past snow in the browser with the other weather data (R29).
- Status: done.

### R46. Usual closing day of Going-to-the-Sun Road

Request from the owner (edited for clarity):

> Going-to-the-Sun Road is usually fully open until the third Monday of October. Show this as a default line, so that people know what to expect.

Requirements:

- Going-to-the-Sun Road has a usual plan: it is fully open over Logan Pass until the third Monday of October, if the weather permits.
- The page calculates the date for this year (for example Monday, October 19, 2026). After that date, it shows the date of next year.
- The line shows always, also with no live data:
  - in the seasonal road history, above the live status ("Usually fully open until the third Monday of October (Mon, Oct 19, 2026), if the weather permits.");
  - in the Glacier park details, under the live status of Going-to-the-Sun Road.
- Other roads can have the same kind of rule (`plan` in the road data).
- Status: done.

### R47. Chiricahua, the 64th national park

Request from the owner (edited for clarity):

> There is now a 64th national park. Check if the data supports it yet.

Requirements:

- The NPS API lists Chiricahua (code `chir`, Arizona) with the designation "National Park". It was Chiricahua National Monument.
- The data sources support it:
  - NPS alerts, campgrounds (Bonita Canyon Campground) and visitor center: yes.
  - Monthly visits (NPS Visitor Use Statistics, unit CHIR): yes, from January 2023 to December 2025. The 2025 total is 70,406 visits.
  - Park outline (NPS boundary data, unit CHIR, still named "Chiricahua National Monument"), NWS zones, Open-Meteo weather and climate, NASA fall color data and OurAirports: yes.
  - The NWS Flash Flood Potential Rating does not include it (it is not in southern Utah). The page uses its estimate (R40).
  - The closure history (fixed data) has no event for it.
- The park list has 64 parks. Chiricahua is number 57 by 2025 visits, between Dry Tortugas and North Cascades. The parks after it move down one place. A note in the park details says that it was a national monument.
- The data scripts accept a park that is new in `index.html`:
  - `scripts/fetch_history.py` expects 64 parks and gets all the months of the file for a new park. The other parks do not change.
  - `scripts/fetch_foliage.py` gets all the years for a new park with the normal box, then with the wide box if it has no data.
  - The airports, park outlines and seasonal closures are made again for all parks. The new workflow `.github/workflows/build-airports.yml` makes `data/airports.js` when its script changes, or from the Actions tab.
- The default branch of the repository is gh-pages, so the scheduled data runs worked on gh-pages and main did not get their data. Now a scheduled run works on main and then publishes main to gh-pages, so the two branches stay the same.
- Status: done.

### R48. Flash flood potential for all 3 forecast days

Request from the owner (edited for clarity):

> Show the flash flood potential for all 3 forecast days.

Requirements:

- The flash flood potential shows a rating for each of the 3 forecast days of every park.
- For Arches, Bryce Canyon, Canyonlands, Capitol Reef and Zion, the days that the NWS rating covers (usually today and tomorrow) use the NWS rating. The other days use the estimate of the page (R40) and have the mark "est.".
- The page matches the NWS rating to the days by date. "TODAY" in the rating is the issue date in Utah (Mountain time). So a rating that NWS issued yesterday gives the rating of today from its "tomorrow".
- The park row badge shows the highest day: an NWS rating from "Possible", an estimate from "Probable". It has "(est.)" when the highest day is an estimate. The tooltip lists all 3 days.
- The park details show the 3 days. An estimate day has a dashed frame and "est.". The text says which days come from NWS and which are estimates.
- Status: done.

### R49. Zion: the forecast upstream of the Narrows

Request from the owner (edited for clarity):

> For Zion, also include the forecast for the Narrows upstream: https://forecast.weather.gov/MapClick.php?lat=37.5269&lon=-112.7612

Requirements:

- Rain upstream on the North Fork of the Virgin River causes flash floods in the Narrows, also when the sky in Zion Canyon is clear. The page adds the point 37.5269, -112.7612 ("The Narrows upstream") to Zion.
- On "Refresh data", the page gets the 3-day forecast for this point (in the same Open-Meteo request) and the NWS alerts for this point.
- The Zion park details show the 3-day forecast of the point under the park forecast, with the storm and heavy snow marks (R38) and a link to the NWS forecast for the point.
- An NWS alert for the point counts as a Zion alert, with "(Narrows upstream)" after its name. A flood alert there shows the flood badge in the row.
- The flash flood estimate (R40, R48) of a day uses the higher value of the park point and the upstream point.
- The storm badge in the row also uses the upstream forecast, for example "Storm Fri (Narrows upstream)".
- Other parks can have extra points in the same way (`EXTRA_POINTS`).
- Status: done.

### R50. Fix the failed scheduled data run

Request from the owner (edited for clarity):

> Fix the error of the latest deployment.

Requirements:

- The cause: the change in R47 did not change the push line of the data workflows. A scheduled run made its commit on main but pushed it only to gh-pages. On 2026-10-26, the fall color run pushed to gh-pages only. Then the seasonal run (made from main, without that commit) could not push to gh-pages, and failed.
- The fall color data of that run is now on main too. No data is lost.
- All five data workflows (`update-data`, `update-foliage`, `update-seasonal`, `build-bounds`, `build-airports`):
  - A run that starts on gh-pages (a scheduled run, or a run from the Actions tab, because gh-pages is the default branch) works on main, pushes to main, then publishes main to gh-pages.
  - A push to gh-pages does not start a data run.
  - Each workflow has its own queue, so GitHub does not cancel a waiting run of another workflow.
  - The push step takes the newest commits of main and tries again (4 times), so two runs at the same time do not fail. Then it publishes the newest main to gh-pages. If another run already published a newer main, that is not an error.
- Status: done.

### R51. Road conditions of Capitol Reef (and other parks), and a short flash flood text

Request from the owner (edited for clarity):

> Capitol Reef has road closure conditions that the page does not show. Add them.
>
> Also, keep the flash flood message short.

Requirements:

- Capitol Reef posts a "Current Road Conditions" table for each district on its conditions page (Road Name, Condition, Updated on). The NPS API does not have these conditions.
- The script `scripts/fetch_conditions.py` reads the road condition tables of all parks (on the conditions, road conditions and roads pages). It uses a table when the first row has a road column and a condition or status column. The heading above the table is the district. When a cell has a long description, the script uses the first bold text or the first line, and keeps a short part of the rest as a note. A row that only points to another table ("See the … Table above") is left out. Now: Capitol Reef and Sequoia and Kings Canyon.
- The workflow `.github/workflows/update-conditions.yml` runs the script every 6 hours, and saves `data/road-conditions.js`.
- The park details show "Road conditions" for each district, with a colored mark: Closed (red), not recommended or impassable (orange), unknown or a warning (gray), open (green). It shows the date of the park update and a link.
- A road that is closed or (likely) impassable counts as a road closure: in the Roads count, in the park status ("Partial closures") and in the tooltip of the status.
- The flash flood text is short: "NWS: Today and Wed. Estimate: Thu. Avoid slot canyons and washes at Probable or Expected." The meaning of each rating is in the tooltip of the day. The flood alert note is short too.
- Status: done.

### R52. Weather icons

Request from the owner (edited for clarity):

> Show the weather as icons, so that it is easy to read and scan.

Requirements:

- The weather conditions show as icons, not as words, so that you can read the weather quickly:
  - "Weather now": an icon for the current weather. At night, a clear sky shows a moon.
  - "Today": an icon for the weather of today.
  - 3-day forecast cards (also the Zion "Narrows upstream" point): an icon for each day, with the short name of the weather in small gray text.
- Icons: ☀️ clear, 🌤️ mostly clear, ⛅ partly cloudy, ☁️ overcast, 🌫️ fog, 🌦️ light rain or showers, 🌧️ rain, 🧊 freezing rain or drizzle, 🌨️ snow, ❄️ heavy snow, ⛈️ thunderstorm, 🌙 clear at night.
- Small icons in front of values: 💨 wind, 💧 chance of precipitation, ❄️ snow.
- The name of the weather is the tooltip of each icon and the label for screen readers.
- Status: done.

### R53. NPS API key for development tests

Request from the owner (edited for clarity):

> For development, store this NPS API key to test the data. (The key is not written here.)

Requirements:

- The NPS API key for development is a network secret of the cloud development environment (host `developer.nps.gov`). The proxy adds it to the requests. Tests can then use the real NPS data.
- The key is not in the repository. The repository is public, so a key in it is not secret. The page still uses `DEMO_KEY`, or the key that a user types in "NPS API key".
- Status: open. The secret is saved, but the NPS API returns "API_KEY_INVALID". The secret must send only the key in the `X-Api-Key` header, with no word before it.

### R54. Units button: imperial or metric

Request from the owner (edited for clarity):

> Add a button to choose imperial or metric units. Apply it to all values.

Requirements:

- A "Units" button at the top of the page has two parts: "°F · Imperial" and "°C · Metric". Imperial is the default.
- The page shows one unit system at a time. This replaces the two units side by side of R28.
  - Imperial: °F, inches (rain and snow), mph, miles, feet.
  - Metric: °C, mm (rain), cm (snow), km/h, km, m.
- The units apply to all values on the page:
  - current weather, feels like, wind and gusts, today, past snow
  - 3-day forecast cards and the storm and heavy snow labels
  - monthly charts (axes and titles), the monthly tooltip and the monthly values table
  - the reasons on the best time banner
  - airport distances and the distance of the fall color reports
  - lengths in the fixed texts of the page (for example "Tioga Pass (9,943 ft)" and "10 in of snow")
- The text of NPS alerts and of NPS pages stays as NPS wrote it.
- The browser saves the choice (`parkUnits.v1`). The page uses it again on the next visit.
- When you click the button, the page shows all values again at once. It does not get new data.
- Status: done.

### R55. The 3-day forecast is horizontal

Request from the owner (edited for clarity):

> Show the 3-day forecast horizontally, not vertically.

Requirements:

- The 3-day forecast in the park details shows the days side by side, one column for each day. This also applies to the Zion "Narrows upstream" forecast. (R66: 7 days.)
- Each column shows, from top to bottom: the day, the weather icon, the name of the weather, the high and low temperatures, the chance and amount of precipitation, and the snow (when there is snow).
- A day with a storm or heavy snow has a thick colored line at the top. The warning and its reasons are at the bottom of the column, so that the values of the days stay in line.
- On a phone, the three columns stay side by side. The page does not scroll sideways.
- Status: done.

### R56. Closure history at the end of the park details

Request from the owner (edited for clarity):

> Move the closure history to the end of each park's details. It is not very useful, because it has few events.

Requirements:

- In the park details, "Closure history" is the last part, after "Visits and climate by month". It uses the full width.
- The top of the park details has two columns: the alerts (left) and the weather (right). On a narrow screen (700 px or less), the parts are in one column.
- Status: done.

### R57. Source link at the top, collapsible alert sections, data labels on the climate charts

Request from the owner (edited for clarity):

> Put the GitHub source URL at the top of the page. Also, make all park alerts collapsible, with a button for each park that opens all sections. Also, add data labels to the temperature, rain and snow charts.

Requirements:

- The link to the source code (github.com/minhlong94/National-Park-Status) is at the top of the page, under the description, with the GitHub mark. It is not in the footer.
- In the park details, each alert section can open and close: flood alerts, live road status, road conditions, and the NPS alert groups (Roads, Trails, Facilities and camping, Other alerts).
  - The sections are closed when you open a park. The title of each section shows the number of items, and a red flag shows the closures (or flood warnings) in it, for example "Roads (2) 1 closure".
  - When a park has two or more sections, a "Show all sections" button opens all of them. Then the button changes to "Hide all sections".
  - The page keeps the open sections when it shows the list again (for example after the units change).
  - Note: R58 replaces these collapsible sections. The sections are always visible, and each alert opens and closes.
- The temperature, rain and snow charts show their values:
  - Temperature: the average high above each column and the average low below it.
  - Rain and snow: the value above each column. One decimal under 10, no decimal from 10. No label for a month with no rain or snow.
  - The labels use the selected units (R54). On narrow screens the labels are smaller.
- Status: done.

### R58. Alerts show the headline, and the text opens on a click

Request from the owner (edited for clarity):

> Correction: for the park alerts, show only the headline and collapse the content.

Requirements:

- In the park details, the section headings are always visible, with the number of alerts and a red flag for the closures (for example "Roads (2) 1 closure").
- Each alert shows only its headline. The text, the category, the date and the link open when you click the headline. This applies to NPS alerts, flood alerts and live road status.
- An alert has its color line (closure, danger, caution, information) also when it is closed.
- When a park has two or more alerts, a "Show all alert details" button opens all of them. Then the button changes to "Hide all alert details".
- The page keeps the open alerts when it shows the list again (for example after the units change).
- Status: done.

### R59. Average closing line on the seasonal road chart, and clear owner requests in this file

Request from the owner (edited for clarity), with a screenshot of the Going-to-the-Sun Road chart and a red line drawn at Oct 1:

> For Glacier, add a red line to the seasonal road chart at the average closing date.
>
> Also, clean up my requests in `spec.md`, so that they are clear and have no errors. Do this for future requests too. The text does not need to match my words exactly.

Requirements:

- The seasonal road chart shows a red dashed line at the average closing date, with the label "Average closing" and the date, for example "Average closing Oct 1 (6 years)". The average uses the years in the chart that have a closing date.
- The line is on the charts of all seasonal roads that have closing dates (Going-to-the-Sun Road, Tioga Road and the others), because they use the same chart. The caption of the chart explains the line. (R60 changes the date for roads with a park rule.)
- `spec.md`: the request of the owner in each item is edited for clarity: correct spelling and grammar, full names (for example "Going-to-the-Sun Road", not "GTTS"), and clear meaning. The label is "Request from the owner (edited for clarity)". Future items use the same rule. `CLAUDE.md` has the same rule.
- `spec.md`: old items that later items changed have a note, for example "(Replaced by R55: …)".
- Status: done.

### R60. Going-to-the-Sun Road: the usual closing is the third week of October

Request from the owner (edited for clarity):

> The average closing date of Going-to-the-Sun Road is in the third week of October, not Oct 1.

Requirements:

- The recorded closing dates of Going-to-the-Sun Road in the last 10 years give Oct 1. This is not correct for planning:
  - NPS did not publish closing dates after 2022, so only 6 of the 10 years have a date.
  - Most of these years closed early: the Sprague Fire (2017), early snow (2018, 2019) and COVID-19 (2020).
- When a road has a park rule for the closing (Going-to-the-Sun Road: the third Monday of October), the page uses the rule:
  - Chart: the red dashed line is at the average date of the rule in the chart years. A light red band shows the range of dates (Oct 15–21). The label is "Usual closing Oct 15–21 (the third Monday of October)".
  - Statistics: "Usual closing (the third Monday of October)" with the range of dates, not the average of the recorded dates.
  - Best time to visit: "Going-to-the-Sun Road is usually open from about … to the third Monday of October".
- Roads without a rule (for example Tioga Road) still use the average of the recorded closing dates.
- Status: done.

### R61. Feedback link

Request from the owner (edited for clarity):

> Add a feedback link after the GitHub link: https://forms.gle/B73GLTbAME3KaJsU8

Requirements:

- The top of the page has a "Send feedback" link after the source code link, in the same line. The link opens the feedback form (https://forms.gle/B73GLTbAME3KaJsU8) in a new tab.
- The link has a small message icon. On a narrow screen, the icon and the link stay together on one line.
- Status: done.

### R62. New title: "US National Park Conditions Board"

Request from the owner (edited for clarity):

> Change the title to "US National Park Conditions Board".

Requirements:

- The page heading is "US National Park Conditions Board". The old heading was "Park conditions board".
- The browser tab title is also "US National Park Conditions Board".
- The README heading is the same title.
- Status: done.

### R63. 2026 visits in the monthly chart

Request from the owner (edited for clarity):

> Also add the 2026 visits, up to the last available month. Show only 3 years: 2024–2026. Leave the future months blank.

Requirements:

- The NPS statistics service (`irmaservices.nps.gov`) has only final years. It returns no data for 2026. NPS makes a year final in the first quarter of the next year.
- The IRMA Stats website has preliminary data for the current year. The script `scripts/fetch_history.py` reads it from the report "Park YTD Version 1":
  - The park code is in the URL. If the code does not select the park, the script selects the park by name. The script selects each month in the form of the report viewer (as a browser does) and exports the report as CSV.
  - The rows are different in each park. The script uses the rows named "Total Adjusted Recreation Visits", "Total Recreation Visits", "Total Recreation Visitors" or "Recreation Visitors", and takes the largest value. Example: Yosemite has a total row for each entrance and one for the park ("Park Totals"). The park total is the largest.
  - If a park has no row with these names, the script uses the row whose value "same month last year" is the final value of last year in the file (for example "Canyonlands NP Visitors", "NPS Recreation Visits" for Redwood).
  - It reads 3 parks at the same time. Each request has 3 tries, because the server sends 504 errors when it is busy. If a park still fails, the file does not change, and the next run tries again.
  - Some parks are not in this report (for example Grand Canyon, Rocky Mountain, Carlsbad Caverns, Chiricahua), or the report has no visits total for them (for example Yellowstone, Shenandoah). Their 2026 months stay blank.
- A check: the report value "same month last year" for Great Smoky Mountains (Sep 2025 and Oct 2025) is the same as the final value in the file.
- The key `prelim` in `data/park-history.js` is the first month with preliminary visits. On each run, the script asks the statistics service for these months again. When a month is final, the script writes the final value.
- The first run of a year reads about 10 months for each park (about 30 minutes). The script limit is 45 minutes. Later runs read only the new month.
- The monthly chart shows the last 3 calendar years in the file: 2024, 2025 and 2026. The months after the last month with data are blank.
- The tooltip shows "(preliminary)" for a preliminary month. The source line under the charts tells which visits are preliminary.
- Status: done.

### R64. Campgrounds and visitor centers: parks in alphabetical order

Request from the owner (edited for clarity):

> In "Campgrounds, visitor centers and seasonal closures", sort the parks alphabetically.

Requirements:

- The park list of the section "Campgrounds, visitor centers and seasonal closures" is in alphabetical order (Acadia to Zion). Before, it was in the order of visits.
- When the page opens, the section still shows the most visited park with data (Great Smoky Mountains).
- Status: done.

### R65. Show 2023 in the months without 2026 data

Request from the owner (edited for clarity):

> Also show 2023 for the months that have no data.

Requirements:

- The monthly visits chart shows 2024, 2025 and 2026. In a month without 2026 data, the chart shows 2023 in its place. Examples: November and December 2026 (not available yet), and all months of a park without preliminary 2026 data (for example Yellowstone, Grand Canyon).
- So each month usually has 3 columns. The columns of a month are side by side, with no empty place.
- 2023 has a muted gray color. The legend shows "2023*". Its tooltip says "2023: only in the months without 2026 data". The chart title says the same. The legend button can hide 2023, as for the other years.
- The month tooltip shows the 2023 value only in these months. The values table shows all months of 2023, 2024, 2025 and 2026.
- The best time to visit still uses only the 3 newest years.
- Status: done.

### R66. 7-day forecast

Request from the owner (edited for clarity):

> Make the forecast 7 days.

Requirements:

- The page gets 7 forecast days from Open-Meteo (before: 3). This also applies to the Zion "Narrows upstream" point.
- The park details show "7-day forecast" with 7 compact cards side by side: the day and date, the weather icon and name, the high and low temperatures (the unit is in the heading), the chance and amount of precipitation, and the snow.
- When the 7 cards do not fit (for example on a phone), the row scrolls sideways. The page itself does not scroll sideways.
- A day with a storm or heavy snow has its colored frame and a short label ("Storm", "Heavy snow"). The reasons (amounts and gusts) are in a list under the row and in the tooltip of the card.
- The storm and heavy snow marks (R38), the row badge and the filter "Storm or heavy snow" use all 7 days.
- The flash flood potential (R40, R48) stays at the first 3 days: the NWS rating covers about 3 days, and an estimate further out is not useful.
- Saved data from before this change has 3 days. The heading then shows "3-day forecast" and asks the reader to click Refresh data.
- Status: done.

### R67. Labels on the visits chart, and a road closure map for each park

Request from the owner (edited for clarity):

> For each month of the visits chart, show the label of the highest column.
>
> Show a map of the current road closures of each park. Use a picture if necessary. It is mainly an overview that sends the reader to the NPS page for full details.

Requirements:

- Visits chart: each month shows the value of its highest column (for example "1.6M", "868K"). On narrow screens the text is smaller.
- Road map in the park details (under the alerts):
  - A small map of the park: the park outline (`data/park-bounds.js`) and its main roads (`data/park-roads.js`). The page draws the map, so it does not need a picture.
  - Road lines: OpenStreetMap (© OpenStreetMap contributors, ODbL). The script `scripts/build_roads.py` gets the roads for cars in each park with the Overpass API, keeps the parts inside the park (with a margin of about 200 m), and simplifies the lines. Town streets are not used. Named tracks and named service roads must be 1.5 km or longer. A park has 40 roads or less. The workflow `.github/workflows/build-roads.yml` runs the script when the script changes, or from the Actions tab.
  - The Overpass server sends errors to fast clients, so the script waits 12 seconds between parks. It saves the file after each park and stops after 40 minutes. The next run continues with the parks that are left (all 64 parks take two runs).
  - The page marks the roads that are closed now in red, and the roads with delays or restrictions in orange. The status comes from the data that the page already has: live road status (Glacier), park road condition tables (Capitol Reef, Sequoia and Kings Canyon), seasonal road dates, seasonal closures and NPS road alerts. A report matches a road when the name of the road (without words such as "Road" or "Drive", and without a direction word at the end, as in "Newfound Gap Road South") is in the name or the title of the report. A short report name does not mark longer roads (for example "Many Glacier Road" does not mark "Many Glacier Hotel Parking Road").
  - The names of the closed roads are on the map and in a list under it. A road closure that does not match a road on the map is in a line "Also closed (not on the map)".
  - A note says that the map is an overview only (a red road can be closed in one part only, and some closures can be missing), with a link to the NPS road status page of the park (the live road map, the road conditions page or the conditions page).
  - Note: R69 makes the map interactive, with OpenStreetMap tiles and the NPS road events.
- Status: done.

### R68. Daily screenshots of the NPS road pages (not done)

Requests from the owner (edited for clarity):

> It is better to take screenshots of the NPS page every day.
>
> No need. Keep it as it is.

Requirements:

- The owner withdrew the request. The page keeps the road map of R67. There are no screenshots of NPS pages.
- Status: cancelled.

### R69. NPS road events and an interactive road map

Request from the owner (edited for clarity):

> Use the NPS road events (option 1). Also use them to build what I wanted with the screenshots: a real map with OpenStreetMap.

Requirements:

- On "Refresh data", the page also gets the NPS road events (`developer.nps.gov/api/v1/roadevents`, WZDx format). It saves them with the live road status.
  - An event has road names, a description, start and end dates, the vehicle impact and the line of the part of the road that it affects.
  - The page keeps the events that are active now or start in the next 2 weeks. It keeps one event for each direction of travel, and shortens the lines (at most 80 points, 4 decimals).
  - The feed has no park code. An event goes to a park when a point of its line is inside the park outline.
  - Now: Mount Rainier, Lassen Volcanic, Sequoia and Kings Canyon, Great Smoky Mountains, Crater Lake and Yosemite have events. Yellowstone has none.
- The road map is an interactive map (Leaflet 1.9.4 from cdnjs) with OpenStreetMap tiles in the CARTO style (light, or dark in dark mode). The page loads the map only when a park opens. (R70: OpenStreetMap standard tiles. CARTO tiles need an API key. R71: NPS Park Tiles, with OpenStreetMap as the fallback.)
  - The map shows the park outline, the road events on their exact lines (red: all lanes closed, orange: other impacts, dashed: starts in the next 2 weeks), and the roads that the page marks from alerts and park road pages (R67).
  - A click on an event line shows the name, the roads, the description and the dates. A road line shows its name and reason.
  - The mouse wheel does not zoom the map, so the page scrolls as usual. Use the + and − buttons.
  - If the map library or the tiles do not load, the page shows the drawn map of R67.
- Under the map: "NPS road events", one item for each closure (with the number of road parts), then "From alerts and park road pages".
- Status: done.

### R70. Map tiles without an API key

Request from the owner (edited for clarity), with a screenshot of the road map with "API KEY REQUIRED" on the tiles:

> Where do I put the carto.com key? (The map shows "API KEY REQUIRED".)

Requirements:

- The CARTO basemap tiles now need an API key. A key on a public page is not secret, so the page does not use CARTO.
- The road map uses the OpenStreetMap standard tiles (`tile.openstreetmap.org`). They need no key. The map shows "© OpenStreetMap contributors".
- In dark mode, a filter makes the tiles dark.
- Status: done.

### R71. NPS map tiles on the road map

Request from the owner (edited for clarity):

> Is it possible to use the NPS map instead? (Answer to the options: try option 1, the NPS Park Tiles.)

Requirements:

- The road map uses the NPS Park Tiles as the base map: "NPS Park Tiles Standard" in light mode and "NPS Park Tiles Slate" in dark mode.
- The NPS publishes these tiles as public web maps on ArcGIS Online (owner NPS_EGIS_AGOL). The page reads the tile address from the web map (`www.arcgis.com/sharing/rest/content/items/<id>/data`) when the first park map opens. Thus the page has no key in its code, and a new tile address from the NPS comes in automatically.
- The map shows "Map: NPS Park Tiles · © Mapbox · © OpenStreetMap contributors".
- Fallback: if the web map does not load in 8 seconds, or the first 3 tiles do not load, the map uses the OpenStreetMap tiles of R70 (with the dark filter in dark mode).
- Status: done.
