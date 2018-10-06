import requests
import scraperwiki
from .base import BaseScraper


class Paginator:
    def __init__(self, page1):
        self.next_page = page1

    def __iter__(self):
        while self.next_page:
            print('🔍 searching {} ...'.format(self.next_page))

            r = requests.get(self.next_page)
            r.raise_for_status()
            data = r.json()

            try:
                self.next_page = data['links']['next']
            except KeyError:
                self.next_page = None

            yield data

        raise StopIteration()


class ArcGisHubScraper(BaseScraper):

    @property
    def table_name(self):
        return 'arcgis_hub'

    def is_interesting_site(self, site):
        try:
            if site['attributes']['defaultExtent']['spatialReference']['wkid'] == 27700:
                return True
        except KeyError:
            pass

        if 'gov.uk' in site['attributes']['url']:
            return True

        try:
            if site['attributes']['defaultExtent']['spatialReference']['wkid'] == 4326:
                if (
                    site['attributes']['defaultExtent']['xmin'] > -9 and
                    site['attributes']['defaultExtent']['xmax'] < 2 and
                    site['attributes']['defaultExtent']['ymin'] > 49 and
                    site['attributes']['defaultExtent']['ymax'] < 61
                ):
                    return True
        except KeyError:
            pass

        return False

    def process_page(self, page):
        for site in page['data']:
            if self.is_interesting_site(site):
                url = site['attributes']['url']
                scraperwiki.sqlite.save(
                    unique_keys=['url'], data={'url': url}, table_name=self.table_name)
                scraperwiki.sqlite.commit_transactions()
                print('👀 found {}'.format(url))

    def scrape(self):
        pages = Paginator('https://opendata.arcgis.com/api/v2/sites?page[number]=1&page[size]=500')
        for p in pages:
            self.process_page(p)
