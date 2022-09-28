import asyncio
import json
import logging.config
from collections import defaultdict

import httpx
import yaml

from coingecko_ids import coingecko_ids
from common import ChainId, Token


with open("./logger.yml", "r") as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

logging.config.dictConfig(config)

log = logging.getLogger(__name__)


class TokenListProvider:
    name: str
    base_url: str
    chains: dict[str, str]
    _by_chain_id = False
    _get_chain_id_key = False
    _tokens_to_list = False
    absent_chain_id = False

    @classmethod
    async def get_tokenlists(cls) -> dict[str, dict[ChainId, list[Token]]]:
        res: dict[ChainId, list[Token]] = defaultdict(list)

        for chain_id, chain_name in cls.chains.items():
            try:
                resp = await httpx.AsyncClient().get(
                    cls.base_url.format(chain_id if cls._by_chain_id else chain_name))
            except httpx.ReadTimeout:
                await asyncio.sleep(0.5)
                continue
            num_retries = 0
            while resp.status_code != 200:
                if num_retries > 60:
                    raise Exception(f"failed to get tokenlits {cls.base_url} after {num_retries} retries")
                sleep_time = int(resp.headers.get("Retry-After", 1))
                num_retries += 1
                log.info(f"[{cls.name}] {chain_id} {chain_name} waiting {sleep_time} seconds")
                await asyncio.sleep(sleep_time)
                resp = await httpx.AsyncClient().get(cls.base_url.format(chain_id if cls._by_chain_id else chain_name))

            try:
                tokenlist = resp.json()
            except:
                tokenlist = json.loads(resp.text)
            if "tokens" in tokenlist:
                raw_tokens = tokenlist["tokens"]
            elif "data" in tokenlist:
                raw_tokens = tokenlist["data"]
            elif "results" in tokenlist:
                raw_tokens = tokenlist["results"]
            elif "recommendedTokens" in tokenlist:
                raw_tokens = tokenlist["recommendedTokens"]
            else:
                raw_tokens = tokenlist

            if cls._get_chain_id_key and str(chain_id) in raw_tokens:
                raw_tokens = raw_tokens[str(chain_id)]

            if cls._tokens_to_list:
                raw_tokens = list(raw_tokens.values())

            tokens: list[Token] = []
            for t in raw_tokens:

                if not isinstance(t, dict):
                    log.error(f"Token must be of type dict, got {t=} {cls.__name__}")
                    continue
                if not t.get("chainId"):
                    if cls.absent_chain_id:
                        t["chainId"] = chain_id
                    else:
                        log.error(f"{cls.name} chain id absent")
                        continue
                if not t.get("coingeckoId"):
                    t["coingeckoId"] = coingecko_ids.get(str(t["chainId"]), {}).get(t["address"].lower())
                parsed_token = Token.parse_obj(t)
                res[parsed_token.chainId].append(parsed_token)
            log.info(f"[{cls.name}] {chain_id} {chain_name} OK")
        return {cls.name: res}


class CoinGeckoTokenLists(TokenListProvider):
    name = "coingecko"
    base_url = "https://tokens.coingecko.com/{}/all.json"
    chains = {
        "592": "astar",
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
        "-1": "solana",
        "9001": "evmos",
        # sora
    }
    absent_chain_id = True


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
        "1": "1",
        "56": "56",
        "137": "137",
        "10": "10",
        "42161": "42161",
        "100": "100",
        "43114": "43114",
        "250": "250",
        "1313161554": "1313161554",
    }
    _tokens_to_list = True
    absent_chain_id = True


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
    absent_chain_id = True


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
        "40": "telos",
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
    absent_chain_id = True


class CronaSwapLists(TokenListProvider):
    name = "cronaswap"
    base_url = "https://raw.githubusercontent.com/cronaswap/default-token-list/main/assets/tokens/cronos.json"
    chains = {"25": "cronos"}


class Ubeswap(TokenListProvider):
    name = "ubeswap"
    base_url = "https://raw.githubusercontent.com/Ubeswap/default-token-list/master/ubeswap.token-list.json"
    chains = {"42220": "celo"}


class OolongSwap(TokenListProvider):
    name = "oolongswap"
    base_url = "https://raw.githubusercontent.com/OolongSwap/boba-community-token-list/main/src/tokens/boba.json"
    chains = {"288": "boba"}


class Multichain(TokenListProvider):
    name = "multichain"
    base_url = "https://bridgeapi.anyswap.exchange/v4/poollist/{}"
    chains = {"592": "592"}
    _tokens_to_list = True


