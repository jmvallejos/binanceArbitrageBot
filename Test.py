from BinanceSpot.AccountStream import AccountStream
from BinanceSpot.Environment import Environment
from BinanceSpot.MarketOperator import MarketOperator
from BinanceSpot.Test.TickerStreamFixApiTest import TickerStreamFixApiTest
from BinanceSpot.Test.TickerStreamIndividualTickTest import TickerStreamIndividualTickTest
from BinanceSpot.Test.TickerStreamSbeTest import TickerStreamSbeTest
from BinanceSpot.Test.TriangularArbitrageTest import TriangularArbitrageTest

if __name__ == "__main__":    
    test = TriangularArbitrageTest()
    test.Test()
    
