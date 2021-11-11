import requests
import os
from dotenv import load_dotenv
import pygsheets
import pandas as pd
import datetime
import time

load_dotenv

def dict_init(buyToken, sellToken):
    """Instantiates output dictionary"""
    now = datetime.datetime.now()
    output_dict = {
    'Pair': f'{buyToken}/{sellToken}',
    'Time': f'{now}',
}
    return output_dict

def price_request(network, buyToken, sellToken, sellAmount, decimals="00000000000000000"):
    """Returns JSON response for 0x price aggregator lookup. Match decimals to sellToken value in its token contract - default value is 18"""
    if network.lower() != "ethereum":
        
        if network.lower() == 'fantom': # only on the fantom chain is tether (USDT) called fUSDT. It has 6 decimals. (decimals="00000")
            if buyToken == 'USDT':
                buyToken = 'fUSDT'
            elif sellToken == 'USDT':
                sellToken = 'fUSDT'
        if network.lower() == 'bsc': # only on bsc is tether (USDT) called Binance Peg USD-T (BUSDT). It has 18 decimals (decimals="00000000000000000")
            if buyToken == 'USDT':
                buyToken = 'BUSDT'
            elif sellToken == 'USDC':
                decimals="00000000000000000"
            elif sellToken == 'USDT':
                sellToken = 'BUSDT'
                decimals="00000000000000000"
        
        
        url = f"https://{network}.api.0x.org/swap/v1/quote?buyToken={buyToken}&sellToken={sellToken}&sellAmount={sellAmount}{decimals}"

    else:
        url = f"https://api.0x.org/swap/v1/quote?buyToken={buyToken}&sellToken={sellToken}&sellAmount={sellAmount}{decimals}"
    response = requests.request("GET", url).json()
    return response

def price_eval(response, dictionary, network):
    """Takes raw JSON 0x response to add dicitonary entries for best price opportunities"""
    source = False
    try:
        price = response['price']
        dictionary[f'{network}']=float(price)
    except KeyError:
        price = None
        dictionary[f'{network}']=price
        # print(f'{network} network price unavailable for pair.')
    try:
        sources = response['sources']
    except KeyError:
        sources = False
    if sources:
        for item in sources:
            if item['proportion'] == "1":
                source = item['name']       
    elif not sources:
        source = False
    dictionary[f'{network} network AMM'] = source
    # print(f'{network} network best price: ${price} from: {source}')  
    return dictionary

def arbitrage(dictionary):
    """Returns arbitrage opportunity for pair values calculated within the price_lookup funciton."""
    price_list = []
    networks = ['ethereum', 'bsc', 'polygon', 'fantom']
    percent_opportunity = {'percent_opportunity': 0}
    
    price_list.append(dictionary.get('ethereum', None)) 
    price_list.append(dictionary.get('bsc', None))
    price_list.append(dictionary.get('polygon', None))
    price_list.append(dictionary.get('fantom', None))
    
    for i in range(len(networks)):
        if not price_list[i-1]:
            price_list.pop(i-1)
            networks.pop(i-1)

    tuples = list(zip(networks, price_list))

    tuples.sort(key=lambda x:x[1])

    # print(f"\nhighest price: {tuples[-1]}. Lowest price: {tuples[0]}")

    price_list = sorted(price_list)
    highest_price = price_list[-1]
    lowest_price = price_list[0]

    if highest_price == lowest_price:
        return #print(f"No arb opportunity exists - Highest quoted price of {highest_price} is the same as the lowest quoted price of {lowest_price}")
    
    percentage_change = float((abs(highest_price-lowest_price)) / ((highest_price+lowest_price)/2))
    percent_opportunity['percent_opportunity'] = percentage_change

    dictionary['highest price'] = float(highest_price)
    dictionary['lowest price'] = float(lowest_price)
    dictionary['highest price network'] = tuples[-1][:1]
    dictionary['lowest price network'] = tuples[0][:1] 
    dictionary['arbitrage opportunity'] = percentage_change
    print(f"Arbitrage opportunity: {percentage_change*100:.2f}%")
    return dictionary

def dictionary_to_google(dictionary, json_file, sheet=0):
    """Converts the output dictionary to dataframe. Exports dataframe to Google Sheets."""
    gc = pygsheets.authorize(service_file=json_file)
    sh = gc.open('usd_pairs')
    df = pd.DataFrame(dictionary)
    
    #df['test'] = df['network']['two', 'three'] # test dataframe info
    wks = sh[sheet]
    wks.insert_rows(1, number=1, values=None, inherit=False) # insert_rows(row, number=1, values=None, inherit=False)
    wks.set_dataframe(df,(1,0), extend=False, copy_head=True) # set_dataframe(df, start, copy_index=False, copy_head=True, extend=False, fit=False, escape_formulae=False, **kwargs)
    return


counter = 0