class XyFinance(TokenListProvider):
    name = "xyfinance"
    base_url = "https://open-api.xy.finance/v1/recommendedTokens?chainId={}"
    chains = {
        "1": "1",
        "56": "56",
        "137": "137",
        "250": "250",
        "25": "25",
        "43114": "43114",
        "42161": "42161",
        "10": "10",
        "1285": "1285",
        "592": "592",
        "321": "321",
        "1818": "1818",
    }


class MojitoSwap(TokenListProvider):
    name = "mojitoswap"
    base_url = "https://raw.githubusercontent.com/MojitoFinance/mjtTokenList/461d2ca814d12c37516b986fabfcd21446283ed7/mjtTokenList.json"
    chains = {"321": "321"}
    absent_chain_id = True


class CapricornFinance(TokenListProvider):
    name = "capricorn_finance"
    base_url = "https://raw.githubusercontent.com/capricorn-finance/info-blist/main/list.json"
    chains = {"1818": "1818"}


class Lifinance(TokenListProvider):
    name = "lifinance"
    base_url = "https://li.quest/v1/tokens?chains={}"
    _get_chain_id_key = True

    chains = {
        "1": "1",
        "10": "10",
        "25": "25",
        "56": "56",
        "66": "66",
        "100": "100",
        "122": "122",
        "137": "137",
        "250": "250",
        "1284": "1284",
        "1285": "1285",
        "9001": "9001",
        "42161": "42161",
        "42220": "42220",
        "43114": "43114",
        "1666600000": "1666600000",
    }


class Dfyn(TokenListProvider):
    name = "dfyn"
    base_url = "https://raw.githubusercontent.com/dfyn/new-host/main/list-token.tokenlist.json"

    chains = {
        "1": "1",
        "10": "10",
        "25": "25",
        "56": "56",
        "137": "137",
        "250": "250",
        "43114": "43114",
        "1666600000": "1666600000",
    }


class PancakeSwap(TokenListProvider):
    name = "pancake"
    base_url = "https://tokens.pancakeswap.finance/pancakeswap-extended.json"

    chains = {"56": "56"}


class Pangolin(TokenListProvider):
    name = "pangolin"
    base_url = "https://raw.githubusercontent.com/pangolindex/tokenlists/main/pangolin.tokenlist.json"

    chains = {"43114": "43114"}


class TraderJoe(TokenListProvider):
    name = "joe"
    base_url = "https://raw.githubusercontent.com/traderjoe-xyz/joe-tokenlists/main/joe.tokenlist.json"

    chains = {"43114": "43114"}


class ArbitrumBridge(TokenListProvider):
    name = "arbitrum_bridge"
    base_url = "https://bridge.arbitrum.io/token-list-42161.json"

    chains = {"42161": "42161", "1": "1"}


class Optimism(TokenListProvider):
    name = "optimism"
    base_url = "https://static.optimism.io/optimism.tokenlist.json"

    chains = {"1": "1", "10": "10", }


class SpookySwap(TokenListProvider):
    name = "SpookySwap"
    base_url = "https://raw.githubusercontent.com/SpookySwap/spooky-info/master/src/constants/token/spookyswap.json"

    chains = {"250": "250"}


class RouterProtocol(TokenListProvider):
    name = "RouterProtocol"
    base_url = "https://raw.githubusercontent.com/router-protocol/reserve-asset-list/main/router-reserve-asset.json"

    chains = {
        "1": "1",
        "10": "10",
        "25": "25",
        "56": "56",
        "137": "137",
        "250": "250",
        "42161": "42161",
        "1313161554": "1313161554",
        "1666600000": "1666600000",
    }


tokenlists_providers = [
    CoinGeckoTokenLists,
    OneInchTokenLists,
    UniswapTokenLists,
    SushiswapTokenLists,
    OpenOceanTokenLists,
    SolanaLabsTokenLists,
    OneSolTokenLists,
    QuickSwapTokenLists,
    FuseSwapTokenLists,
    TrisolarisLabsLists,
    Dfyn,
    RouterProtocol,
    SpookySwap,
    Optimism,
    ArbitrumBridge,
    TraderJoe,
    Pangolin,
    PancakeSwap,
    MojitoSwap,
    RubicLists,
    Lifinance,
    XyFinance,
    ElkFinanceTokenLists,
    Multichain,
    CronaSwapLists,
    Ubeswap,
    OolongSwap,
    CapricornFinance,
]
