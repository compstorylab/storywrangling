import logging
import warnings
warnings.filterwarnings("ignore")

import unittest
from storywrangling import Realtime


class RealtimeTesting(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(RealtimeTesting, self).__init__(*args, **kwargs)

        self.api = Realtime()
        self.lang_example = "en"
        self.ngram_example = "😂"
        self.array_example = ["the pandemic", "next hour", "new cases", "😭 😭", "used to"]
        self.multilang_example = [
            ('covid19', 'en'),
            ('cuarentena', 'es'),
            ('quarentena', 'pt'),
            ('فيروس', 'ar'),
            ('#BTS', 'ko'),
            ('Brexit', 'fr'),
            ('virus', 'id'),
            ('Suriye', 'tr'),
            ('coronavirus', 'hi'),
            ('Flüchtling', 'de'),
            ('Pasqua', 'it'),
            ('карантин', 'ru'),
        ]

        self.ngrams_cols = [
            "count",
            "count_no_rt",
            "rank",
            "rank_no_rt",
            "freq",
            "freq_no_rt",
            "r_rel"
        ]

    def test_get_ngram(self):
        df = self.api.get_ngram(
            self.ngram_example,
            self.lang_example,
        )
        logging.info(df)
        assert not df.empty

    def test_get_ngrams_array(self):
        df = self.api.get_ngrams_array(
            self.array_example,
            lang=self.lang_example,
        )
        logging.info(df)
        assert not df.empty

    def test_get_ngrams_tuples(self):
        df = self.api.get_ngrams_tuples(
            self.multilang_example,
        )
        logging.info(df)
        assert not df.empty

    def test_get_zipf_dist(self):
        df = self.api.get_zipf_dist(
            lang=self.lang_example,
        )
        logging.info(df)
        assert not df.empty


if __name__ == '__main__':
    unittest.main()
