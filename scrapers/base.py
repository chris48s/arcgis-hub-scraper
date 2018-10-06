import abc
import scraperwiki
from .common import dump_table, sync_file_to_github


class BaseScraper(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def table_name(self):
        pass

    def __init__(self, commit_result, data_repo=None):
        self.commit_result = commit_result
        self.data_repo = data_repo
        scraperwiki.sql.execute("""
            CREATE TABLE IF NOT EXISTS {} (url TEXT);
        """.format(self.table_name))
        scraperwiki.sql.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            {table}_url_unique ON {table} (url);
        """.format(table=self.table_name))

    @abc.abstractmethod
    def scrape(self):
        pass

    def sync(self):
        if self.commit_result and self.data_repo:
            sync_file_to_github(
                self.data_repo,
                '{}.json'.format(self.table_name),
                dump_table(self.table_name)
            )
