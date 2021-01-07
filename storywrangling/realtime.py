
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


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Realtime:

    def __init__(self) -> None:
        """Python API to access the realtime database"""

        with pkg_resources.open_binary(resources, 'ngrams.bin') as f:
            self.parser = pickle.load(f)

        with pkg_resources.open_binary(resources, 'realtime_languages.json') as f:
            self.supported_languages = ujson.load(f)

    def get_ngram(self, ngram: str, lang: str = 'en', case_insensitive: bool = False) -> pd.DataFrame:
        """RealtimeQuery database for an ngram timeseries

        Args:
            ngram: target ngram
            lang: target language (iso code)
            case_insensitive: a toggle for case sensitivity

        Returns:
            dataframe of ngrams usage over time
        """
        if self.supported_languages.get(lang) is not None:
            logging.info(f"Retrieving {self.supported_languages.get(lang)}: '{ngram}'")

            q = RealtimeQuery('realtime_1grams', lang)
            df = q.query_ngram(ngram, case_insensitive)
            df.index.name = 'time'
            df.index = pd.to_datetime(df.index)
            return df

        else:
            logger.warning(f"Unsupported language: {lang}")

    def get_ngrams_array(self, ngrams_list: list, lang: str = 'en', case_insensitive: bool = False) -> pd.DataFrame:
        """RealtimeQuery database for an array ngram timeseries

        Args:
            ngrams_list: list of strings to query mongo
            lang: target language (iso code)
            case_insensitive: a toggle for case sensitivity

        Returns:
            dataframe of ngrams usage over time
        """
        if self.supported_languages.get(lang) is not None:
            logger.info(f"Retrieving: {len(ngrams_list)} 1grams ...")

            q = RealtimeQuery('realtime_1grams', lang)
            df = q.query_ngrams_array(ngrams_list, case_insensitive)
            df['time'] = pd.to_datetime(df['time'])
            df.set_index(['time', 'ngram'], inplace=True)
            return df

        else:
            logger.warning(f"Unsupported language: {lang}")

    def get_ngrams_tuples(self, ngrams_list: [(str, str)], case_insensitive: bool = False) -> pd.DataFrame:
        """RealtimeQuery database for an array ngram timeseries

        Args:
            ngrams_list: list of tuples (ngram, lang)
            case_insensitive: a toggle for case sensitivity

        Returns:
            dataframe of ngrams usage over time
        """

        ngrams = []
        pbar = tqdm(ngrams_list, desc='Retrieving', leave=True, unit="")

        for w, lang in pbar:
            pbar.set_description(f"Retrieving: ({self.supported_languages.get(lang)}) {w.rstrip()}")

            q = RealtimeQuery('realtime_1grams', lang)
            df = q.query_ngram(w, case_insensitive)

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
                      case_insensitive: bool = False,
                      max_rank: Optional[int] = None,
                      min_count: Optional[int] = None,
                      rt: bool = True) -> pd.DataFrame:
        """Query database for ngram Zipf distribution for a given 15-minute batch

        Args:
            dtime: target datetime
            lang: target language (iso code)
            case_insensitive: a toggle for case sensitivity
            max_rank: Max rank cutoff (default is None)
            min_count: min count cutoff (default is None)
            rt: a toggle to include or exclude RTs

        Returns:
            dataframe of ngrams
        """

        if self.supported_languages.get(lang) is not None:
            q = RealtimeQuery('realtime_1grams', lang)

            if dtime is None or dtime > q.last_updated:
                dtime = q.last_updated
            else:
                dtime = pd.Timestamp(dtime).round(q.time_resolution).to_pydatetime()

            if q.reference_date <= dtime <= q.last_updated:
                logger.info(f"Retrieving {self.supported_languages.get(lang)} 1grams for {dtime} ...")

                df = q.query_batch(
                    dtime,
                    case_insensitive=case_insensitive,
                    max_rank=max_rank,
                    min_count=min_count,
                    rt=rt
                )
                df.index.name = 'ngram'
                return df

            else:
                logger.warning(f"Datatime should be within the last 10 days")
        else:
            logger.warning(f"Unsupported language: {lang}")
