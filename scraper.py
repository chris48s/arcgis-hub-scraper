import json
import os
import requests
from commitment import GitHubCredentials, GitHubClient


# hack to override sqlite database filename
# see: https://help.morph.io/t/using-python-3-with-morph-scraperwiki-fork/148
os.environ['SCRAPERWIKI_DATABASE_NAME'] = 'sqlite:///data.sqlite'
import scraperwiki


COMMIT_RESULT = True
DATA_REPO = 'DemocracyClub/arcgis-hub-sites'


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


def sync_file_to_github(repo, filename, content):
    creds = GitHubCredentials(
        repo=repo,
        name=os.environ['MORPH_GITHUB_USERNAME'],
        email=os.environ['MORPH_GITHUB_EMAIL'],
        api_key=os.environ['MORPH_GITHUB_API_KEY']
    )
    g = GitHubClient(creds)
    g.push_file(content, filename, 'Found new ArcGIS Hub site')

def is_interesting_site(site):
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

def process_page(page):
    for site in page['data']:
        if is_interesting_site(site):
            url = site['attributes']['url']
            scraperwiki.sqlite.save(
                unique_keys=['url'], data={'url': url}, table_name='data')
            scraperwiki.sqlite.commit_transactions()
            print('👀 found {}'.format(url))

def dump_table():
    records = scraperwiki.sqlite.select(" * FROM data ORDER BY url;")
    return json.dumps([r['url'] for r in records], indent=4)

def scrape():
    pages = Paginator('https://opendata.arcgis.com/api/v2/sites?page[number]=1&page[size]=500')
    for p in pages:
        process_page(p)
    if COMMIT_RESULT:
        sync_file_to_github(DATA_REPO, 'data.json', dump_table())

def init():
    scraperwiki.sql.execute("""
        CREATE TABLE IF NOT EXISTS data (url TEXT);
    """)
    scraperwiki.sql.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS data_url_unique ON data (url);
    """)


init()
scrape()
