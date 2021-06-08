##################
Storywrangler API
##################

.. contents::


Description
###########

The `Storywrangler <https://gitlab.com/compstorylab/storywrangler>`__ project is
a natural language processing instrument
designed to carry out an ongoing,
day-scale curation of over 100 billion tweets
containing roughly 1 trillion 1-grams
from 2008 to 2021.
For each day,
we break tweets into unigrams, bigrams, and trigrams
spanning over 100 languages.
We track ngram usage frequencies,
and generate Zipf distributions,
for words, hashtags, handles, numerals, symbols, and emojis.
We make the data set available through an interactive
`time series viewer <https://storywrangling.org/>`__,
and as downloadable time series and daily distributions.
Although Storywrangler leverages Twitter data,
our method of extracting and tracking dynamic changes of ngrams
can be extended to any similar social media platform.
We showcase a few examples of the many possible avenues of study
we aim to enable including
how social amplification can be visualized through
`contagiograms <https://gitlab.com/compstorylab/contagiograms>`__.
The project is intended to enable or enhance the study of any large-scale
temporal phenomena where people matter including culture, politics,
economics, linguistics, public health, conflict, climate change, and
data journalism.


Usage
#####

All ngram timeseries are stored and served on `Hydra`, a server
at the `Vermont Complex Systems Center <https://vermontcomplexsystems.org/>`__.
Further details about our backend infrastructure
and our Twitter stream processing framework
can be found on our Gitlab
`repository <https://gitlab.com/compstorylab/storywrangler>`__.


If you can connect to the UVM VPN at
`sslvpn2.uvm.edu` using your UVM credentials,
then you can access our database using this Python module.
Unfortunately you can not use this package if you are not connected to the UVM network for the time being.
We do hope to have a workaround eventually,
but in the meantime if you would like to use our ngrams  dataset in your research,
we provide an easy way to download daily ngrams timeseries as JSON
files via our
`web service <https://github.com/janeadams/storywrangler>`__.

    If there is a large subset of ngrams you would like from
    our database, please send us an email.



Installation
############

You can install the latest version by cloning the repo and running
`setup.py <setup.py>`__ script in your terminal

Setuptools
**********

.. code:: shell

    git clone https://gitlab.com/compstorylab/storywrangling.git
    cd storywrangling
    python setup.py install

Install Development Version
***************************

.. code:: shell

    git clone https://gitlab.com/compstorylab/storywrangling.git
    cd storywrangling
    python setup.py develop


Historical Database
##########################


Getting started
***************

Import our library and create an instance of the master
`Storywrangler() <storywrangling/api.py>`__ class object.

.. code:: python

    from datetime import datetime
    from storywrangling import Storywrangler

    storywrangler = Storywrangler()

The ``Storywrangler()`` class provides a set of methods
to access our database.
We outline some of the main methods below.


A single ngram timeseries
***************************

You can get a dataframe of usage rate for a single ngram timeseries
by using the ``get_ngram()`` method.

================  ========  ======================  =============================
Argument                                            Description
--------------------------------------------------  -----------------------------
Name              Type      Default
================  ========  ======================  =============================
``ngram``         str       required                target 1-, 2-, or 3-gram
``lang``          str       "en"                    target language (iso code)
``start_time``    datetime  datetime(2010, 1, 1)    starting date for the query
``end_time``      datetime  last\_updated           ending date for the query
================  ========  ======================  =============================

    See `ngrams\_languages.json <resources/ngrams_languages.json>`__
    for a list of all supported languages.

**Example code**

.. code:: python

    ngram = storywrangler.get_ngram(
      "Black Lives Matter",
      lang="en",
      start_time=datetime(2010, 1, 1),
      end_time=datetime(2020, 1, 1),
    )

**Expected output**

A single Pandas dataframe (see `ngram_example.tsv <tests/ngram_example.tsv>`__).

================  =============================================
Argument          Description
================  =============================================
``time``          Pandas `DatetimeIndex`
``count``         usage rate in all tweets (AT)
``count_no_rt``   usage rate in original tweets (OT)
``freq``          normalized frequency in all tweets (AT)
``freq_no_rt``    normalized frequency in original tweets (OT)
``rank``          usage tied-rank in all tweets (AT)
``rank_no_rt``    usage tied-rank in original tweets (OT)
================  =============================================




A list of ngrams from one language
************************************

If you have a list of ngrams,
then you can use the ``get_ngrams_array()`` method
to retrieve a dataframe of usage rates in a single language.


================  ========  ======================  ===============================
Argument                                            Description
--------------------------------------------------  -------------------------------
Name              Type      Default
================  ========  ======================  ===============================
``ngrams_list``   list      required                a list of 1-, 2-, or 3-grams
``lang``          str       "en"                    target language (iso code)
``start_time``    datetime  datetime(2010, 1, 1)    starting date for the query
``end_time``      datetime  last\_updated           ending date for the query
================  ========  ======================  ===============================


