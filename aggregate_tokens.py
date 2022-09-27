import asyncio
import json
import logging
from collections import defaultdict

from common import ChainId, Address, NATIVE_ADDRESSES, Token, CHAIN_NAMES_BY_ID
from token_list_providers import tokenlists_providers

TOKENLISTS_FOLDER = "tokenlists"

log = logging.getLogger(__name__)


async def collect_trusted_tokens() -> dict[ChainId, dict[Address, Token]]:
    data = await asyncio.gather(*[provider.get_tokenlists() for provider in
                                  tokenlists_providers])
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

    log.info("Succesfully collected trusted tokens")
    return trusted


if __name__ == "__main__":
    asyncio.run(collect_trusted_tokens())
