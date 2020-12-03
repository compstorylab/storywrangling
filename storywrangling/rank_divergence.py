
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
from datetime import datetime
from typing import Optional

import resources
from storywrangling.query import Query


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RankDivergence:

    def __init__(self) -> None:
        """Python API to access the rank divergence database"""

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

    def get_divergence(self,
                       date: datetime,
                       database: str = '1grams',
                       max_rank: Optional[int] = None,
                       rt: bool = True) -> pd.DataFrame:
        """Get a list of narratively dominant ngrams for a given day

        Args:
            date: target date
            database: target ngram collection ("1grams", "2grams")
            max_rank: Max rank cutoff (default is None)
            rt: a toggle to include or exclude RTs

        Returns (pd.DataFrame):
            dataframe of ngrams
        """

        logger.info(
            f"Retrieving {self.divergence_languages.get('en')} {database} divergence ngrams for {date.date()} ..."
        )

        q = Query(("rd_"+database), 'en')
        df = q.query_divergence(date, max_rank=max_rank, rt=rt)
        df.index.name = 'ngram'
        return df

