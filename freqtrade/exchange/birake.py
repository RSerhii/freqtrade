import logging
from typing import Dict

import ccxt

from freqtrade import (DependencyException, InvalidOrderException,
                       OperationalException, TemporaryError)
from freqtrade.exchange import Exchange

logger = logging.getLogger(__name__)


class Birake(Exchange):
    _createdOrders = {}
    def get_valid_pair_combination(self, curr_1, curr_2) -> str:
        """
        Get valid pair combination of curr_1 and curr_2 by trying both combinations.
        """        
        for pair in [f"{curr_1}_{curr_2}", f"{curr_2}_{curr_1}"]:
            if pair in self.markets and self.markets[pair].get('active'):
                return pair
        raise DependencyException(f"Could not combine {curr_1} and {curr_2} to get a valid pair.")

    def get_order(self, order_id: str, pair: str) -> Dict:
        if self._config['dry_run']:
            return super.get_order(order_id, pair)
        order = None
        knownOrder = None
        if order_id in self._createdOrders:            
            knownOrder = self._createdOrders[order_id]            
        else:
            # unknown order
            pass
        try:
            activeOrders = self._api.fetch_open_orders(order_id, pair) 
            for activeOrder in activeOrders:
                if activeOrder['id'] == order_id:
                    activeOrder['remaining'] = activeOrder['amount']
                    activeOrder['amount'] = knownOrder['amount']
                    return activeOrder
            knownOrder['filled'] = True
            knownOrder['status'] = 'closed'
        except ccxt.InvalidOrder as e:
            raise InvalidOrderException(
                f'Tried to get an invalid order (id: {order_id}). Message: {e}') from e
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            raise TemporaryError(
                f'Could not get order due to {e.__class__.__name__}. Message: {e}') from e
        except ccxt.BaseError as e:
            raise OperationalException(e) from e
        if order is None:
            order = self._api.orders[order_id]
            order['remaining'] = 0
            order['filled'] = True
        if order is None:
            raise InvalidOrderException(f'Tried to get an invalid order (id: {order_id}). Probably it could be filled') from e
        return order


    def create_order(self, pair: str, ordertype: str, side: str, amount: float,
                     rate: float, params: Dict = {}) -> Dict:
        order = None
        try:
            # Set the precision for amount and price(rate) as accepted by the exchange
            amount = self.symbol_amount_prec(pair, amount)
            needs_price = (ordertype != 'market'
                           or self._api.options.get("createMarketBuyOrderRequiresPrice", False))
            rate = self.symbol_price_prec(pair, rate) if needs_price else None

            order = self._api.create_order(pair, ordertype, side, amount, rate, params)

        except ccxt.InsufficientFunds as e:
            raise DependencyException(
                f'Insufficient funds to create {ordertype} {side} order on market {pair}.'
                f'Tried to {side} amount {amount} at rate {rate}.'
                f'Message: {e}') from e
        except ccxt.InvalidOrder as e:
            raise DependencyException(
                f'Could not create {ordertype} {side} order on market {pair}.'
                f'Tried to {side} amount {amount} at rate {rate}.'
                f'Message: {e}') from e
        except (ccxt.NetworkError, ccxt.ExchangeError) as e:
            raise TemporaryError(
                f'Could not place {side} order due to {e.__class__.__name__}. Message: {e}') from e
        except ccxt.BaseError as e:
            raise OperationalException(e) from e

        self._createdOrders[order['id']] = order
        return order

