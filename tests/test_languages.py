import unittest
from datetime import datetime
import pandas as pd
from storywrangling import Languages, Query


class LanguagesTesting(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(LanguagesTesting, self).__init__(*args, **kwargs)

        self.api = Languages()

        self.start = datetime(2010, 1, 1)
        self.end = datetime(2020, 1, 1)

        self.lang_example = "en"

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

    def test_connection_languages(self):
        q = Query("languages", "languages")
        df = q.query_languages("en")
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


if __name__ == '__main__':
    unittest.main()
