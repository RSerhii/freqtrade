""" Southxchange exchange subclass """
import logging
from typing import Dict, List
from freqtrade import OperationalException

from freqtrade.exchange import Exchange

logger = logging.getLogger(__name__)


class Southxchange(Exchange):

    def validate_pairs(self, pairs: List[str]) -> None:
        """
        Checks if all given pairs are tradable on the current exchange.
        Raises OperationalException if one pair is not available.
        :param pairs: list of pairs
        :return: None
        """

        if not self.markets:
            logger.warning("Unable to validate pairs (assuming they are correct).")
            return

        for pair in pairs:
            # Note: ccxt has BaseCurrency/QuoteCurrency format for pairs
            # TODO: add a support for having coins in BTC/USDT format
            if self.markets and pair not in self.markets:
                raise OperationalException(
                    f"Pair {pair} is not available on {self.name}. "
                    f"Please remove {pair} from your whitelist.")
