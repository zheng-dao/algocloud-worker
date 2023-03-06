#!/usr/bin/python
from tkinter.messagebox import NO
import requests
import datetime


api_url_base = 'https://mainnet.analytics.tinyman.org/api/v1'


def get(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()


def fetch_assets(asset_price_dict):
    assets = []
    api_url = '{0}/assets/?limit=10&is_pool_member=true&with_statistics=true&verified_only=false'.format(api_url_base)
    while api_url:
        response = get(api_url)
        if response is None:
            return None

        api_url = response['next']
        results = response['results']
        for asset in results:
            if asset['unit_name'] in asset_price_dict:
                price = asset_price_dict[asset['unit_name']]
            else:
                price = None
            try:
                # mc_url = "https://algoexplorerapi.io/v1/asset/{0}/info".format(asset['id'])
                mc_url = "https://indexer.algoexplorerapi.io/v2/assets/{0}?include-all=true".format(asset['id'])
                mc_res = get(mc_url)
                if mc_res is None:
                    if int(asset['id']) == 0:
                        mc_url = 'https://metricsapi.algorand.foundation/v1/supply/circulating?unit=algo'
                        mc_res = get(mc_url)
                        print("Algorand Supply Circulating...")
                        marketCap = float(mc_res)
                    else:
                        marketCap = None
                else:
                    if mc_res['asset']['params']['circulating-supply'] is None:
                        if int(asset['id']) == 0:
                            mc_url = 'https://metricsapi.algorand.foundation/v1/supply/circulating?unit=algo'
                            mc_res = get(mc_url)
                            print("Algorand Supply Circulating...")
                            marketCap = mc_res
                        else:
                            marketCap = None
                    else:
                        if price is not None:
                            decimals = int(mc_res['asset']['params']['decimals'])
                            marketCap = int(mc_res['asset']['params']['circulating-supply']) / 10**decimals
                        else:
                            marketCap = None
            except (Exception) as error:
                print(error)
            if (price is not None) and (marketCap is not None):
                marketCap = int(float(marketCap) * price)
            else:
                marketCap = 0

            print(asset['name'])
            print(asset['id'])
            print(marketCap)

            assets.append({
                'assetId': asset['id'],
                'name': asset['name'],
                'price': price,
                'unitName': asset['unit_name'],
                'liquidity': asset['liquidity_in_usd'],
                'lastDayVolume': asset['last_day_volume_in_usd'],
                'lastDayPriceChange': asset['last_day_price_change'],
                'createdDate': datetime.datetime.now(),
                'marketCap': marketCap
            })

    return assets


def fetch_pools():
    pools = []
    asset_dict = {'USDC': 1.0}
    api_url = '{0}/pools/?limit=20&ordering=-liquidity&with_statistics=true&verified_only=true'.format(api_url_base)
    while api_url:
        response = get(api_url)
        if response is None:
            return None

        api_url = response['next']
        results = response['results']
        print("\nFetching pools result")
        for pool in results:
            pools.append({
                'address': pool['address'],
                'name': pool['liquidity_asset']['name'],
                'unitName': pool['liquidity_asset']['unit_name'],
                'assetOneId': pool['asset_1']['id'],
                'assetOneName': pool['asset_1']['name'],
                'assetOneUnitName': pool['asset_1']['unit_name'],
                'assetOneReserves': pool['current_asset_1_reserves'],
                'assetTwoId': pool['asset_2']['id'],
                'assetTwoName': pool['asset_2']['name'],
                'assetTwoUnitName': pool['asset_2']['unit_name'],
                'assetTwoReserves': pool['current_asset_2_reserves'],
                'liquidity': pool['liquidity_in_usd'],
                'lastDayVolume': pool['last_day_volume_in_usd'],
                'lastWeekVolume': pool['last_week_volume_in_usd'],
                'lastDayFees': pool['last_day_fees_in_usd'],
                'createdDate': datetime.datetime.now()
            })
            try:
                print(pool['asset_1']['unit_name'] + '/' + pool['asset_2']['unit_name'])
                if pool['asset_1']['unit_name'] == 'ALGO' and pool['asset_2']['unit_name'] == 'USDC':
                    asset_dict['ALGO'] = (float(pool['current_asset_2_reserves'])  / 10**(pool['asset_2']['decimals'])) / (float(pool['current_asset_1_reserves'])  / 10**(pool['asset_1']['decimals']))
                elif pool['asset_1']['unit_name'] == 'USDC' and pool['asset_2']['unit_name'] == 'ALGO':
                    asset_dict['ALGO'] = (float(pool['current_asset_1_reserves'])   / 10**(pool['asset_1']['decimals'])) / (float(pool['current_asset_2_reserves'])  / 10**(pool['asset_2']['decimals']))
                elif pool['asset_1']['unit_name'] == 'ALGO':
                    print("Algo")
                    if pool['asset_2']['unit_name'] in asset_dict:
                        continue
                    else:
                        asset_dict[pool['asset_2']['unit_name']] = asset_dict['ALGO'] * (float(pool['current_asset_1_reserves'])  / 10**(pool['asset_1']['decimals'])) / (float(pool['current_asset_2_reserves'])  / 10**(pool['asset_2']['decimals']))
                elif pool['asset_2']['unit_name'] == 'ALGO':
                    print("Algo2")
                    if pool['asset_1']['unit_name'] in asset_dict:
                        continue
                    else:
                        asset_dict[pool['asset_1']['unit_name']] = asset_dict['ALGO'] * (float(pool['current_asset_2_reserves'])  / 10**(pool['asset_2']['decimals'])) / (float(pool['current_asset_1_reserves'])  / 10**(pool['asset_1']['decimals']))
                elif pool['asset_1']['unit_name'] == 'USDC':
                    print("USDC")
                    if pool['asset_2']['unit_name'] in asset_dict:
                        continue
                    else:
                        asset_dict[pool['asset_2']['unit_name']] = (float(pool['current_asset_1_reserves'])  / 10**(pool['asset_1']['decimals'])) / (float(pool['current_asset_2_reserves'])  / 10**(pool['asset_2']['decimals']))
                elif pool['asset_2']['unit_name'] == 'USDC':
                    print("USDC2")
                    if pool['asset_1']['unit_name'] in asset_dict:
                        continue
                    else:
                        asset_dict[pool['asset_1']['unit_name']] = (float(pool['current_asset_2_reserves'])  / 10**(pool['asset_2']['decimals'])) / (float(pool['current_asset_1_reserves'])  / 10**(pool['asset_1']['decimals']))
                else:
                    print("Others")
                    if (pool['asset_1']['unit_name'] in asset_dict) and (pool['asset_2']['unit_name'] not in asset_dict):
                        asset_dict[pool['asset_2']['unit_name']] = asset_dict[pool['asset_1']['unit_name']] * (float(pool['current_asset_1_reserves'])  / 10**(pool['asset_1']['decimals'])) / (float(pool['current_asset_2_reserves'])  / 10**(pool['asset_2']['decimals']))
                    if (pool['asset_2']['unit_name'] in asset_dict) and (pool['asset_1']['unit_name'] not in asset_dict):
                        asset_dict[pool['asset_1']['unit_name']] = asset_dict[pool['asset_2']['unit_name']] * (float(pool['current_asset_2_reserves'])  / 10**(pool['asset_2']['decimals'])) / (float(pool['current_asset_1_reserves'])  / 10**(pool['asset_1']['decimals']))

            except (Exception) as error:
                print("Handling error for pools data")
                print(error)

    print('@@@@@@@@@@@@@@@@@@@@@@')
    print(asset_dict)
    print('@@@@@@@@@@@@@@@@@@@@@@')
    return [pools, asset_dict]


def fetch_algo_stats():
    api_url = '{0}/general-statistics/'.format(api_url_base)
    response = get(api_url)
    if response is None:
        return None

    return {
        'totalLiquidity': response['total_liquidity_in_usd'],
        'lastDayVolume': response['last_day_total_volume_in_usd'],
        'lastDayPriceChange': response['last_day_algo_price_change'],
        'createdDate': datetime.datetime.now(),
    }
