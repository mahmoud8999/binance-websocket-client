from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Checkbox, Footer, DataTable, Label

import src.client
import asyncio


COLUMNS = (
    ("SYMBOL", 14),
    ("OPEN", 14),
    ("HIGH", 14),
    ("LOW", 14),
    ("CLOSE", 14),
    ("VOLUME", 16),
    ("STATUS", 14),
)


SYMBOLS = (
    ("BTC/USDT", "btcusdt"),
    ("ETH/USDT", "ethusdt"),
    ("SOL/USDT", "solusdt"),
    ("XRP/USDT", "xrpusdt"),
    ("BNB/USDT", "bnbusdt"),
    ("DOGE/USDT", "dogeusdt"),
    ("ADA/USDT", "adausdt"),
    ("LINK/USDT", "linkusdt"),
    ("SUI/USDT", "suiusdt"),
    ("NEAR/USDT", "nearusdt"),
)


class BinanceApp(App[None]):

    CSS_PATH = "binance_css.tcss"

    BINDINGS = [
        Binding(
            key="q",
            action="quit",
            description="Quit App",
        )
    ]
    
    def __init__(self):
        super().__init__()
        
        self.client = src.client.BinanceWebSocketClient(
            on_trade=self.handle_trade,
            on_connection_change=self.handle_connection_change,
        )
        
    def handle_trade(self, trade):
        
        table = self.query_one("#market-table", DataTable)
        
        symbol_id = trade["SYMBOL"].lower()
        
        table.update_cell(symbol_id, "OPEN", trade["OPEN"])
        table.update_cell(symbol_id, "HIGH", trade["HIGH"])
        table.update_cell(symbol_id, "LOW", trade["LOW"])
        table.update_cell(symbol_id, "CLOSE", trade["CLOSE"])
        table.update_cell(symbol_id, "VOLUME", trade["VOLUME"])
        table.update_cell(symbol_id, "STATUS", "LIVE")
        
    def handle_connection_change(self, connected):
        connection_status = self.query_one(
            "#connection-status",
            Label,
        )
        
        if connected:
            connection_status.update(
                "Connection: CONNECTED"
            )
        else:
            connection_status.update(
                "Connection: DISCONNECTED"
            )

    def compose(self) -> ComposeResult:

        yield Header()

        # -----------------------------------------------------
        # SYMBOL SELECTOR
        # -----------------------------------------------------

        with Vertical(id="symbol-selector"):

            with Horizontal(classes="symbol-row"):
                for symbol, symbol_id in SYMBOLS[:5]:
                    yield Checkbox(
                        symbol,
                        id=symbol_id,
                    )

            with Horizontal(classes="symbol-row"):
                for symbol, symbol_id in SYMBOLS[5:]:
                    yield Checkbox(
                        symbol,
                        id=symbol_id,
                    )

        # -----------------------------------------------------
        # MARKET TABLE
        # -----------------------------------------------------

        with Vertical(id="table-container"):
            yield DataTable(id="market-table")

        # -----------------------------------------------------
        # CONNECTION STATUS
        # -----------------------------------------------------

        with Horizontal(id="status-bar"):

            yield Label(
                "Connection: DISCONNECTED",
                id="connection-status",
            )

            yield Label(
                "Streams: 0 subscribed",
                id="stream-status",
            )

        yield Footer()

    def on_mount(self) -> None:

        self.title = "BINANCE REAL-TIME MARKET MONITOR"

        table = self.query_one("#market-table", DataTable)

        # Add table columns.
        for column_name, column_width in COLUMNS:
            table.add_column(
                column_name,
                key=column_name,
                width=column_width,
            )

        # Check all checkboxes by default.
        for checkbox in self.query(Checkbox):
            checkbox.value = True

        # Build the initial table from the checked symbols.
        self.update_market_table()
        
        asyncio.create_task(self.client.connect())

    def update_market_table(self) -> None:

        table = self.query_one("#market-table", DataTable)

        # Remove the existing rows.
        table.clear(columns=False)

        # Add only checked symbols.
        for symbol, symbol_id in SYMBOLS:

            checkbox = self.query_one(f"#{symbol_id}", Checkbox)

            if checkbox.value:
                table.add_row(
                    symbol,
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    key=symbol_id,
                )

    async def on_checkbox_changed(self, event: Checkbox.Changed) -> None:

        table = self.query_one("#market-table", DataTable)

        self.update_market_table()
        
        symbol_id = event.checkbox.id
        stream = f"{event.checkbox.id}@kline_1s"
        
        if event.value:
            symbol = next(
                symbol
                for symbol, sid in SYMBOLS
                if sid == symbol_id
            )
            
            if symbol_id not in table.rows:
                table.add_row(
                    symbol,
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    key=symbol_id,
                 )
        
            await self.client.subscribe([stream])
        else:
            if symbol_id in table.rows:
                table.remove_row(symbol_id)
        
            await self.client.unsubscribe([stream])

        stream_status = self.query_one("#stream-status", Label)
        
        stream_status.update(
            f"Streams: {len(self.client.subscriptions)} subscribed"
        )

if __name__ == "__main__":
    BinanceApp().run()
