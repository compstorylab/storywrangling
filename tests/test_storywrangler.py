import warnings

warnings.filterwarnings("ignore")

import sys

sys.path.append('./')

import logging
import unittest
import pandas as pd
from datetime import datetime
from storywrangling import Storywrangler


class NgramsTesting(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(NgramsTesting, self).__init__(*args, **kwargs)

        self.api = Storywrangler()

        self.start = datetime(2010, 1, 1)
        self.end = datetime(2020, 1, 1)

        self.rank_example = 100
        self.lang_example = "en"
        self.ngram_example = "Black Lives Matter"
        self.lang_isindexed_example = "fr"
        self.ngram_isindexed_example = "bonjour mon ami"
        self.array_example = ["Higgs", "#AlphaGo", "CRISPR", "#AI", "LIGO"]
        self.multilang_example = [
            ('😊', '_all'),
            ('2012', '_all'),
            ('2018', '_all'),
            ('Christmas', 'en'),
            ('Pasqua', 'it'),
            ('eleição', 'pt'),
            ('sommar', 'sv'),
            ('Olympics', 'en'),
            ('World Cup', 'en'),
            ('Super Bowl', 'en'),
            ('Higgs', 'en'),
            ('#AlphaGo', 'en'),
            ('gravitational waves', 'en'),
            ('CRISPR', 'en'),
            ('black hole', 'en'),
            ('Cristiano Ronaldo', 'pt'),
            ('Donald Trump', 'en'),
            ('Papa Francesco', 'it'),
            ('cholera', 'en'),
            ('Ebola', 'en'),
            ('Zika', 'en'),
            ('coronavirus', 'en'),
            ('غزة', 'ar'),
            ('Libye', 'fr'),
            ('Suriye', 'tr'),
            ('Росія', 'uk'),
            ('ثورة', 'ar'),
            ('Occupy', 'en'),
            ('Black Lives Matter', 'en'),
            ('Brexit', 'en'),
            ('#MeToo', 'en'),
        ]

        self.ngrams_cols = [
            "count",
            "count_no_rt",
            "rank",
            "rank_no_rt",
            "freq",
            "freq_no_rt"
        ]

        self.lang_cols = [
            "count",
            "freq",
            "rank",
            "comments",
            "retweets",
            "speakers",
            "tweets",
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

        self.ngram_filters = [
            "handles",
            "hashtags",
            "handles_hashtags",
            "no_handles_hashtags",
            "latin"
        ]

    def test_get_rank(self):
        df = self.api.get_rank(
            self.rank_example,
            self.lang_example,
            start_time=self.start,
            end_time=self.end
        )
        logging.info(df)
        assert not df.empty

    def test_get_ngram(self):
        df = self.api.get_ngram(
            self.ngram_example,
            self.lang_example,
            start_time=self.start,
            end_time=self.end
        )
        expected_df = pd.read_csv(
            "tests/ngram_example.tsv",
            index_col=0,
            parse_dates=True,
            header=0,
            sep='\t',
        )
        expected_df.index.name = 'time'

        pd.testing.assert_frame_equal(
            df[self.ngrams_cols],
            expected_df[self.ngrams_cols],
        )
        logging.info(df)

    def test_get_indexed_ngram(self):
        df = self.api.get_ngram(
            self.ngram_isindexed_example,
            self.lang_isindexed_example,
            start_time=self.start,
            end_time=self.end,
            only_indexed=True
        )

        expected_df = pd.read_csv(
            "tests/ngrams_indexed_only_example.tsv",
            parse_dates=True,
            header=0,
            sep='\t',
        )
        expected_df['time'] = pd.to_datetime(expected_df['time'])
        expected_df.set_index(['time', 'ngram'], inplace=True)

        pd.testing.assert_frame_equal(
            df[self.ngrams_cols],
            expected_df[self.ngrams_cols],
        )
        logging.info(df)

    def test_get_ngrams_array(self):
        df = self.api.get_ngrams_array(
            self.array_example,
            lang=self.lang_example,
            start_time=self.start,
            end_time=self.end,
        )
        expected_df = pd.read_csv(
            "tests/ngrams_array_example.tsv",
            parse_dates=True,
            header=0,
            sep='\t',
        )
        expected_df['time'] = pd.to_datetime(expected_df['time'])
        expected_df.set_index(['time', 'ngram'], inplace=True)

        pd.testing.assert_frame_equal(
            df[self.ngrams_cols],
            expected_df[self.ngrams_cols],
        )
        logging.info(df)

    def test_get_ngrams_tuples(self):
        df = self.api.get_ngrams_tuples(
            self.multilang_example,
            start_time=self.start,
            end_time=self.end,
        )
        expected_df = pd.read_csv(
            "tests/ngrams_multilang_example.tsv",
            parse_dates=True,
            header=0,
            sep='\t',
        )
        expected_df['time'] = pd.to_datetime(expected_df['time'])
        expected_df.set_index(['time', 'ngram', 'lang'], inplace=True)

        pd.testing.assert_frame_equal(
            df[self.ngrams_cols],
            expected_df[self.ngrams_cols],
        )
        logging.info(df)

    def test_get_lang(self):
        df = self.api.get_lang(
            self.lang_example,
            start_time=self.start,
            end_time=self.end,
        )
        expected_df = pd.read_csv(
            "tests/lang_example.tsv",
            index_col=0,
            parse_dates=True,
            header=0,
            sep='\t',
        )
        expected_df.index.name = 'time'

        pd.testing.assert_frame_equal(
            df[self.lang_cols],
            expected_df[self.lang_cols],
        )
        logging.info(df)

    def test_get_zipf_dist(self):
        df = self.api.get_zipf_dist(
            date=self.end,
            lang=self.lang_example,
            ngrams='1grams',
        )
        logging.info(df)
        assert not df.empty

    def test_get_zipf_dist_filter_1grams(self):
        for _filter in self.ngram_filters:
            df = self.api.get_zipf_dist(
                date=self.end,
                lang=self.lang_example,
                ngrams='1grams',
                ngram_filter=_filter,
                top_n=100
            )
            logging.info(f'Filter set: {_filter}. (1grams)')
            logging.info(df)
            assert not df.empty

    def test_get_zipf_dist_filter_3grams(self):

        df = self.api.get_zipf_dist(
            date=self.end,
            lang=self.lang_example,
            ngrams='3grams',
            ngram_filter='latin',
            top_n=100
        )
        logging.info(f'Filter set: latin. (3grams)')
        logging.info(df)
        assert not df.empty

    def test_get_divergence_1grams(self):
        df = self.api.get_divergence(
            date=self.end,
            lang=self.lang_example,
            ngrams='1grams',
        )
        logging.info(df)
        assert not df.empty

    def test_get_divergence_2grams(self):
        df = self.api.get_divergence(
            date=self.end,
            lang=self.lang_example,
            ngrams='2grams',
        )
        logging.info(df)
        assert not df.empty

    def test_get_divergence_dist_filter_1grams(self):
        for _filter in self.ngram_filters:
            df = self.api.get_divergence(
                date=self.end,
                lang=self.lang_example,
                ngrams='1grams',
                ngram_filter=_filter,
                top_n=100
            )
            logging.info(f'Filter set: {_filter}. (1grams)')
            logging.info(df)
            assert not df.empty


if __name__ == '__main__':
    unittest.main()
