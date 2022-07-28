import asyncio
import json
from collections import defaultdict

import httpx
from web3 import Web3

from coingecko_ids import coingecko_ids
from common import ChainId, Address, NATIVE_ADDRESSES, Token, CHAIN_NAMES_BY_ID

TOKENLISTS_FOLDER = "tokenlists"


class TokenListProvider:
    name: str
    base_url: str
    chains: dict[ChainId, str]
    _by_chain_id = False
    _tokens_to_list = False

    @staticmethod
    def _filter_tokens(tokens: list[Token], chain_id: str) -> list[Token]:
        res = []
        for token in tokens:
            if not token["address"]:
                continue
            try:
                token["address"] = token["address"].strip()
                if token["address"].startswith("0x"):
                    token["address"] = Web3.toChecksumAddress(token["address"])
                cg_id = coingecko_ids.get(chain_id, {}).get(token["address"].lower())
                logo = token.get("logoURI") or token.get("icon") or token.get("image")
                if logo and logo.startswith('//'):
                    logo = 'https:' + logo
                t = Token(
                    address=token["address"],
                    symbol=token["symbol"],
                    name=token["name"],
                    decimals=token["decimals"],
                    chainId=chain_id,
                    logoURI=logo,
                    coingeckoId=cg_id
                )
                res.append(t)
            except Exception as exc:
                print(chain_id, token["address"], exc, token)
        return res

    @classmethod
    async def get_tokenlists(cls) -> dict[str, dict[ChainId, list[Token]]]:
        res: dict[ChainId, list[Token]] = defaultdict(list)

        for chain_id, chain_name in cls.chains.items():
            resp = await httpx.AsyncClient().get(cls.base_url.format(chain_id if cls._by_chain_id else chain_name))
            num_retries = 0
            while resp.status_code != 200:
                if num_retries > 60:
                    raise Exception(f"failed to get tokenlits {cls.base_url} after {num_retries} retries")
                sleep_time = int(resp.headers.get("Retry-After", 1))
                num_retries += 1
                print(f"[{cls.name}] {chain_id} {chain_name} waiting {sleep_time} seconds")
                await asyncio.sleep(sleep_time)
                resp = await httpx.AsyncClient().get(cls.base_url.format(chain_id if cls._by_chain_id else chain_name))
            tokenlist = resp.json()
            if "tokens" in tokenlist:
                tokens = tokenlist["tokens"]
            elif "data" in tokenlist:
                tokens = tokenlist["data"]
            else:
                tokens = tokenlist

            if cls._tokens_to_list:
                tokens = list(tokens.values())

            res[chain_id] = cls._filter_tokens(tokens, chain_id)
            print(f"[{cls.name}] {chain_id} {chain_name} OK")
        return {cls.name: res}


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
        "1": "ethereum",
        "-1": "solana"
        # sora
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
        "1284": "moonbeam",
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
    _tokens_to_list = True


class SolanaLabsTokenLists(TokenListProvider):
    name = "solanalabs"
    base_url = "https://raw.githubusercontent.com/solana-labs/token-list/main/src/tokens/{}.tokenlist.json"
    chains = {
        "-1": "solana"
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


# TODO: support
class RefFinanceTokenLists(TokenListProvider):
    # unusual format
    base_url = "https://indexer.ref-finance.net/list-token"


class OneSolTokenLists(TokenListProvider):
    name = "1sol"
    base_url = "https://raw.githubusercontent.com/1sol-io/token-list/fb6336f63b1511c095bd5160277983a6ad3c8aa5/src/tokens/solana.tokenlist.json"
    chains = {
        "-1": "solana"
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


class TrisolarisLabsLists(TokenListProvider):
    name = "trisolaris"
    base_url = "https://raw.githubusercontent.com/trisolaris-labs/tokens/master/lists/{}/list.json"
    chains = {
        "1313161554": "1313161554",
    }


class RubicLists(TokenListProvider):
    name = "rubic"
    base_url = "https://api.rubic.exchange/api/tokens/?network={}"
    chains = {
        "-2": "near",
        "-1": "solana",
        "1": "ethereum",
        # "25": "cronos",
        '40': 'telos',
        "56": "binance-smart-chain",
        "100": "xdai",
        "137": "polygon",
        "250": "fantom",
        "1284": "moonbeam",
        "1285": "moonriver",
        "42161": "arbitrum",
        "43114": "avalanche",
        "1313161554": "aurora",
        "1666600000": "harmony",
    }


class CronaSwapLists(TokenListProvider):
    name = "cronaswap"
    base_url = "https://raw.githubusercontent.com/cronaswap/default-token-list/main/assets/tokens/cronos.json"
    chains = {'25': 'cronos'}


tokenlists_providers = [
    CoinGeckoTokenLists,
    OneInchTokenLists,
    UniswapTokenLists,
    SushiswapTokenLists,
    OpenOceanTokenLists,
    SolanaLabsTokenLists,
    ElkFinanceTokenLists,
    OneSolTokenLists,
    QuickSwapTokenLists,
    FuseSwapTokenLists,
    TrisolarisLabsLists,
    RubicLists,
    CronaSwapLists,
]


async def collect_trusted_tokens() -> dict[ChainId, dict[Address, Token]]:
    data = await asyncio.gather(*[provider.get_tokenlists() for provider in tokenlists_providers])
    provider_data: dict[str, dict[ChainId, list[Token]]] = {}
    for prov in data:
        provider_data |= prov

    res = defaultdict(dict)
    for provider_name, tokens_by_chains in provider_data.items():
        for chain_id, tokens in tokens_by_chains.items():
            for token in tokens:
                addr = token["address"].strip().lower()
                if addr.lower() in NATIVE_ADDRESSES:  # skip native tokens
                    continue
                # if addr.startswith('0x'):
                #     token['address'] = Web3.toChecksumAddress(addr)
                if addr in res[chain_id]:
                    if "listedIn" in res[chain_id][addr]:
                        res[chain_id][addr] |= token
                        if provider_name not in res[chain_id][addr]["listedIn"]:
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
    trusted = {k: v for k, v in trusted.items() if len(v) > 0}
    trusted = {k: list(sorted(v.values(), key=lambda x: x['address'], reverse=True)) for k, v in trusted.items()}
    for chain_id, tokens in trusted.items():
        filename = f"{TOKENLISTS_FOLDER}/{CHAIN_NAMES_BY_ID[chain_id]}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(tokens, f, ensure_ascii=False, indent=4)
    with open(f"{TOKENLISTS_FOLDER}/all.json", "w", encoding="utf-8") as f:
        json.dump(trusted, f, ensure_ascii=False, indent=4)

    print("collected trusted tokens")
    return trusted


if __name__ == "__main__":
    asyncio.run(collect_trusted_tokens())