**Example code**

.. code:: python

    ngrams = ["Higgs", "#AlphaGo", "CRISPR", "#AI", "LIGO"]
    ngrams_df = storywrangler.get_ngrams_array(
      ngrams,
      lang="en",
      start_time=datetime(2010, 1, 1),
      end_time=datetime(2020, 1, 1),
    )

All ngrams should be in one language and one database collection.


**Expected output**

A single Pandas dataframe (see `ngrams_array_example.tsv <tests/ngrams_array_example.tsv>`__).

================  =============================================
Argument          Description
================  =============================================
``time``          Pandas `DatetimeIndex`
``ngram``          requested ngram
``count``         usage rate in all tweets (AT)
``count_no_rt``   usage rate in original tweets (OT)
``freq``          normalized frequency in all tweets (AT)
``freq_no_rt``    normalized frequency in original tweets (OT)
``rank``          usage tied-rank in all tweets (AT)
``rank_no_rt``    usage tied-rank in original tweets (OT)
================  =============================================




A list of ngrams across several languages
******************************************

To request a list of ngrams across several languages,
you can use the ``get_ngrams_tuples()`` method.

===============  ============  ======================  ================================
Argument                                               Description
-----------------------------------------------------  --------------------------------
Name             Type          Default
===============  ============  ======================  ================================
``ngrams_list``  list(tuples)  required                a list of ("ngram", "iso-code")
``start_time``   datetime      datetime(2010, 1, 1)    starting date for the query
``end_time``     datetime      last\_updated           ending date for the query
===============  ============  ======================  ================================



**Example code**

.. code:: python

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

**Expected output**

A single Pandas dataframe (see `ngrams_multilang_example.tsv <tests/ngrams_multilang_example.tsv>`__).

================  =============================================
Argument          Description
================  =============================================
``time``          Pandas `DatetimeIndex`
``ngram``         requested ngram
``lang``          requested language
``count``         usage rate in all tweets (AT)
``count_no_rt``   usage rate in original tweets (OT)
``freq``          normalized frequency in all tweets (AT)
``freq_no_rt``    normalized frequency in original tweets (OT)
``rank``          usage tied-rank in all tweets (AT)
``rank_no_rt``    usage tied-rank in original tweets (OT)
================  =============================================



Zipf distribution for a given day
**********************************

To get the Zipf distribution of all
ngrams in our database for a given language on a single day,
please use the ``get_zipf_dist()`` method:

==================      ========  ======================  =====================================
Argument                                                  Description
--------------------------------------------------------  -------------------------------------
Name                    Type      Default
==================      ========  ======================  =====================================
``date``                datetime  required                target date
``lang``                str       "en"                    target language (iso code)
``ngrams``              str       "1grams"                target database collection
``max_rank``            int       None                    max rank cutoff (optional)
``min_count``           int       None                    min count cutoff (optional)
``top_n``               int       None                    limit results to top N ngrams. applied after query (optional)
``rt``                  bool      True                    include or exclude RTs (optional)
``ngram_filter``        str        None                   perform regex to filter results (optional, see below)
==================      ========  ======================  =====================================


**Example code**

.. code:: python

    ngrams_zipf = storywrangler.get_zipf_dist(
      date=datetime(2010, 1, 1),
      lang="en",
      ngrams="1grams",
      max_rank=1000,
      rt=False
    )


**Expected output**

A single Pandas dataframe (see `ngrams_zipf_example.tsv <tests/ngrams_zipf_example.tsv.gz>`__).

================  =============================================
Argument          Description
================  =============================================
``ngram``         requested ngram
``count``         usage rate in all tweets (AT)
``count_no_rt``   usage rate in original tweets (OT)
``freq``          normalized frequency in all tweets (AT)
``freq_no_rt``    normalized frequency in original tweets (OT)
``rank``          usage tied-rank in all tweets (AT)
``rank_no_rt``    usage tied-rank in original tweets (OT)
================  =============================================


Language filters
**************************

Language filters ensure that results for daily Zipf distribution and rank divergence include only specified
n-gram types. All filters are applied using Mongo regex operations.

Filters are supported on ``get_zipf_dist()`` and ``get_divergence()`` methods.

There are two types of regex queries: inclusionary and exclusionary. Inclusionary matches against a standard Mongo
regex query ``{"$regex":<regex pattern>}`` whereas exclusionary excludes the regex matches using ``{"$not":{{"$regex":<regex pattern>}}}``.

For the inclusionary queries where n-grams have an order of n>1, the regex is dynamically resized so that every 1-gram in the result must match the query.
For example ``handles``-filtered 3gram queries will filter through this regex: ``^(@\S+) (@\S+) (@\S+)$``.

