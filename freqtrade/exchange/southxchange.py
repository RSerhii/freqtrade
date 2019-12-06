""" Southxchange exchange subclass """
import logging
from typing import Dict, List
from freqtrade import OperationalException

from freqtrade.exchange import Exchange

logger = logging.getLogger(__name__)


class Southxchange(Exchange):

    def __init__(self, config: dict, validate: bool = True) -> None:
        super().__init__(config, validate)
        for i in self.markets:
            self.markets[i]["active"] = True
            self.markets[i]["precision"]["base"] = 8
            self.markets[i]["precision"]["quote"] = 8
            self.markets[i]["precision"]["amount"] = 8
            self.markets[i]["precision"]["price"] = 8
        self._api.calculate_fee = self.calculate_fee

    timeframes: list = ["1m", "5m", "30m", "1h", "6h", "12h", "1d", "1w"]
    _ccxt_config: Dict = {"timeframes": dict({"1m":"1m", "5m":"5m", "30m":"30m", "1h":"1h", "6h":"6h", "12h":"12h", "1d":"1d", "1w":"1w"})}

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

    def calculate_fee(self, symbol, type, side, amount, price, takerOrMaker="taker", params={}):
        market = self.markets[symbol]
        key = "quote"
        rate = market[takerOrMaker]
        cost = amount * rate
        if side == "sell":
            cost *= price
        else:
            key = "base"
            precision = market["precision"]["amount"]
        cost = float(self._api.cost_to_precision(symbol, amount * price))
        return {
            "type": takerOrMaker,
            "currency": market[key],
            "rate": rate,
            "cost": float(self._api.fee_to_precision(symbol, rate * cost)),
        }
