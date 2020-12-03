
import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

try:
    sys.path.remove(str(parent))
except ValueError:
    pass

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

import logging
import ujson
import pickle
import pandas as pd
from tqdm import tqdm
from typing import Optional
from datetime import datetime

import resources
from storywrangling.query import Query
from storywrangling.regexr import nparser


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Storywrangler:

    def __init__(self) -> None:
        """Python API to access the Storywrangler database"""

        self.parser = pickle.load(
            pkg_resources.open_binary(resources, 'ngrams.bin')
        )
        self.supported_languages = ujson.load(
            pkg_resources.open_binary(resources, 'supported_languages.json')
        )
        self.indexed_languages = ujson.load(
            pkg_resources.open_binary(resources, 'indexed_languages.json')
        )
        self.divergence_languages = ujson.load(
            pkg_resources.open_binary(resources, 'divergence_languages.json')
        )

    def check_if_indexed(self, language: str, n: int) -> int:
        """Returns the requested number, if supported, or 1, if requested is not supported
        Args:
            language: target language (iso code)
            n: number of ngrams requested

        Returns:
            number of ngrams to search, based on what is indexed

        """
        if language in self.indexed_languages[str(n)+'grams']:
            logging.info(f"{language} {n}grams are indexed")
            return n
        else:
            logging.info(f"{language} {n}grams are not indexed yet")
            return 1

    def get_ngram(self,
                  ngram: str,
                  lang: str = 'en',
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  only_indexed: bool = False) -> pd.DataFrame:
        """Query database for an n-gram timeseries

        Args:
            ngram: target ngram
            lang: target language (iso code)
            start_time: starting date for the query
            end_time: ending date for the query
            only_indexed: only search ngrams that are indexed;
            if true, return dfs for each 1gram, stacked on top of one another

        Returns:
            dataframe of ngrams usage over time
        """

        n = len(nparser(ngram, parser=self.parser, n=1))

        if self.check_if_indexed(lang, n) != n:

            logger.warning(f"{n}grams not indexed for {lang}")

            if only_indexed:

                q = Query(f"1grams", lang)

                if self.supported_languages.get(lang) is not None:
                    ngrams = list(nparser(ngram, parser=self.parser, n=1).keys())

                    df = q.query_ngrams_array(
                        ngrams,
                        start_time=start_time,
                        end_time=end_time,
                    )
                    df['time'] = pd.to_datetime(df['time'])
                    df.set_index(['time', 'ngram'], inplace=True)
                    return df
                else:
                    logger.warning(f"Unsupported language: {lang}")

        else:
            q = Query(f"{n}grams", lang)

            if self.supported_languages.get(lang) is not None:
                logging.info(f"Retrieving {self.supported_languages.get(lang)}: {n}gram -- '{ngram}'")

                df = q.query_ngram(
                    ngram,
                    start_time=start_time,
                    end_time=end_time,
                )

                df.index.name = 'time'
                df.index = pd.to_datetime(df.index)
                return df

            else:
                logger.warning(f"Unsupported language: {lang}")

    def get_ngrams_array(self,
                         ngrams_list: list,
                         database: str,
                         lang: str = 'en',
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None):
        """Query database for an array n-gram timeseries

        Args:
            ngrams_list (list): list of strings to query mongo
            database (string): target ngram collection ("1grams", "2grams", "3grams")
            lang (string): target language (iso code)
            start_time (datetime): starting date for the query
            end_time (datetime): ending date for the query

        Returns (pd.DataFrame):
            dataframe of ngrams usage over time
        """

        q = Query(database, lang)

        if self.supported_languages.get(lang) is not None:
            logger.info(f"Retrieving: {len(ngrams_list)} {database} ...")

            df = q.query_ngrams_array(
                ngrams_list,
                start_time=start_time,
                end_time=end_time,
            )
            df['time'] = pd.to_datetime(df['time'])
            df.set_index(['time', 'ngram'], inplace=True)
            return df

        else:
            logger.warning(f"Unsupported language: {lang}")

    def get_ngrams_tuples(self,
                          ngrams_list,
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None):
        """Query database for an array n-gram timeseries

        Args:
            ngrams_list (list(tuples)): list of tuples (ngram, lang)
            start_time (datetime): starting date for the query
            end_time (datetime): ending date for the query

        Returns (list):
            a list of dataframes of for each ngram
        """

        ngrams = []
        pbar = tqdm(ngrams_list, desc='Retrieving', leave=True, unit="")

        for w, lang in pbar:
            n = len(nparser(w, parser=self.parser, n=1))
            pbar.set_description(f"Retrieving: ({self.supported_languages.get(lang)}) {w.rstrip()}")

            q = Query(f"{n}grams", lang)
            df = q.query_ngram(
                w,
                start_time=start_time,
                end_time=end_time,
            )

            df["ngram"] = w
            df["lang"] = self.supported_languages.get(lang) \
                if self.supported_languages.get(lang) is not None else "All"

            df.index.name = 'time'
            df.index = pd.to_datetime(df.index)
            df.set_index([df.index, 'ngram', 'lang'], inplace=True)
            ngrams.append(df)
            pbar.refresh()

        ngrams = pd.concat(ngrams)
        return ngrams

    def get_zipf_dist(self,
                      date: datetime,
                      lang: str = 'en',
                      database: str = '1grams',
                      max_rank: Optional[int] = None,
                      min_count: Optional[int] = None,
                      rt: bool = True):
        """Query database for an array n-gram timeseries

        Args:
            date (datetime): target date
            lang (string): target language (iso code)
            database (string): target ngram collection ("1grams", "2grams", "3grams")
            max_rank (int): Max rank cutoff (default is None)
            min_count (int): min count cutoff (default is None)
            rt (bool): a toggle to include or exclude RTs

        Returns (pd.DataFrame):
            dataframe of ngrams
        """

        if self.supported_languages.get(lang) is not None:
            logger.info(f"Retrieving {self.supported_languages.get(lang)} {database} for {date.date()} ...")

            q = Query(database, lang)
            df = q.query_day(date, max_rank=max_rank, min_count=min_count, rt=rt)
            df.index.name = 'ngram'
            return df

        else:
            logger.warning(f"Unsupported language: {lang}")

