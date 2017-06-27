Preliminary Proposal Specifications

#1. AirBnb listing attractiveness
Description:
As an Airbnb host myself, it's interesting to understand what features make a listing attractive to guests. Intuitively, price, travel convenience, cleanness should constitute the most to attractiveness, but is it generally true or does it differ given other factors, such as urban/rural listings, different cities (planning to look at a couple of major cities in US/Canada),etc? I want to use both listing descriptions and review comments to determine whether there's a link between what's advertised and what guests actually observed and liked/disliked through NLP and different clustering rules (e.g. by ratings, neighborhoods, cities, etc). The question I want to answer is what features of a listing guests speak about the most in order to provide a guidance to hosts



Data availability:
Scraped listing/calendar/review data are available at http://insideairbnb.com/get-the-data.html by cities with the last scrape date as at April 2017. Listing data include all information about a particular listing on Airbnb, such as descriptions, house rules, ratings, prices, availability, etc, sorted by listing ID. Review data includes review comments from each guest corresponding to the listing ID.

Occupancy rate and revenue data might be very useful for this analysis, but is not available through the above site. They are available through another website https://www.airdna.co/services/datafeed but not feasible due to the cost of data ($500/city). Alternatively, the monthly number of reviews could be a strong indicator of attractiveness of any listing and could be used to support my findings.

Presentation:
Charts and graphs will be the primary forms of Presentation for relationship digging.

#2.Vehicle specs vs CO2 emission and their relationship with sales historically

Description:
There are two questions I would like to explore:
1. What's the CO2 emission score given the specs of a vehicle? I want to build a regression model by looking at vehicle specs such as make, model, model year, MPG, fuel type, etc. to predict the EPA (US Environmental Protection Agency) tested emission scores (smog ratings 1-10).
2. Has the mindset of fuel efficiency and/or environmentally friendliness affected consumers' purchase preferences over time? I would like to explore the relationship between change in fuel efficiency/emissions and change in sales trend over the years for each vehicle model sold in the U.S from 2000 to 2017.

Data availability:
I have found comprehensive vehicle specs data with model history dated back to 1985 as well their emissions data as measured by EPA from this public site: http://www.fueleconomy.gov/feg/ws/index.shtml#emissions.

In order to answer question 2, I will need US car sales data for a reasonable historical period (ideally since 2000). A web based source seems to be providing this information for free (http://www.goodcarbadcar.net/p/sales-stats.html), but it's by user selecting a brand and model to display the sales data. Potentially web scraping might be needed if no other sources can be found.


#3. Flights Rewards comparisons

My Preliminary idea is to explore which flight points rewards system offers the most benefits based on users redemption histories on flights. However it's difficult to collect the data for this idea at least I haven't come across any free sources for this data. 
