import time
from datetime import datetime
from storywrangling import Storywrangler


def main():
    timeit = time.time()

    storywrangler = Storywrangler()

    # Getting language usage over time
    lang = storywrangler.get_lang("en")
    print(lang)

    # Getting a single n-gram
    ngram = storywrangler.get_ngram(
        "Black Lives Matter",
        lang="en",
        start_time=datetime(2010, 1, 1),
        end_time=datetime(2020, 1, 1),
    )
    print(ngram)

    # Getting a list of n-grams from one language
    ngrams = ["Higgs", "#AlphaGo", "CRISPR", "#AI", "LIGO"]
    ngrams_df = storywrangler.get_ngrams_array(
        ngrams,
        lang="en",
        database="1grams",
        start_time=datetime(2010, 1, 1),
        end_time=datetime(2020, 1, 1),
    )
    print(ngrams_df)

    # Getting a list of n-grams across several languages
    examples = [
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
    ngrams_array = storywrangler.get_ngrams_tuples(
        examples,
        start_time=datetime(2010, 1, 1),
        end_time=datetime(2020, 1, 1),
    )
    print(ngrams_array)

    # Getting all n-grams for a given day
    ngrams_zipf = storywrangler.get_zipf_dist(
        date=datetime(2010, 1, 1),
        lang="en",
        database="1grams"
    )
    print(ngrams_zipf)

    print(f"Total time elapsed: {time.time() - timeit:.2f} sec.")


if __name__ == "__main__":
    main()
