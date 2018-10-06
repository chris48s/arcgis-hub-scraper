from scrapers.arcgis_scraper import ArcGisHubScraper
from scrapers.ckan_scraper import CkanScraper

COMMIT_RESULT = True
DATA_REPO = 'DemocracyClub/open-data-portals'

classes = [ArcGisHubScraper, CkanScraper]

for class_ in classes:
    scraper = class_(COMMIT_RESULT, DATA_REPO)
    scraper.scrape()
    scraper.sync()
