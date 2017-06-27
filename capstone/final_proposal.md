
Description: Airbnb User Experience Topic Modeling
As an Airbnb host myself, it's interesting to understand what features make a listing attractive to guests. Intuitively, price, travel convenience, cleanness should constitute the most to attractiveness, but is it generally true or does it differ given other factors, such as urban/rural listings, different cities (planning to look at a couple of major cities in US/Canada),etc? I want to perform analysis on both listing descriptions and review comments to determine whether there's a link between what's advertised and what guests actually observed and liked/disliked through LDA and different clustering rules (e.g. by ratings, neighborhoods, cities, etc). The question I want to answer is what features of a listing guests speak about the most in order to provide a guidance to hosts.

Presentation:
Primary presentation will be through slides and graphs. I will also explore potentials of creating a web app for an interactive UI for users to view findings across different cities or categories.

Data Source:
Scraped listing/calendar/review data are available at http://insideairbnb.com/get-the-data.html by cities with the last scrape date as at April 2017. Listing data include all information about a particular listing on Airbnb, such as descriptions, house rules, ratings, prices, availability, etc, sorted by listing ID. Review data includes review comments from each guest corresponding to the listing ID. This enables me to access a large amount of listing data which will hopefully help boost the performance of LDA.

Next Steps:
1. Get all the data available by cities and store them into a database structure (e.g PostgresSQL, MongoDB) on AWS for later easy access.
2. Perform Preliminary EDA to try to identify some trends that would hopefully steer the project into interesting directions that's not obvious at current state
