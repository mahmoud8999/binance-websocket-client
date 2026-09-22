from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

URI = "wss://stream.binance.com:9443/ws"
RETRY_DELAY = 1
MAX_RETRY_DELAY = 30
PING_INTERVAL = 10
PING_TIMEOUT = 10
LOGFILE = PROJECT_ROOT / "logs" / "logfile.log"
