import json
import asyncio
import websockets

from websockets.exceptions import ConnectionClosed
from . import config, parser
from .logger import setup_logger


logger = setup_logger(config.LOGFILE)


class BinanceWebSocketClient:

    def __init__(self, on_trade=None, on_connection_change=None):
        self.websocket = None
        self.subscriptions = set()
        self.on_trade = on_trade
        self.on_connection_change = on_connection_change

    async def subscribe(self, crypto_currencies):

        self.subscriptions.update(crypto_currencies)

        if self.websocket is None:
            return

        subscribe_request = {
            "method": "SUBSCRIBE",
            "params": crypto_currencies,
            "id": 1,
        }

        try:
            await self.websocket.send(
                json.dumps(subscribe_request)
            )
        except ConnectionClosed:
            logger.warning(
                "Cannot subscribe: WebSocket connection is closed."
            )

    async def unsubscribe(self, crypto_currencies):

        self.subscriptions.difference_update(crypto_currencies)

        if self.websocket is None:
            return

        unsubscribe_request = {
            "method": "UNSUBSCRIBE",
            "params": crypto_currencies,
            "id": 2,
        }

        try:
            await self.websocket.send(
                json.dumps(unsubscribe_request)
            )
        except ConnectionClosed:
            logger.warning(
                "Cannot unsubscribe: WebSocket connection is closed."
            )

    async def connect(self):

        retry_delay = config.RETRY_DELAY

        while True:
            try:
                async with websockets.connect(
                    config.URI,
                    ping_interval=config.PING_INTERVAL,
                    ping_timeout=config.PING_TIMEOUT,
                ) as websocket:

                    self.websocket = websocket
                    
                    if self.on_connection_change:
                        self.on_connection_change(True)

                    logger.info(
                        "Connected to Binance WebSocket."
                    )

                    retry_delay = config.RETRY_DELAY

                    # Re-subscribe after a reconnect.
                    if self.subscriptions:
                        await self.subscribe(
                            list(self.subscriptions)
                        )

                    async for message in websocket:

                        message_data = json.loads(message)

                        normalized_trade = parser.parse_raw_data(
                            message_data
                        )
                        
                        if normalized_trade and self.on_trade:
                            self.on_trade(normalized_trade)

            except ConnectionClosed as error:

                logger.warning(
                    "Binance WebSocket connection closed: %s",
                    error,
                )

            except Exception as error:

                logger.warning(
                    "Binance WebSocket error: %s",
                    error,
                )

            finally:
                self.websocket = None
                
                if self.on_connection_change:
                    self.on_connection_change(False)

            logger.info(
                "Retrying in %s seconds",
                retry_delay,
            )

            await asyncio.sleep(retry_delay)

            retry_delay = min(
                retry_delay * 2,
                config.MAX_RETRY_DELAY,
            )
