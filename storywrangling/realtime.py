import warnings
warnings.filterwarnings("ignore")

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
from storywrangling import RealtimeQuery
from storywrangling.regexr import nparser


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Realtime:

    def __init__(self) -> None:
        """Python API to access the realtime database"""

        with pkg_resources.open_binary(resources, 'ngrams.bin') as f:
            self.parser = pickle.load(f)

        with pkg_resources.open_binary(resources, 'realtime_languages.json') as f:
            self.supported_languages = ujson.load(f)

    def get_ngram(self, ngram: str, lang: str = 'en') -> pd.DataFrame:
        """Query database for an ngram timeseries

        Args:
            ngram: target ngram
            lang: target language (iso code)

        Returns:
            dataframe of ngrams usage over time
        """
        if self.supported_languages.get(lang) is not None:
            ngram = ngram.lower()
            logging.info(f"Retrieving {self.supported_languages.get(lang)}: '{ngram}'")

            n = len(nparser(ngram, parser=self.parser, n=1))
            q = RealtimeQuery(f'realtime_{n}grams', lang)
            df = q.query_ngram(ngram)
            df.index.name = 'time'
            df.index = pd.to_datetime(df.index)
            return df

        else:
            logger.warning(f"Unsupported language: {lang}")

    def get_ngrams_array(self, ngrams_list: list, lang: str = 'en') -> pd.DataFrame:
        """Query database for an array ngram timeseries

        Args:
            ngrams_list: list of strings to query mongo
            lang: target language (iso code)

        Returns:
            dataframe of ngrams usage over time
        """
        if self.supported_languages.get(lang) is not None:
            ngrams_list = [w.lower() for w in ngrams_list]
            n = len(nparser(ngrams_list[0], parser=self.parser, n=1))
            logger.info(f"Retrieving timestamps for [{len(ngrams_list)}] {n}grams ...")

            q = RealtimeQuery(f'realtime_{n}grams', lang)
            df = q.query_ngrams_array(ngrams_list)
            df['time'] = pd.to_datetime(df['time'])
            df.set_index(['time', 'ngram'], inplace=True)
            return df

        else:
            logger.warning(f"Unsupported language: {lang}")

    def get_ngrams_tuples(self, ngrams_list: [(str, str)]) -> pd.DataFrame:
        """Query database for an array ngram timeseries

        Args:
            ngrams_list: list of tuples (ngram, lang)

        Returns:
            dataframe of ngrams usage over time
        """

        ngrams = []
        pbar = tqdm(ngrams_list, desc='Retrieving', leave=True, unit="")

        for w, lang in pbar:
            w = w.lower()
            pbar.set_description(f"Retrieving: ({self.supported_languages.get(lang)}) {w.rstrip()}")

            n = len(nparser(w, parser=self.parser, n=1))
            q = RealtimeQuery(f'realtime_{n}grams', lang)
            df = q.query_ngram(w)

            df["ngram"] = w
            df["lang"] = self.supported_languages.get(lang) \
                if self.supported_languages.get(lang) is not None else "en"

            df.index.name = 'time'
            df.index = pd.to_datetime(df.index)
            df.set_index([df.index, 'ngram', 'lang'], inplace=True)
            ngrams.append(df)
            pbar.refresh()

        ngrams = pd.concat(ngrams)
        return ngrams

    def get_zipf_dist(self,
                      dtime: Optional[datetime] = None,
                      lang: str = 'en',
                      ngrams: str = '1grams',
                      max_rank: Optional[int] = None,
                      min_count: Optional[int] = None,
                      rt: bool = True) -> pd.DataFrame:
        """Query database for ngram Zipf distribution for a given 15-minute batch

        Args:
            dtime: target datetime
            lang: target language (iso code)
            ngrams: target ngram collection ("1grams", "2grams")
            max_rank: Max rank cutoff (default is None)
            min_count: min count cutoff (default is None)
            rt: a toggle to apply the filters above on ATs or OTs (w/out RTs)

        Returns:
            dataframe of ngrams
        """

        if self.supported_languages.get(lang) is not None:
            q = RealtimeQuery(f'realtime_{ngrams}', lang)

            if dtime is None or dtime > q.last_updated:
                dtime = q.last_updated
            else:
                dtime = pd.Timestamp(dtime).round(q.time_resolution).to_pydatetime()

            if q.reference_date <= dtime <= q.last_updated:
                logger.info(f"Retrieving {self.supported_languages.get(lang)} {ngrams} for {dtime} ...")

                df = q.query_batch(
                    dtime,
                    max_rank=max_rank,
                    min_count=min_count,
                    rt=rt
                )
                df.index.name = 'ngram'
                return df

            else:
                logger.warning(f"Date should be within the last 30 days")
        else:
            logger.warning(f"Unsupported language: {lang}")
