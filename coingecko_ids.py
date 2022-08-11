from collections import defaultdict

import httpx

from common import ChainId, Address


def get_coingecko_ids() -> dict[ChainId, dict[Address, str]]:
    chain_id_to_coingecko_platform = {
        "1284": "moonbeam",
        "361": "theta",
        "592": "astar",
        "70": "hoo-smart-chain",
        "122": "fuse",
        "42262": "oasis",
        "128": "huobi-token",
        "321": "kucoin-community-chain",
        "42161": "arbitrum-one",
        "1088": "metis-andromeda",
        "56": "binance-smart-chain",
        "66": "okex-chain",
        "250": "fantom",
        "88": "tomochain",
        "82": "meter",
        "1818": "cube-network",
        "42220": "celo",
        "10": "optimistic-ethereum",
        "137": "polygon-pos",
        "43114": "avalanche",
        "1285": "moonriver",
        "25": "cronos",
        "288": "boba",
        "10000": "smartbch",
        "1313161554": "aurora",
        "1666600000": "harmony-shard-0",
        "100": "xdai",
        "1": "ethereum",
        "32659": "fusion-network",
        "40": "telos",
        "-1": "solana",
        "9001": "evmos"
    }
    coingecko_platform_to_chain_id = {v: k for k, v in chain_id_to_coingecko_platform.items()}
    coins = httpx.get('https://api.coingecko.com/api/v3/coins/list', params={'include_platform': True}).json()
    res = defaultdict(dict)
    for coin in coins:
        if not coin['id']:
            continue
        for platform, address in coin.get('platforms', {}).items():
            if platform and address and platform in coingecko_platform_to_chain_id:
                res[coingecko_platform_to_chain_id[platform]][address.lower()] = coin['id']
    return res


coingecko_ids = get_coingecko_ids()
