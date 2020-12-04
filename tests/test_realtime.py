import unittest
from storywrangling import Realtime, RealtimeQuery


class NgramsTesting(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(NgramsTesting, self).__init__(*args, **kwargs)

        self.api = Realtime()

        self.lang_example = "en"
        self.ngram_example = "the"
        self.lang_isindexed_example = "en"

        self.ngrams_cols = [
            "count",
            "count_no_rt",
            "rank",
            "rank_no_rt",
            "freq",
            "freq_no_rt"
        ]

    def test_connection(self):
        q = RealtimeQuery(f"realtime_1grams", "en")
        df = q.query_ngram("!")
        assert not df.empty

    def test_get_ngram(self):
        df = self.api.get_ngram(
            self.ngram_example,
            self.lang_example,
        )
        print(df)


if __name__ == '__main__':
    unittest.main()
