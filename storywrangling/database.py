import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import Optional
from datetime import datetime
from pymongo import MongoClient


class Database:
    """Class to work with n-gram db"""

    def __init__(self,
                 db: str,
                 lang: str,
                 username: str = "guest",
                 pwd: str = "roboctopus",
                 port="27017") -> None:
        """Python wrapper to access database on hydra.uvm.edu

        Args:
            db: database to use
            lang: language collection to use
            username: username to access database
            pwd: password to access database
        """
        client = MongoClient(f"mongodb://{username}:{pwd}@hydra.uvm.edu:{port}")
        db = client[db]

        self.database = db[lang]
        self.lang = lang

        self.db_cols = [
            "counts",
            "count_noRT",
            "rank",
            "rank_noRT",
            "freq",
            "freq_noRT",
        ]

        self.cols = [
            "count",
            "count_no_rt",
            "rank",
            "rank_no_rt",
            "freq",
            "freq_no_rt"
        ]

        self.lang_cols = [
            "ft_count",
            "ft_freq",
            "ft_rank",
            "ft_comments",
            "ft_retweets",
            "ft_speakers",
            "ft_tweets",
            "num_1grams",
            "num_2grams",
            "num_3grams",
            "unique_1grams",
            "unique_2grams",
            "unique_3grams",
            "num_1grams_no_rt",
            "num_2grams_no_rt",
            "num_3grams_no_rt",
            "unique_1grams_no_rt",
            "unique_2grams_no_rt",
            "unique_3grams_no_rt",
        ]

        self.db_div_cols = [
            "rd_contribution",
            "rank_change",
            "rd_contribution_noRT",
            "rank_change_noRT",
            "time_1",
            "time_2"
        ]

        self.div_cols = [
            "rd_contribution",
            "rank_change",
            "rd_contribution__no_rt",
            "rank_change_no_rt",
            "time_1",
            "time_2"
        ]

    def prepare_data(self, query: dict, cols: list) -> dict:
        return {
            d: {c: np.nan for c in cols}
            for d in pd.date_range(
                start=query["time"]["$gte"].date(),
                end=query["time"]["$lte"].date(),
                freq="D",
            ).date
        }

    def prepare_ngram_query(self,
                            word: str,
                            start: Optional[datetime] = None,
                            end: Optional[datetime] = None) -> (dict, dict):
        query = {
            "word": {"$in": word} if type(word) is list else word,
            "time": {
                "$gte": start if start else datetime(2010, 1, 1),
                "$lte": end if end else self.last_updated,
            }
        }
        return query, self.prepare_data(query, self.cols)

    def prepare_lang_query(self,
                           lang: str,
                           start: Optional[datetime] = None,
                           end: Optional[datetime] = None) -> (dict, dict):
        query = {
            "language": lang if lang else "_all",
            "time": {
                "$gte": start if start else datetime(2010, 1, 1),
                "$lte": end if end else self.last_updated,
            }
        }
        return query, self.prepare_data(query, self.lang_cols)

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

    def prepare_divergence_query(self,
                                 date: datetime,
                                 max_rank: Optional[int] = None,
                                 rt: bool = True) -> dict:
        if max_rank:
            if rt:
                return {
                    "time_2": date if date else self.last_updated,
                    "rank_change": {"$lte": max_rank, "$gte": -max_rank}
                }
            else:
                return {
                    "time_2": date if date else self.last_updated,
                    "rank_change_noRT": {"$lte": max_rank, "$gte": -max_rank}
                }

        else:
            return {"time_2": date if date else self.last_updated}
