![api](resources/logo.png)

# StoryWrangler API 




## Installation

You can install the latest verion by cloning the repo and running [setup.py](setup.py) script in your terminal

```shell 
git clone https://gitlab.com/compstorylab/storywrangling.git
cd storywrangling
python setup.py install 
```


### Install Development Version

```shell
git clone https://gitlab.com/compstorylab/storywrangling.git
cd storywrangling
pip install -e .
```

### Anaconda

This will create a new conda environment (``storywrangling``) with all required dependencies. 

```shell
conda env create -q -f requirements.yml
```

## Usage

```
from datetime import datetime
from storywrangling import Storywrangler	

storywrangler = Storywrangler()
```

Getting a single n-gram

```
ngram = storywrangler.get_ngram(
  "Black Lives Matter",
  lang="en",
  start_time=datetime(2010, 1, 1),
  end_time=datetime(2020, 1, 1),
)
```

Getting a list of n-grams from one language

````
ngrams = ["Higgs", "#AlphaGo", "CRISPR", "#AI", "LIGO"]
ngrams_df = storywrangler.get_ngrams_array(
  ngrams,
  lang="en",
  database="1grams",
  start_time=datetime(2010, 1, 1),
  end_time=datetime(2020, 1, 1),
)
````

Getting a list of n-grams across several languages

```
examples = [
  ('😊', '_all'),
  ('2018', '_all'),
  ('Christmas', 'en'),
  ('Pasqua', 'it'),
  ('eleição', 'pt'),
  ('sommar', 'sv'),
  ('Olympics', 'en'),
  ('World Cup', 'en'),
  ('#AlphaGo', 'en'),
  ('gravitational waves', 'en'),
  ('black hole', 'en'),
  ('Papa Francesco', 'it'),
  ('coronavirus', 'en'),
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
```

Getting language usage over time

```
lang = storywrangler.get_lang("en")
```

Getting all n-grams for a given day

```python
ngrams_zipf = storywrangler.get_zipf_dist(
  date=datetime(2010, 1, 1),
  lang="en",
  database="1grams"
)
```

## Citation
See the following paper for more details, and please cite it if you use our dataset:

> Alshaabi, T., Adams, J.L., Arnold, M.V., Minot, J.R., Dewhurst, D.R., Reagan, A.J., Danforth, C.M. and Dodds, P.S., 2020. [Storywrangler: A massive exploratorium for sociolinguistic, cultural, socioeconomic, and political timelines using Twitter](https://arxiv.org/abs/2007.12988). *arXiv preprint arXiv:2007.12988*.

