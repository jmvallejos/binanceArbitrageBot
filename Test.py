from BinanceSpot.AccountStream import AccountStream
from BinanceSpot.Environment import Environment
from BinanceSpot.TickerStream import TickerStream

if __name__ == "__main__":    
    environment = Environment()
    environment.SetProdValues()

    wallet = AccountStream(environment)
    wallet.run()
    
    while True:
        a = 1