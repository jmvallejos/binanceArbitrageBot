from BinanceSpot.AccountStream import AccountStream
from BinanceSpot.Environment import Environment
from BinanceSpot.MarketOperator import MarketOperator
from BinanceSpot.Test.TickerStreamIndividualTickTest import TickerStreamIndividualTickTest
from BinanceSpot.Test.TickerStreamSbeTest import TickerStreamSbeTest
from BinanceSpot.TickerStream.TickerStreamIndividualTick import TickerStreamIndividualTick
from BinanceSpot.TickerStream.TickerStreamSbe import TickerStreamSbe
from BinanceSpot.TriangularArbitrage import TriangularArbitrage

if __name__ == "__main__":    
    environment = Environment()
    environment.SetProdValues()

    testTickerStream = TickerStreamSbeTest()
    testTickerStream.TestAllSymbols()
    
