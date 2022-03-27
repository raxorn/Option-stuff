from yahoo_fin import options as op
import yahoo_fin.stock_info as si
import json
import os.path


def get_call_option_data(ticker, all_dates=False, num_of_exp = 1 ):

    expiration_dates = op.get_expiration_dates(ticker)
    if all_dates:
        num_of_exp = len(expiration_dates)

    call_option_table = {}
    put_option_table = {}

    for date in range(num_of_exp):
        chain = op.get_calls(ticker, expiration_dates[date])
        strikes = chain["Contract Name"]
        OI = chain["Open Interest"]
        for (strike, OI) in zip(strikes, OI):
            strike = get_strike(strike, len(ticker))
            #removes "-" from open interest
            if OI != '-':
                if strike in call_option_table:
                    call_option_table[strike] += int(OI)
                else:
                    call_option_table[strike] = int(OI)

    return call_option_table


def get_strike(strike, len_ticker):
    # fjern prefix på striken
    remove_prefix = len_ticker + 6 + 1

    # fjern suffix på striken
    remove_suffix = 3

    return int(strike[remove_prefix: -remove_suffix])


def get_num_itm_options(option_dict, current_price):
    itm = 0
    for key, value in option_dict.items():
        if int(key) < current_price:
            itm += value
    return itm


def write_to_json(filename, option_table):
    with open(filename, 'w') as fp:
        json.dump(option_table, fp)


def read_from_json(filename):
    with open(filename) as f:
        option_table = json.load(f)

    return option_table


def print_table(option_table):
    for key, value in option_table.items():
        print("Strike: ", key, " Open interest: ", value)


def main():
    ticker = 'AAPL'

    current_price = si.get_live_price(ticker)

    # Get all expirationDates
    all_dates = False

    if all_dates:
        filename = ticker +" all call options.json"
    else:
        filename = ticker +" call options this_week.json"

    if os.path.exists(filename):
        option_table = read_from_json(filename)
    else:
        option_table = get_call_option_data(ticker, all_dates)
        write_to_json(filename, option_table)

    print_table(option_table)
    itm = get_num_itm_options(option_table, current_price)
    print("\nPris på aksje nå: ", current_price)
    print("Antall in the money opsjoner: ", itm)
    print("Antall call opsjoner totalt: ", sum(option_table.values()))



if __name__ == '__main__':
    main()
