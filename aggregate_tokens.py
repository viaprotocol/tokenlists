import json
import os
from collections import defaultdict
from time import sleep
from typing import Union, TypedDict

import httpx

TOKENLISTS_FOLDER = "tokenlists"


class Token(TypedDict):
    symbol: str
    name: str
    address: str
    decimals: str
    chainId: str
    logoURI: str


class TokenListProvider:
    name: str
    base_url: str
    chains: dict[Union[str, int], str]
    _by_chain_id = False
    _set_chain_id = False
    _tokens_to_list = False

    @classmethod
    def get_tokenlists(cls):
        for chain_id, chain_name in cls.chains.items():
            resp = httpx.get(cls.base_url.format(chain_id if cls._by_chain_id else chain_name))
            while resp.status_code != 200:
                sleep_time = int(resp.headers.get("Retry-After", 1))
                print(f"[{cls.name}] {chain_id} {chain_name} waiting {sleep_time} seconds")
                sleep(sleep_time)
                resp = httpx.get(cls.base_url.format(chain_id if cls._by_chain_id else chain_name))
            tokenlist = resp.json()
            filename = f"{TOKENLISTS_FOLDER}/{cls.name}/{chain_name}.json"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            if "tokens" in tokenlist:
                tokens = tokenlist["tokens"]
            elif "data" in tokenlist:
                tokens = tokenlist["data"]
            else:
                tokens = tokenlist
            if cls._set_chain_id:
                for token in tokens.values():
                    token["chainId"] = chain_id
            if cls._tokens_to_list:
                tokens = list(tokens.values())
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(tokens, f, ensure_ascii=False, indent=4)
            print(f"[{cls.name}] {chain_id} {chain_name} OK")

    @classmethod
    def tokens_by_chains(cls) -> dict[str, list[Token]]:
        res = defaultdict(list)
        for chain_id, chain_name in cls.chains.items():
            with open(f"{TOKENLISTS_FOLDER}/{cls.name}/{chain_name}.json") as f:
                tokens = json.load(f)
                for token in tokens:
                    tkn = Token(**token)
                    res[chain_id].append(tkn)

        return res


class CoinGeckoTokenLists(TokenListProvider):
    name = "coingecko"
    base_url = "https://tokens.coingecko.com/{}/all.json"
    chains = {
        "1284": "moonbeam",
        "361": "theta",
        "70": "hoo-smart-chain",
        "42161": "arbitrum-one",
        "56": "binance-smart-chain",
        "66": "okex-chain",
        "250": "fantom",
        "88": "tomochain",
        "82": "meter",
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
        "1": "ethereum"
    }


class UniswapTokenLists(TokenListProvider):
    name = "uniswap"
    base_url = "https://raw.githubusercontent.com/Uniswap/default-token-list/main/src/tokens/{}.json"
    chains = {
        "5": "goerli",
        "42": "kovan",
        "1": "mainnet",
        "80001": "mumbai",
        "137": "polygon",
        "4": "rinkeby",
        "3": "ropsten",
    }


class SushiswapTokenLists(TokenListProvider):
    name = "sushiswap"
    base_url = "https://raw.githubusercontent.com/sushiswap/default-token-list/master/tokens/{}.json"
    chains = {
        "42161": "arbitrum",
        "43114": "avalanche",
        "97": "bsc-testnet",
        "56": "bsc",
        "42220": "celo",
        "1024": "clover",
        "4002": "fantom-testnet",
        "250": "fantom",
        "43113": "fuji",
        "122": "fuse",
        "5": "goerli",
        "1666700000": "harmony-testnet",
        "1666600000": "harmony",
        "256": "heco-testnet",
        "128": "heco",
        "42": "kovan",
        "1": "mainnet",
        "80001": "matic-testnet",
        "137": "matic",
        "1287": "moonbase",
        "1285": "moonriver",
        "65": "okex-testnet",
        "66": "okex",
        "11297108109": "palm",
        "4": "rinkeby",
        "3": "ropsten",
        "40": "telos",
        "100": "xdai"
    }


class OneInchTokenLists(TokenListProvider):
    name = "1inch"
    base_url = "https://api.1inch.io/v4.0/{}/tokens"
    chains = {
        "1": "ethereum",
        "10": "optimism",
        "56": "bsc",
        "100": "gnosis",
        "137": "polygon",
        "43114": "avalanche",
        "42161": "arbitrum",
    }
    _by_chain_id = True
    _set_chain_id = True
    _tokens_to_list = True


