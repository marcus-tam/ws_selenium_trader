from yahoo_fin import stock_info
from time import sleep
import schedule
from pprint import PrettyPrinter


def algo1():
    """
        Classical buy low, sell high
        Purpose of this algorithm is to determine price points for BUY_LOW and SELL_HIGH\n
        The price points are determined by finding the two most frequent price poitns the stock is trading at
        This works especially well with penny stocks (at least the penny stocks I look at) because they only have 
        a few price points to work with. 
    """
    stock_prices = set()
    lock_price = int()
    stock_prices_array = list()
    output_time = 5
    counter = 0  #We will use this as a counter to occasionally output the array

    pp = PrettyPrinter(indent=4)

    while True:
        price_point = stock_info.get_live_price('FIRE.TO')
        round(price_point, 4)
        # If the current lock price is not equal to the price point
        # Set the lock price to the price point
        # Add the price point to the set
        # Add the price point to the list
        if lock_price != price_point:
            lock_price = price_point
            stock_prices.add(price_point)
            stock_prices_array.append(price_point)
        if counter % (output_time * 60) == 0:
            # output should be
            # PRICE : PERMUTATIONS_OF_PRICE
            for prices in stock_prices:
                temp = 0
                for values in stock_prices_array:
                    if prices == values:
                        temp += 1
                print(f'{prices} : {temp}')
        counter += 1
        sleep(1)


# algo1()