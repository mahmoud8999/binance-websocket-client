import logging

def setup_logger(filepath):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        filename=filepath
    )

    return logging.getLogger("binance-websocket-client")
