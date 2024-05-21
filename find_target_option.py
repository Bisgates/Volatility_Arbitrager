from ib_insync import *
import datetime


def get_valid_date(chain):
    expirations = sorted(expiry for expiry in chain.expirations)

    target_date = None
    min_diff = float('inf')
    for expiry in expirations:
        expiry_date = datetime.datetime.strptime(expiry, '%Y%m%d').date()
        diff = (expiry_date - datetime.date.today()).days
        if abs(diff - 90) < min_diff:
            min_diff = abs(diff - 90)
            target_date = expiry

    if not target_date:
        print("No options found within the next 90 days.")
    else:
        print(f'Target Expiration Date: {target_date}')
    return target_date


def find_target_option(chain, delta_thred=-0.15, debug=False):
    target_date = get_valid_date(chain)
    target_option = None
    # filter option
    strikes = [int(t) for t in chain.strikes if t < spy_price and t > spy_price * 0.93]   

    for strike in strikes:
        option = Option('SPY', target_date, strike, 'P', 'SMART')
        ib.qualifyContracts(option)

        ticker = ib.reqTickers(option)[0]

        if debug:
            print(strike, ticker.modelGreeks.delta, ticker.bid, ticker.ask)

        if ticker.modelGreeks.delta < delta_thred:
            return target_option
        else:
            target_option = option

if __name__ == '__main__':

    util.startLoop()

    ib = IB()
    ib.connect('127.0.0.1', 4002, clientId=14)
    symbol = 'SPY'
    spy = Stock(symbol, 'SMART', 'USD')

    ib.qualifyContracts(spy)
    ib.reqMarketDataType(4)

    [ticker] = ib.reqTickers(spy)

    spy_price = ticker.marketPrice()
    print(f'Current SPY price: {spy_price}')

    chains = ib.reqSecDefOptParams(spy.symbol, '', spy.secType, spy.conId)
    chain = next(c for c in chains if c.tradingClass == symbol and c.exchange == 'SMART')
    option = find_target_option(chain, debug=True)

    print(option)
