from scrapers.arcgis_scraper import ArcGisHubScraper

COMMIT_RESULT = True
DATA_REPO = 'DemocracyClub/open-data-portals'

scraper = ArcGisHubScraper(COMMIT_RESULT, DATA_REPO)
scraper.scrape()
scraper.sync()