while counter < 100000:
    ################ VARIABLES - DAI/USDC ############################
    all_networks = ['ethereum', 'bsc', 'polygon', 'fantom']
    querey_buyToken = "DAI"
    querey_sellToken = "USDC"
    querey_amount = "1000"  
    querey_sellToken_decimals = "00000" # only fill if NOT 18 decimals.
    json_gsheet_credential = 'dollar-pairs-f7df709cc2b7.json'
    gsheet_number = 0

    ################ FUNCTION - DAI/USDC ##############################
    print(f"Evaluating {querey_buyToken}/{querey_sellToken}")
    output_dict = {}
    output_dict = dict_init(querey_buyToken, querey_sellToken)

    for network in all_networks:
        response = price_request(network, querey_buyToken, querey_sellToken, querey_amount, querey_sellToken_decimals)
        output_dict = price_eval(response, output_dict, network)

    output_dict = arbitrage(output_dict)
    dictionary_to_google(output_dict, json_gsheet_credential)
    print(f"Complete at {output_dict['Time']}\n")
    time.sleep(15)

    ################ VARIABLES - DAI/WETH ############################
    all_networks = ['ethereum', 'bsc', 'polygon', 'fantom']
    querey_buyToken = "DAI"
    querey_sellToken = "WETH"
    querey_amount = "1"
    querey_sellToken_decimals = "00000000" # only fill if NOT 18 decimals.
    json_gsheet_credential = 'dollar-pairs-f7df709cc2b7.json'
    gsheet_number = 5

    ################ FUNCTION - DAI/WETH ##############################
    print(f"Evaluating {querey_buyToken}/{querey_sellToken}")
    output_dict = {}
    output_dict = dict_init(querey_buyToken, querey_sellToken)

    for network in all_networks:
        response = price_request(network, querey_buyToken, querey_sellToken, querey_amount)
        output_dict = price_eval(response, output_dict, network)

    output_dict = arbitrage(output_dict)
    dictionary_to_google(output_dict, json_gsheet_credential, gsheet_number)
    print(f"Complete at {output_dict['Time']}\n")
    time.sleep(15)


    ################ VARIABLES - USDC/WETH ############################
    all_networks = ['ethereum', 'bsc', 'polygon', 'fantom']
    querey_buyToken = "USDC"
    querey_sellToken = "WETH"
    querey_amount = "1"
    querey_sellToken_decimals = "00000000" # only fill if NOT 18 decimals.
    json_gsheet_credential = 'dollar-pairs-f7df709cc2b7.json'
    gsheet_number = 4

    ################ FUNCTION - DAI/WETH ##############################
    print(f"Evaluating {querey_buyToken}/{querey_sellToken}")
    output_dict = {}
    output_dict = dict_init(querey_buyToken, querey_sellToken)

    for network in all_networks:
        response = price_request(network, querey_buyToken, querey_sellToken, querey_amount)
        output_dict = price_eval(response, output_dict, network)

    output_dict = arbitrage(output_dict)
    dictionary_to_google(output_dict, json_gsheet_credential, gsheet_number)
    print(f"Complete at {output_dict['Time']} \n")
    time.sleep(15)

    ################ VARIABLES - DAI/USDT ############################
    all_networks = ['ethereum', 'bsc', 'polygon', 'fantom']
    querey_buyToken = "DAI"
    querey_sellToken = "USDT"
    querey_amount = "1000"
    querey_sellToken_decimals = "00000" # only fill if NOT 18 decimals.
    json_gsheet_credential = 'dollar-pairs-f7df709cc2b7.json'
    gsheet_number = 1

    ################ FUNCTION - DAI/USDT ##############################
    print(f"Evaluating {querey_buyToken}/{querey_sellToken}")
    output_dict = {}
    output_dict = dict_init(querey_buyToken, querey_sellToken)

    for network in all_networks:
        response = price_request(network, querey_buyToken, querey_sellToken, querey_amount, querey_sellToken_decimals)
        output_dict = price_eval(response, output_dict, network)

    output_dict = arbitrage(output_dict)
    dictionary_to_google(output_dict, json_gsheet_credential, gsheet_number)
    print(f"Complete at {output_dict['Time']} \n")
    time.sleep(15)

     ################ VARIABLES - USDT/WETH ############################
    all_networks = ['ethereum', 'bsc', 'polygon', 'fantom']
    querey_buyToken = "USDT"
    querey_sellToken = "WETH"
    querey_amount = "1"
    querey_sellToken_decimals = "00000" # only fill if NOT 18 decimals.
    json_gsheet_credential = 'dollar-pairs-f7df709cc2b7.json'
    gsheet_number = 3

    ################ FUNCTION - USDC/USDT ##############################
    print(f"Evaluating {querey_buyToken}/{querey_sellToken}")
    output_dict = {}
    output_dict = dict_init(querey_buyToken, querey_sellToken)

    for network in all_networks:
        response = price_request(network, querey_buyToken, querey_sellToken, querey_amount)
        output_dict = price_eval(response, output_dict, network)

    output_dict = arbitrage(output_dict)
    dictionary_to_google(output_dict, json_gsheet_credential, gsheet_number)
    print(f"Complete at {output_dict['Time']} \n")
    time.sleep(15)

    ################ VARIABLES - USDC/USDT ############################
    all_networks = ['ethereum', 'bsc', 'polygon', 'fantom']
    querey_buyToken = "USDC"
    querey_sellToken = "USDT"
    querey_amount = "1000"
    querey_sellToken_decimals = "00000" # only fill if NOT 18 decimals.
    json_gsheet_credential = 'dollar-pairs-f7df709cc2b7.json'
    gsheet_number = 2

    ################ FUNCTION - USDC/USDT ##############################
    print(f"Evaluating {querey_buyToken}/{querey_sellToken}")
    output_dict = {}
    output_dict = dict_init(querey_buyToken, querey_sellToken)

    for network in all_networks:
        response = price_request(network, querey_buyToken, querey_sellToken, querey_amount, querey_sellToken_decimals)
        output_dict = price_eval(response, output_dict, network)

    output_dict = arbitrage(output_dict)
    dictionary_to_google(output_dict, json_gsheet_credential, gsheet_number)
    print(f"Complete at {output_dict['Time']} \nData avalable at 'https://docs.google.com/spreadsheets/d/1hUwgdLyBYbSbduUKBS9PH-Q3_7TY6ty3VAF3GcC20XI/edit?usp=sharing'")
    time.sleep(15)
    

    counter +=1