class SolanaLabsTokenLists(TokenListProvider):
    name = "solanalabs"
    base_url = "https://raw.githubusercontent.com/solana-labs/token-list/main/src/tokens/{}.tokenlist.json"
    chains = {
        "101": "solana"
    }


class OpenOceanTokenLists(TokenListProvider):
    # TODO: maybe more, check all ids from coingecko
    name = "openocean"
    base_url = "https://open-api.openocean.finance/v1/cross/tokenList?chainId={}"
    chains = {
        "42161": "arbitrum-one",
        "43114": "avalanche",
        "56": "binance-smart-chain",
        "66": "okex-chain",
        "250": "fantom",
        "10": "optimistic-ethereum",
        "137": "polygon-pos",
        "288": "boba",
        "100": "xdai-gnosis",
        "128": "heco",
        "1": "ethereum",
    }
    _by_chain_id = True


class ElkFinanceTokenLists(TokenListProvider):
    name = "elkfinance"
    base_url = "https://raw.githubusercontent.com/elkfinance/tokens/main/{}.tokenlist.json"
    chains = {
        "42161": "farms",
        "43114": "avax",
        "56": "bsc",
        "25": "cronos",
        "20": "elastos",
        "1": "ethereum",
        "250": "ftm",
        "4002": "ftmtest",
        "43113": "fuji",
        "122": "fuse",
        "1666600000": "harmony",
        "128": "heco",
        "70": "hoo",
        "4689": "iotex",
        "321": "kcc",
        "137": "matic",
        "1285": "moonriver",
        "80001": "mumbai",
        "66": "okex",
        "40": "telos",
        "100": "xdai"
    }
    # "all", "top"


class RefFinanceTokenLists(TokenListProvider):
    # unusual format
    base_url = "https://indexer.ref-finance.net/list-token"


class OneSolTokenLists(TokenListProvider):
    name = "1sol"
    base_url = "https://raw.githubusercontent.com/1sol-io/token-list/main/src/tokens/solana.tokenlist.json"
    chains = {
        "101": "solana"
    }


class QuickSwapTokenLists(TokenListProvider):
    name = "quickswap"
    base_url = "https://raw.githubusercontent.com/sameepsi/quickswap-default-token-list/master/src/tokens/mainnet.json"
    chains = {
        "137": "polygon"
    }


class FuseSwapTokenLists(TokenListProvider):
    name = "fuseswap"
    base_url = "https://raw.githubusercontent.com/fuseio/fuseswap-default-token-list/master/src/tokens/fuse.json"
    chains = {
        "122": "fuse"
    }


tokelists_providers = [
    CoinGeckoTokenLists,
    OneInchTokenLists,
    UniswapTokenLists,
    SushiswapTokenLists,
    SolanaLabsTokenLists,
    OpenOceanTokenLists,
    ElkFinanceTokenLists,
    OneSolTokenLists,
    QuickSwapTokenLists,
    FuseSwapTokenLists
]


def agg():
    for provider in tokelists_providers:
        provider.get_tokenlists()


def collect_trusted_tokens():
    provider_data: dict[str, dict[str, list[Token]]] = {}
    for provider in tokelists_providers:
        provider_data[provider.name] = provider.tokens_by_chains()

    res = defaultdict(dict)
    for provider_name, tokens_by_chains in provider_data.items():
        for chain_id, tokens in tokens_by_chains.items():
            for token in tokens:
                addr = token["address"].lower()
                if addr in res[chain_id]:
                    if "listedIn" in res[chain_id][addr]:
                        res[chain_id][addr]["listedIn"].append(provider_name)
                    else:
                        res[chain_id][addr]["listedIn"] = [provider_name]
                else:
                    res[chain_id][addr] = token
                    res[chain_id][addr]["listedIn"] = [provider_name]

    trusted = {
        chain_id: {addr: token for addr, token in tokens.items() if len(token["listedIn"]) > 1} for
        chain_id, tokens in res.items()
    }
    filename = f"{TOKENLISTS_FOLDER}/trusted.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(trusted, f, ensure_ascii=False, indent=4)
    print('collected trusted tokens')


if __name__ == "__main__":
    agg()
    collect_trusted_tokens()