The handle and hashtag filters are not strictly valid Twitter handle or hashtags, but rather handle- and hashtag-like.

Ranks and frequencies are not adjusted to account for the filtered Zipf distributions. I.e., rank and frequency columns
are calculated off of the original data. Setting ``max_rank`` will yield somewhat arbitrary results; use ``top_n`` to
select ngrams in the top N of the filtered results.




========================            ========================================================================================================
Filter Name                         Description (``<1-gram example>``)
========================            ========================================================================================================
``handles``                         include only handle-like strings (``^(@\S+)``)
``hashtags``                        include only hashtag-like strings (``^(#\S+)``)
``handles_hashtags``                include only handle- and hashtag-like strings (``^([@|#]\S+)``)
``no_handles_hashtags``             include only strings that do not match handle- and hashtag-like strings (``^(?<![@#])(\b[\S]+)``)
``latin``                           include only latin characters w/ hyphens and apostrophes  (``^([A-Za-z0-9]+[\‘\’\'\-]?[A-Za-z0-9]+)$``)
``no_punc``                         exclude punctuation (``([!…”“\"#@$%&'\(\)\*\+\,\-\.\/\:\;<\=>?@\[\]\^_{|}~]+)``)
========================            ========================================================================================================

**Example code**

.. code:: python

    ngrams_zipf = storywrangler.get_zipf_dist(
      date=datetime(2010, 1, 1),
      lang="en",
      ngrams="1grams",
      max_rank=1000, # pull from 1grams ranked in top 1000 of unfiltered data
      ngram_filter='latin',
      top_n=10, # limit results to top 10 1grams in filtered data
      rt=False
    )



Language usage over time
**************************

To get a timeseries of usage rate for a given language,
you can use the ``get_lang()`` method.

==============  ============  ======================  ================================
Argument                                              Description
----------------------------------------------------  --------------------------------
Name            Type          Default
==============  ============  ======================  ================================
``lang``        str           "\_all"                 target language (iso code)
``start_time``  datetime      datetime(2010, 1, 1)    starting date for the query
``end_time``    datetime      last\_updated           ending date for the query
==============  ============  ======================  ================================

    See `supported\_languages.json <resources/supported_languages.json>`__
    for a list of all supported languages.


**Example code**

.. code:: python

    lang = storywrangler.get_lang(
        "en",
        start_time=datetime(2010, 1, 1),
    )


**Expected output**

A single Pandas dataframe (see `lang_example.tsv <tests/lang_example.tsv>`__).


========================  ===================================================
Argument                  Description
========================  ===================================================
``time``                  Pandas `DatetimeIndex`
``count``                 usage rate of all tweets (AT)
``count_no_rt``           usage rate of original tweets (OT)
``freq``                  normalized frequency of all tweets (AT)
``freq_no_rt``            normalized frequency of original tweets (OT)
``rank``                  usage tied-rank of all tweets (AT)
``rank_no_rt``            usage tied-rank of original tweets (OT)
``num_1grams``            volume of 1-grams in all tweets (AT)
``num_1grams_no_rt``      volume of 1-grams in original tweets (OT)
``num_2grams``            volume of 2-grams in all tweets (AT)
``num_2grams_no_rt``      volume of 3-grams in original tweets (OT)
``num_3grams``            volume of 3-grams in all tweets (AT)
``num_3grams_no_rt``      volume of 3-grams in original tweets (OT)
``unique_1grams``         number of unique 1-grams in all tweets (AT)
``unique_1grams_no_rt``   number of unique 1-grams in original tweets (OT)
``unique_2grams``         number of unique 2-grams in all tweets (AT)
``unique_2grams_no_rt``   number of unique 2-grams in original tweets (OT)
``unique_3grams``         number of unique 3-grams in all tweets (AT)
``unique_3grams_no_rt``   number of unique 3-grams in original tweets (OT)
========================  ===================================================



Narratively trending ngrams
**********************************

To get a list of narratively dominant English ngrams of a given day compared to the year before
please use the ``get_divergence()`` method.
Each ngram is ranked daily by 1-year rank-divergence with :math:`\alpha=1/4`
using our `Allotaxonometry and rank-turbulence divergence <https://arxiv.org/abs/2002.09770>`_ instrument.



==============  ========  ======================  =====================================
Argument                                          Description
------------------------------------------------  -------------------------------------
Name            Type      Default
==============  ========  ======================  =====================================
``date``        datetime  required                target date
``lang``        str       "en"                    target language (iso code)
``ngrams``      str       "1grams"                target database collection
``max_rank``    int       None                    max rank cutoff (optional)
``rt``          bool      True                    include or exclude RTs (optional)
==============  ========  ======================  =====================================


**Example code**

.. code:: python

    ngrams = storywrangler.get_divergence(
        date=datetime(2010, 1, 1),
        lang="en",
        ngrams="1grams",
        max_rank=1000,
        rt=True
    )


**Expected output**

A single Pandas dataframe (see `ngrams_divergence_example.tsv <tests/ngrams_divergence_example.tsv.gz>`__).

==============================  ================================================================
Argument                        Description
==============================  ================================================================
``ngram``                       requested ngram
``rd_contribution``             RTD in all tweets (AT)
``rd_contribution_no_rt``       RTD in original tweets (OT)
``normed_rd``                   normalized RTD in all tweets (AT)
``normed_rd_no_rt``             normalized RTD in original tweets (OT)
``time_1``                      reference date
``rank_1``                      usage rank at reference date in all tweets (AT)
``rank_1_no_rt``                usage rank at reference date in original tweets (OT)
``time_2``                      current date
``rank_2``                      usage rank at current date in all tweets (AT)
``rank_2_no_rt``                usage rank at current date in original tweets (OT)
``rank_change``                 new rank relative to trending ngrams in all tweets (AT)
``rank_change_no_rt``           new rank relative to trending ngrams in original tweets (OT)
==============================  ================================================================



Realtime Database
##################


In addition to our historical daily ngrams database,
we provide a 15-min resolution data stream

- `Time window`: Last 30 days
- `Time resolution`: 15-minute stream of unigrams and bigrams
- `Languages`: Top 12 languages on Twitter


+------------+-------+------------+-------+------------+-------+
| Language   |  ISO  | Language   |  ISO  | Language   |  ISO  |
+============+=======+============+=======+============+=======+
| English    | `en`  | Spanish    |  `es` | Portuguese | `pt`  |
+------------+-------+------------+-------+------------+-------+
| Arabic     | `ar`  | Korean     |  `ko` | French     | `fr`  |
+------------+-------+------------+-------+------------+-------+
| Indonesian | `id`  | Turkish    |  `tr` | Hindi      | `hi`  |
+------------+-------+------------+-------+------------+-------+
| German     | `de`  | Italian    |  `it` | Russian    | `ru`  |
+------------+-------+------------+-------+------------+-------+



Getting started
***************

To use our realtime stream, create an instance of the
`Realtime() <storywrangling/realtime.py>`__ class object.

.. code:: python

    from datetime import datetime
    from storywrangling import Realtime

    storywrangler = Realtime()

The ``Realtime()`` class provides a set of methods similar to the ones found in the Storywrangler class.


A single n-gram timeseries
***************************

You can get a dataframe of usage rate for a single n-gram timeseries
by using the ``get_ngram()`` method.

**Example code**

.. code:: python

    ngram = api.get_ngram("virus", lang="en")


A list of n-grams from one language
************************************

If you have a list of n-grams,
then you can use the ``get_ngrams_array()`` method
to retrieve a dataframe of usage rates in a single language.

**Example code**

.. code:: python

    ngrams = ["the pandemic", "next hour", "new cases", "😭 😭", "used to"]
    ngrams_df = api.get_ngrams_array(ngrams_list=ngrams, lang="en")



A list of n-grams across several languages
******************************************

To request a list of n-grams across several languages,
you can use the ``get_ngrams_tuples()`` method.

**Example code**

.. code:: python

    examples = [
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
    ngrams_array = api.get_ngrams_tuples(examples)


Zipf distribution for a given 15-minute batch
**********************************************

To get the Zipf distribution for a given 15-minute batch,
please use the ``get_zipf_dist()`` method:


**Example code**

.. code:: python

    ngrams_zipf = api.get_zipf_dist(
      dtime=None,  # datetime(Y, m, d, H, M)
      lang="en",
      ngrams='1grams',
      max_rank=None,
      min_count=None,
      rt=True
    )


Citation
########

See the following paper for more details,
and please cite it if you use
our dataset:

    Alshaabi, T., Adams, J. L., Arnold, M. V., Minot, J. R., Dewhurst,
    D. R., Reagan, A. J., Danforth, C. M., & Dodds, P. S.
    `Storywrangler: A massive exploratorium for sociolinguistic, cultural,
    socioeconomic, and political timelines using Twitter
    <https://arxiv.org/abs/2007.12988>`__.
    *arXiv preprint* (2021).


For more information regarding
our tweet's language identification and detection framework,
please see the following paper:

    Alshaabi, T., Dewhurst, D. R., Minot, J. R., Arnold, M. V.,
    Adams, J. L., Danforth, C. M., & Dodds, P. S.
    `The growing amplification of social media:
    Measuring temporal and social contagion dynamics
    for over 150 languages on Twitter for 2009--2020
    <https://epjdatascience.springeropen.com/articles/10.1140/epjds/s13688-021-00271-0>`__.
    *EPJ Data Science* (2021).

