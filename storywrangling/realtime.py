
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

import logging
import ujson
import pickle
import pandas as pd
from tqdm import tqdm
from typing import Optional
from datetime import datetime

import resources
from storywrangling.query import Query
from storywrangling.regexr import nparser


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Realtime:

    def __init__(self) -> None:
        """Python API to access the realtime database"""

        self.parser = pickle.load(
            pkg_resources.open_binary(resources, 'ngrams.bin')
        )
        self.supported_languages = ujson.load(
            pkg_resources.open_binary(resources, 'supported_languages.json')
        )
        self.indexed_languages = ujson.load(
            pkg_resources.open_binary(resources, 'indexed_languages.json')
        )
        self.divergence_languages = ujson.load(
            pkg_resources.open_binary(resources, 'divergence_languages.json')
        )
