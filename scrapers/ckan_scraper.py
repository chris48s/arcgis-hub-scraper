import requests
import scraperwiki
from .base import BaseScraper


class CkanScraper(BaseScraper):

    @property
    def table_name(self):
        return 'ckan'

    def is_interesting_site(self, site):
        tlds = ['.uk', '.london', '.scot', '.wales', '.cymru']
        for tld in tlds:
            if tld in site['url']:
                return True

        return False

    def scrape(self):
        instances_url = 'https://ckan.github.io/ckan-instances/config/instances.json'
        print('🔍 searching {} ...'.format(instances_url))
        r = requests.get(instances_url)
        r.raise_for_status()
        data = r.json()
        for site in data:
            if self.is_interesting_site(site):
                site_url = site['url']
                print('👀 found {}'.format(site_url))
                scraperwiki.sqlite.save(
                    unique_keys=['url'], data={'url': site_url}, table_name=self.table_name)
                scraperwiki.sqlite.commit_transactions()
