import logging
from typing import Dict

import ccxt

from freqtrade import (DependencyException, InvalidOrderException,
                       OperationalException, TemporaryError)
from freqtrade.exchange import Exchange

logger = logging.getLogger(__name__)


class Birake(Exchange):
    def get_valid_pair_combination(self, curr_1, curr_2) -> str:
        """
        Get valid pair combination of curr_1 and curr_2 by trying both combinations.
        """        
        for pair in [f"{curr_1}_{curr_2}", f"{curr_2}_{curr_1}"]:
            if pair in self.markets and self.markets[pair].get('active'):
                return pair
        raise DependencyException(f"Could not combine {curr_1} and {curr_2} to get a valid pair.")

    

