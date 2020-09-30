import unittest
import pandas as pd
from datetime import datetime
from storywrangling import Storywrangler, Query


class APITesting(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(APITesting, self).__init__(*args, **kwargs)

        self.api = Storywrangler()

        self.start = datetime(2010, 1, 1)
        self.end = datetime(2020, 1, 1)

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
            "count_no_rt",
            "rank",
            "rank_no_rt",
            "freq",
            "freq_no_rt",
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

        self.div_cols = [
            "ngram",
            "rd_contribution",
            "rank_change",
            "rd_contribution_noRT",
            "rank_change_noRT",
            "time_1",
            "time_2"
        ]
    """
    def test_connection_languages(self):
        q = Query("languages", "languages")
        df = q.query_languages("en")
        assert not df.empty

    def test_connection_1grams(self):
        q = Query(f"1grams", "en")
        df = q.query_ngram("!")
        assert not df.empty

    def test_connection_2grams(self):
        q = Query(f"2grams", "en")
        df = q.query_ngram("! !")
        assert not df.empty

    def test_connection_3grams(self):
        q = Query(f"3grams", "en")
        df = q.query_ngram("! ! !")
        assert not df.empty

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

    def test_get_ngrams_array(self):
        df = self.api.get_ngrams_array(
            self.array_example,
            lang=self.lang_example,
            database="1grams",
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
    """
    #@unittest.skip("Skip zipf_cutoff")
    def test_get_zipf_1grams_max1000(self):
            df = self.api.get_zipf_dist(
                self.end,
                self.lang_example,
                "1grams",
                max_rank=1000
            )
            #df.to_pickle('tests/zipf_1grams_max1000.pkl')

            expected_df = pd.read_pickle(
                "tests/zipf_1grams_max1000.pkl",
            )
            expected_df.index.name = 'ngram'

            pd.testing.assert_frame_equal(
                df[self.ngrams_cols],
                expected_df[self.ngrams_cols],
            )
            

    @unittest.skip("Skip zipf_all")
    def test_get_zipf_1grams_all(self):
            df = self.api.get_zipf_dist(
                self.end,
                self.lang_example,
                "1grams"
            )

            expected_df = pd.read_pickle(
                "tests/zipf_1grams_all.pkl",
            )
            expected_df.index.name = 'ngram'

            pd.testing.assert_frame_equal(
                df[self.ngrams_cols],
                expected_df[self.ngrams_cols],
            )

    def test_get_divergence_max1000(self):
        df = self.api.get_divergence(
            self.end,
            self.lang_example,
            "1grams",
            max_n=1000)
        #df.to_pickle("tests/divergence_max1000.pkl")
        expected_df = pd.read_pickle(
            "tests/divergence_max1000.pkl")

        pd.testing.assert_frame_equal(
            df[self.div_cols],
            expected_df[self.div_cols],
        )

if __name__ == '__main__':
    unittest.main()
