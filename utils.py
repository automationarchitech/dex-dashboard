import json

def parse_crypto_pools(json_payload):
    # Convert the JSON payload to a Python dictionary
    data = json_payload

    # List to hold parsed pool data
    parsed_pools = []

    # Iterate through each pool in the data
    for pool in data['data']:
        # Extract relevant information from each pool
        pool_info = {
            'address': pool['attributes']['address'],
            'name': pool['attributes']['name'],
            'pool_created_at': pool['attributes']['pool_created_at'],
            'fdv_usd': pool['attributes'].get('fdv_usd'),
            'market_cap_usd': pool['attributes'].get('market_cap_usd'),
            'volume_usd_h1': pool['attributes']['volume_usd']['h1'],
            'volume_usd_h24': pool['attributes']['volume_usd']['h24'],
            'price_change_percentage_h1': json.loads(pool['attributes']['price_change_percentage']['h1']),
            'price_change_percentage_h24': json.loads(pool['attributes']['price_change_percentage']['h24']),
            'transactions_h1_buys': pool['attributes']['transactions']['h1']['buys'],
            'transactions_h1_sells': pool['attributes']['transactions']['h1']['sells'],
        }
        parsed_pools.append(pool_info)

    return parsed_pools

