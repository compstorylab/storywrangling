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


class Languages:

    def __init__(self) -> None:
        """Python API to access the language database"""

        self.supported_languages = ujson.load(
            pkg_resources.open_binary(resources, 'supported_languages.json')
        )

    def get_lang(self,
                 lang: Optional[str] = None,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None) -> pd.DataFrame:
        """Query database for language usage timeseries

        Args:
            lang: target language (iso code) [default: '_all]
            start_time: starting date for the query [default: 2010-01-01]
            end_time: ending date for the query [default: today]

        Returns:
            dataframe of language over time
        """

        q = Query("languages", "languages")

        logging.info(f"Retrieving: {lang} -- {self.supported_languages.get(lang)}")

        if self.supported_languages.get(lang) is not None:
            df = q.query_languages(
                lang,
                start_time,
                end_time,
            )
            df.index = pd.to_datetime(df.index)
            df.index.name = 'time'
            return df
        else:
            logger.warning(f"Unsupported language: {lang}")
