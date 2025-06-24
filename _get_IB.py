from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import time
# Let's focus on getting the data from each vendor in the same format then it can all be one code
class IBApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        
    def historicalData(self, reqId, bar):
        print(f"ReqId: {reqId} Date: {bar.date} Open: {bar.open} High: {bar.high} Low: {bar.low} Close: {bar.close} Volume: {bar.volume}")
        
    def historicalDataEnd(self, reqId, start, end):
        print(f"Historical data request {reqId} ended from {start} to {end}")
        self.disconnect()

def main(host, port, clientId):
    app = IBApp()
    if not app.connect(host, port, clientId):
        return RuntimeError
    print("hellpo")
    time.sleep(1)  # Allow connection to establish
    # Define AAPL contract
    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"

    # Request historical data:
    # Parameters: reqId, contract, endDateTime, durationStr, barSizeSetting, whatToShow, useRTH, formatDate, chartOptions
    app.reqHistoricalData(1, contract, "", "5 Y", "1 week", "TRADES", 1, 1, True, [])
    
    app.run()
    # return something and check for typeerror
    

if __name__ == "__main__":
    main("127.0.0.1", 4002, clientId=0)


#https://www.interactivebrokers.com/campus/ibkr-api-page/twsapi-ref/#contractdetails-ref