import requests
import scraperwiki
from .base import BaseScraper
from requests_paginator import RequestsPaginator


def get_next_page(page):
    body = page.json()
    try:
        return body['links']['next']
    except KeyError:
        return None


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
                print('👀 found {}'.format(url))
                scraperwiki.sqlite.save(
                    unique_keys=['url'], data={'url': url}, table_name=self.table_name)
                scraperwiki.sqlite.commit_transactions()

    def scrape(self):
        pages = RequestsPaginator(
            'https://opendata.arcgis.com/api/v2/sites?page[number]=1&page[size]=500',
            get_next_page
        )
        for page in pages:
            page.raise_for_status()
            print('🔍 searching {} ...'.format(page.url))
            self.process_page(page.json())
