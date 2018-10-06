import json
import os
import scraperwiki
from commitment import GitHubCredentials, GitHubClient

def sync_file_to_github(repo, filename, content):
    creds = GitHubCredentials(
        repo=repo,
        name=os.environ['MORPH_GITHUB_USERNAME'],
        email=os.environ['MORPH_GITHUB_EMAIL'],
        api_key=os.environ['MORPH_GITHUB_API_KEY']
    )
    g = GitHubClient(creds)
    g.push_file(content, filename, 'Found new ArcGIS Hub site')

def dump_table(table):
    records = scraperwiki.sqlite.select(" * FROM {} ORDER BY url;".format(table))
    return json.dumps([r['url'] for r in records], indent=4)
