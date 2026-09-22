def parse_raw_data(message_data):
    if message_data.get("e") == "kline":
        data = message_data["k"]
        
        trade = {
            "SYMBOL": data["s"],
            "OPEN": data["o"],
            "HIGH": data["h"],
            "LOW": data["l"],
            "CLOSE": data["c"],
            "VOLUME": data["v"]
        }
        
    else:
        trade = {}
        
    return trade
        
