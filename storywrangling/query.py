import logging
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
from datetime import datetime, timedelta
from pymongo.errors import ServerSelectionTimeoutError
from pymongo import MongoClient, ASCENDING, DESCENDING

import ujson
import resources


class Query:
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

        try:
            self.reference_date = list(self.database.find().sort([('time', ASCENDING)]).limit(1))[0]['time']
            self.last_updated = list(self.database.find().sort([('time', DESCENDING)]).limit(1))[0]['time']
        except KeyError:
            try:
                self.reference_date = list(self.database.find().sort([('time_2', ASCENDING)]).limit(1))[0]['time_2']
                self.last_updated = list(self.database.find().sort([('time_2', DESCENDING)]).limit(1))[0]['time_2']
            except KeyError:
                self.lag = timedelta(days=2)
                self.reference_date = datetime(2010, 1, 1)
                self.last_updated = datetime.today() - self.lag

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
            "rd_contribution_noRT",
            "normed_rd",
            "normed_rd_noRT",
            "rank_change",
            "rank_change_noRT",
            "rank_1",
            "rank_1_noRT",
            "rank_2",
            "rank_2_noRT",
            "time_1",
            "time_2",
        ]

        self.div_cols = [
            "rd_contribution",
            "rd_contribution_no_rt",
            "normed_rd",
            "normed_rd_no_rt",
            "rank_change",
            "rank_change_no_rt",
            "rank_1",
            "rank_1_no_rt",
            "rank_2",
            "rank_2_no_rt",
            "time_1",
            "time_2"
        ]

        # work around for inconsistent field names
        self.ngram_field_name = {
            "ngrams": "word",
            "rtd": "ngram"
        }

        self.ngram_filters = {
            "handles": r"(@\S+)",
            "hashtags": r"(#\S+)",
            "handles_hashtags": r"([@|#]\S+)",
            "no_handles_hashtags": "(?![\@\#])([\S]+)",
            "latin": r"([A-Za-z0-9]+[\‘\’\'\-]?[A-Za-z0-9]+)",
            "no_punc": r"([!…”“\"#@$%&'\(\)\*\+\,\-\.\/\:\;<\=>?@\[\]\^_{|}~]+)"
        }

        self.exclude_regex = ["no_punc"]  # regexes operating with $not operator

    def prepare_data(self, query: dict, cols: list) -> dict:
        return {
            d: {c: np.nan for c in cols}
            for d in pd.date_range(
                start=query["time"]["$gte"].date(),
                end=query["time"]["$lte"].date(),
                freq="D",
            ).date
        }

    def prepare_rank_query(
            self,
            rank: int,
            start: Optional[datetime] = None,
            end: Optional[datetime] = None
    ) -> (dict, dict):

        query = {
            "rank": rank,
            "time": {
                "$gte": start if start else self.reference_date,
                "$lte": end if end else self.last_updated,
            }
        }
        return query, self.prepare_data(query, self.cols)

    def prepare_ngram_query(self,
                            word: Union[str, list],
                            start: Optional[datetime] = None,
                            end: Optional[datetime] = None) -> (dict, dict):
        query = {
            "word": {"$in": word} if type(word) is list else word,
            "time": {
                "$gte": start if start else self.reference_date,
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
                "$gte": start if start else self.reference_date,
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
                    "rank_noRT": {"$lte": max_rank}
                }

        elif min_count:
            if rt:
                return {
                    "time": date if date else self.last_updated,
                    "counts": {"$gte": min_count}
                }
            else:
                return {
                    "time": date if date else self.last_updated,
                    "count_noRT": {"$gte": min_count}
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

    def prepare_rd_timeseries_query(self,
                                    dates: tuple,
                                    rt: bool = True) -> dict:
        if rt:
            return {"time_2": {"$gte": dates[0], "$lte": dates[1]},
                    "rank_change": {"$lte": 1, "$gt": 0}
                    }
        else:
            return {"time_2": {"$gte": dates[0], "$lte": dates[1]},
                    "rank_change_noRT": {"$lte": 1, "$gt": 0}
                    }

    def prepare_query_filter(self,
                             ngram_order: int,
                             query: dict,
                             filter_name: str,
                             db_type: str):

        if filter_name in self.exclude_regex:
            regex_pattern = self.ngram_filters[filter_name]
            regex_filter = {self.ngram_field_name[db_type]: {"$not": {"$regex": regex_pattern}}}
        else:
            regex_pattern = r"^" + " ".join([self.ngram_filters[filter_name]] * ngram_order) + "$"
            regex_filter = {self.ngram_field_name[db_type]: {"$regex": regex_pattern}}

        return {**query, **regex_filter}

    def query_rank(
            self,
            rank: int,
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None
    ) -> pd.DataFrame:

        """Query database for rank timeseries

        Args:
            rank: target rank
            start_time: starting date for the query
            end_time: ending date for the query

        Returns:
            dataframe of ngrams usage over time
        """
        query, data = self.prepare_rank_query(rank, start_time, end_time)

        df = pd.DataFrame(tqdm(
            self.database.find(query),
            desc="Retrieving ngrams",
            unit="",
            total=len(data.keys())
        ))

        cols = {"word": "ngram"}
        cols.update(dict(zip(self.db_cols, self.cols)))
        df = df.rename(columns=cols).set_index('time')
        df = df[cols.values()].sort_index().drop_duplicates()
        return df.asfreq('D')

    def query_ngram(self,
                    word,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None) -> pd.DataFrame:
        """Query database for n-gram timeseries

        Args:
            word: target ngram
            start_time: starting date for the query
            end_time: ending date for the query

        Returns:
            dataframe of ngrams usage over time
        """
        query, data = self.prepare_ngram_query(word, start_time, end_time)

        for i in self.database.find(query):
            d = i["time"].date()
            for c, db in zip(self.cols, self.db_cols):
                try:
                    data[d][c] = i[db]
                except KeyError:
                    logging.error(f'Database field names have changed for {d}')

        df = pd.DataFrame.from_dict(data=data, orient="index")
        return df

    def query_ngrams_array(self,
                           word_list: list,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> pd.DataFrame:
        """Query database for an array n-gram timeseries

        Args:
            word_list: list of strings to query mongo
            start_time: starting date for the query
            end_time: ending date for the query

        Returns:
            dataframe of ngrams usage over time
        """

        query, data = self.prepare_ngram_query(word_list, start_time, end_time)

        df = pd.DataFrame(list(self.database.find(query)))
        df.set_index("word", inplace=True, drop=False)

        tl_df = pd.DataFrame(word_list)
        tl_df.set_index(0, inplace=True)

        df = tl_df.join(df)
        df["word"] = df.index
        df.drop("_id", axis=1, inplace=True)
        cols = {d: k for d, k in zip(self.db_cols, self.cols)}
        cols.update({"word": "ngram"})
        df.rename(columns=cols, inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    def query_languages(self,
                        lang: str,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> pd.DataFrame:
        """Query database for language timeseries

        Args:
            lang: target language
            start_time: starting date for the query
            end_time: ending date for the query

        Returns:
            dataframe of language over time
        """
        query, data = self.prepare_lang_query(lang, start_time, end_time)

        for i in self.database.find(query):
            d = i["time"].date()
            for c in self.lang_cols:
                try:
                    if np.isnan(data[d][c]):
                        data[d][c] = i[c]
                    else:
                        data[d][c] += i[c]
                except KeyError:
                    pass

        df = pd.DataFrame.from_dict(data=data, orient="index")
        df.columns = df.columns.str.replace(r"ft_", "")

        df["count_no_rt"] = df["count"] - df["retweets"]
        df["rank_no_rt"] = df["count_no_rt"].rank(method="average", ascending=False)
        df["freq_no_rt"] = df["count_no_rt"] / df["count_no_rt"].sum()
        return df

    def query_day(self,
                  date: datetime,
                  max_rank: Optional[int] = None,
                  min_count: Optional[int] = None,
                  top_n: Optional[int] = None,
                  rt: bool = True,
                  ngram_order: int = 1,
                  ngram_filter: Optional[str] = None):

        """Query database for all ngrams in a single day

        Args:
            date: target date
            max_rank: Max rank cutoff
            min_count: min count cutof
            rt: a toggle to apply the filters above on ATs or OTs (w/out RTs)
            top_n: maximum number of ngrams to return
            ngram_order: n_gram order
            ngram_filter: name of regex filter for ngrams
            (handles, hashtags, handles_hashtags, no_handles_hashtags, or latin)

        Returns:
            dataframe of ngrams
        """

        query = self.prepare_day_query(date, max_rank, min_count, rt)

        if ngram_filter:
            query = self.prepare_query_filter(ngram_order, query, ngram_filter, db_type='ngrams')

        if top_n:
            cur = self.database.aggregate([{'$match': query}, {'$limit': top_n}])
        else:
            cur = self.database.find(query)

        zipf = {}
        for t in tqdm(
                cur,
                desc="Retrieving ngrams",
                unit=""
        ):
            zipf[t["word"]] = {}
            for c, db in zip(self.cols, self.db_cols):
                try:
                    zipf[t["word"]][c] = t[db]
                except KeyError:
                    logging.error('Database field names have changed!!')

        df = pd.DataFrame.from_dict(data=zipf, orient="index")
        if rt:
            df.sort_values(by='count', ascending=False, inplace=True)
        else:
            df.sort_values(by='count_no_rt', ascending=False, inplace=True)

        return df

    def query_divergence(self,
                         date: datetime,
                         max_rank: Optional[int] = None,
                         top_n: Optional[int] = None,
                         rt: bool = True,
                         ngram_order: int = 1,
                         ngram_filter: Optional[str] = None
                         ) -> pd.DataFrame:
        """Query database for a list of narratively dominant ngrams for a given day

        Args:
            date: target date
            max_rank: Max rank cutoff
            rt: a toggle to apply the filters above on ATs or OTs (w/out RTs)
            top_n: maximum number of ngrams to return
            ngram_order: n_gram order
            ngram_filter: name of regex filter for ngrams
            (handles, hashtags, handles_hashtags, no_handles_hashtags, or latin)

        Returns:
            dataframe of ngrams sorted by their rank div contributions
        """
        query = self.prepare_divergence_query(date, max_rank, rt)

        if ngram_filter:
            query = self.prepare_query_filter(ngram_order, query, ngram_filter, db_type='rtd')

        if top_n:
            cur = self.database.aggregate([{'$match': query}, {'$limit': top_n}])
        else:
            cur = self.database.find(query)

        div = {}
        for t in tqdm(
                cur,
                desc="Retrieving ngrams",
                unit=""
        ):
            div[t["ngram"]] = {}
            for c, db in zip(self.div_cols, self.db_div_cols):
                try:
                    div[t["ngram"]][c] = t[db]
                except KeyError:
                    logging.error('Database field names have changed!!')

        df = pd.DataFrame.from_dict(data=div, orient="index")
        if rt:
            df.sort_values(by='rd_contribution', ascending=False, inplace=True)
        else:
            df.sort_values(by='rd_contribution_no_rt', ascending=False, inplace=True)

        return df

    def query_rd_timeseries(self,
                            dates: tuple,
                            rt: bool = True,
                            ) -> pd.DataFrame:
        """ Query database for a list of top ngrams over a daterange

        Args:
            dates: a tuple of datetimes for start and end dates
            rt: a toggle to search ATs or OTs

        Returns:
            dataframe of ngrams with a DatetimeIndex
        """
        query = self.prepare_rd_timeseries_query(dates, rt)
        cur = self.database.find(query)

        div = {}
        for t in tqdm(
                cur,
                desc="Retrieving ngrams",
                unit=""
        ):
            div[t["ngram"]] = {}
            for c, db in zip(self.div_cols, self.db_div_cols):
                try:
                    div[t["ngram"]][c] = t[db]
                except KeyError:
                    logging.error('Database field names have changed!!')

        df = pd.DataFrame.from_dict(data=div, orient="index")
        return df
