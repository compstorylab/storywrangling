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

import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import Optional, Union
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.cursor import Cursor
from pymongo.errors import ServerSelectionTimeoutError

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

        try:
            client = MongoClient(
                f"{self.credentials['database']}://"
                f"{self.credentials['username']}:"
                f"{self.credentials['pwd']}"
                f"@{self.credentials['domain']}:"
                f"{self.credentials['port']}",
                serverSelectionTimeoutMS=5000,
                connect=True
            )
            client.server_info()

        except ServerSelectionTimeoutError:
            client = MongoClient(
                f"{self.credentials['database']}://"
                f"{self.credentials['username']}:"
                f"{self.credentials['pwd']}"
                f"@localhost:"
                f"{self.credentials['port']}",
                serverSelectionTimeoutMS=5000
            )

        db = client[db]
        self.database = db[lang]
        self.lang = lang

        self.time_resolution = '15min'
        self.reference_date = list(self.database.find().sort([('time', ASCENDING)]).limit(1))[0]['time']
        self.last_updated = list(self.database.find().sort([('time', DESCENDING)]).limit(1))[0]['time']

        self.cols = [
            "count",
            "count_no_rt",
            "rank",
            "rank_no_rt",
            "freq",
            "freq_no_rt",
            "r_rel"
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

    def prepare_ngram_query(self, word: Union[str, list]) -> (dict, dict):
        query = {
            "word": {"$in": word} if type(word) is list else word,
            "time": {
                "$gte": self.reference_date,
                "$lte": self.last_updated,
            }
        }
        return query, self.prepare_data(query, self.cols)

    def prepare_rank_query(self, rank: int) -> (dict, dict):
        query = {
            "rank": rank,
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

    def run_query(self, q: dict) -> Cursor:
        query = self.database.find(q)
        return query

    def query_ngram(self, word: str) -> pd.DataFrame:
        """Query database for n-gram timeseries

        Args:
            word: target ngram

        Returns:
            dataframe of ngrams usage over time
        """
        query, data = self.prepare_ngram_query(word)

        for i in self.run_query(query):
            d = i["time"]
            for c in self.cols:
                if np.isnan(data[d][c]):
                    data[d][c] = i[c]
                else:
                    # take top rank for case insensitive queries
                    if 'rank' in c:
                        data[d][c] = np.min([data[d][c], i[c]])
                    # add up counts and freqs for case insensitive queries
                    else:
                        data[d][c] += i[c]

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

        df = pd.DataFrame(
            self.run_query(query),
        ).rename(columns={"word": "ngram"})

        df = df.groupby(['time', 'ngram']).agg({
            'count': 'sum',
            'count_no_rt': 'sum',
            'freq': 'sum',
            'freq_no_rt': 'sum',
            'rank': 'min',
            'rank_no_rt': 'min',
            'r_rel': 'mean',
        })

        index = pd.MultiIndex.from_product([data.keys(), word_list], names=['time', 'ngram'])
        tl_df = pd.DataFrame(index=index)
        df = tl_df.join(df).reset_index()

        return df

    def query_batch(self,
                    dtime: datetime,
                    max_rank: Optional[int] = None,
                    min_count: Optional[int] = None,
                    rt: bool = True) -> pd.DataFrame:
        """Query database for all ngrams in a single day

        Args:
            dtime: target datetime
            max_rank: Max rank cutoff
            min_count: min count cutoff
            rt: a toggle to apply the filters above on ATs or OTs (w/out RTs)

        Returns:
            dataframe of ngrams
        """
        query = self.prepare_day_query(dtime, max_rank, min_count, rt)

        df = pd.DataFrame(tqdm(
            self.run_query(query),
            desc="Retrieving ngrams",
            unit=""
        )).rename(columns={"word": "ngram"})

        if not df.empty:
            df.drop(columns=['_id', 'time'], inplace=True)

            if rt:
                df.sort_values(by='count', ascending=False, inplace=True)
            else:
                df.sort_values(by='count_no_rt', ascending=False, inplace=True)

        return df
