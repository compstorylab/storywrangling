import warnings
warnings.filterwarnings("ignore")

import unittest
from storywrangling import Realtime


class RealtimeTesting(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(RealtimeTesting, self).__init__(*args, **kwargs)

        self.api = Realtime()
        self.lang_example = "en"
        self.ngram_example = "virus"
        self.array_example = ["pandemic", "#BLM", "lockdown", "deaths", "distancing"]
        self.multilang_example = [
            ('coronavirus', 'en'),
            ('cuarentena', 'es'),
            ('quarentena', 'pt'),
            ('فيروس', 'ar'),
            ('#BTS', 'ko'),
        ]

        self.ngrams_cols = [
            "count",
            "count_no_rt",
            "rank",
            "rank_no_rt",
            "freq",
            "freq_no_rt"
        ]

    def test_get_ngram(self):
        df = self.api.get_ngram(
            self.ngram_example,
            self.lang_example,
        )
        assert not df.empty

    def test_get_ngrams_array(self):
        df = self.api.get_ngrams_array(
            self.array_example,
            lang=self.lang_example,
        )
        assert not df.empty

    def test_get_ngrams_tuples(self):
        df = self.api.get_ngrams_tuples(
            self.multilang_example,
        )
        assert not df.empty

    def test_get_zipf_dist(self):
        df = self.api.get_zipf_dist(
            lang=self.lang_example,
        )
        assert not df.empty


if __name__ == '__main__':
    unittest.main()
