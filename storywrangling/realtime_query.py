
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

import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import Optional
from datetime import datetime, timedelta
from pymongo import MongoClient

import ujson
import resources


class RealtimeQuery:
    """Class to work with n-gram db"""

    def __init__(self, db: str, lang: str) -> None:
        """Python wrapper to access database on hydra.uvm.edu

        Args:
            db: database to use
            lang: language collection to use
        """
        with pkg_resources.open_binary(resources, 'client.json') as f:
            self.credentials = ujson.load(f)

        client = MongoClient(
            f"{self.credentials['database']}://"
            f"{self.credentials['username']}:"
            f"{self.credentials['pwd']}"
            f"@{self.credentials['domain']}:"
            f"{self.credentials['port']}"
        )
        db = client[db]

        self.database = db[lang]
        self.lang = lang

        self.time_resolution = '15min'
        self.lag = timedelta(hours=3)
        self.timespan = timedelta(days=10)
        self.now = pd.Timestamp.now().round(self.time_resolution).to_pydatetime()
        self.reference_date = self.now - self.timespan
        self.last_updated = self.now - self.lag

        self.cols = [
            "count",
            "count_no_rt",
            "rank",
            "rank_no_rt",
            "freq",
            "freq_no_rt"
        ]

    def prepare_data(self, query: dict, cols: list) -> dict:
        return {
            t: {c: np.nan for c in cols}
            for t in pd.date_range(
                start=query["time"]["$gte"],
                end=query["time"]["$lte"],
                freq="15min",
            ).round(self.time_resolution).to_pydatetime().tolist()
        }

    def prepare_ngram_query(self, word: str) -> (dict, dict):
        query = {
            "word": {"$in": word} if type(word) is list else word,
            "time": {
                "$gte": self.reference_date,
                "$lte": self.last_updated,
            }
        }
        return query, self.prepare_data(query, self.cols)

    def prepare_day_query(self,
                          date: datetime,
                          max_rank: Optional[int] = None,
                          min_count: Optional[int] = None,
                          rt: bool = True) -> dict:
        if max_rank:
            if rt:
                return {
                    "time": date if date else self.last_updated,
                    "rank": {"$lte": max_rank}
                }
            else:
                return {
                    "time": date if date else self.last_updated,
                    "rank_no_rt": {"$lte": max_rank}
                }

        elif min_count:
            if rt:
                return {
                    "time": date if date else self.last_updated,
                    "count": {"$gte": min_count}
                }
            else:
                return {
                    "time": date if date else self.last_updated,
                    "count_no_rt": {"$gte": min_count}
                }

        else:
            return {"time": date if date else self.last_updated}

    def query_ngram(self, word) -> pd.DataFrame:
        """Query database for n-gram timeseries

        Args:
            word: target ngram

        Returns:
            dataframe of ngrams usage over time
        """
        query, data = self.prepare_ngram_query(word)

        for i in self.database.find(query):
            d = i["time"]
            for c in self.cols:
                data[d][c] = i[c]

        df = pd.DataFrame.from_dict(data=data, orient="index")
        return df

    def query_ngrams_array(self, word_list: list) -> pd.DataFrame:
        """Query database for an array n-gram timeseries

        Args:
            word_list: list of strings to query mongo

        Returns:
            dataframe of ngrams usage over time
        """

        query, data = self.prepare_ngram_query(word_list)

        df = pd.DataFrame(list(self.database.find(query)))
        df.set_index("word", inplace=True, drop=False)

        tl_df = pd.DataFrame(word_list)
        tl_df.set_index(0, inplace=True)

        df = tl_df.join(df)
        df["word"] = df.index
        df.drop("_id", axis=1, inplace=True)
        df.rename(columns={"word": "ngram"}, inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    def query_batch(self,
                    dtime: datetime,
                    max_rank: Optional[int] = None,
                    min_count: Optional[int] = None,
                    rt: bool = True):
        """Query database for all ngrams in a single day

        Args:
            dtime: target datetime
            max_rank: Max rank cutoff
            min_count: min count cutoff
            rt: a toggle to include or exclude RTs

        Returns:
            dataframe of ngrams
        """
        query = self.prepare_day_query(dtime, max_rank, min_count, rt)

        zipf = {}
        for t in tqdm(
                self.database.find(query),
                desc="Retrieving ngrams",
                unit=""
        ):
            zipf[t["word"]] = {}
            for c in self.cols:
                zipf[t["word"]][c] = t[c]

        df = pd.DataFrame.from_dict(data=zipf, orient="index")
        if rt:
            df.sort_values(by='count', ascending=False, inplace=True)
        else:
            df.sort_values(by='count_no_rt', ascending=False, inplace=True)

        return df
