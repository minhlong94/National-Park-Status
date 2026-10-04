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
- Status: partly done. The page shows all 63 parks, not only the top 20. The owner must decide which rule applies.

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
- Show the last 3 complete calendar years.
- Use vertical bars. Give each year a different color.
- Also show these historical monthly values:
  - the average low and high temperature
  - snow
  - rain
- Design choice: The page shows four separate charts with the same months (January to December). Each chart has one y-axis. When the reader points to a month in one chart, all charts show that month and one tooltip shows all the values for that month.
- A table view shows the same values.
- Data sources:
  - Visits: NPS Visitor Use Statistics (irmaservices.nps.gov).
  - Weather: Open-Meteo historical weather archive (archive-api.open-meteo.com). The page shows the average of the 3 years for each month.
- A GitHub Actions workflow gets the data and saves it in `data/park-history.js`.
- Status: in progress.
