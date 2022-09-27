import asyncio
import json
import logging
from collections import defaultdict

from common import Address, NATIVE_ADDRESSES, Token, CHAIN_NAMES_BY_ID
from token_list_providers import tokenlists_providers

TOKENLISTS_FOLDER = "tokenlists"

ALL_TOKENS_FOLDER = "all_tokens"

log = logging.getLogger(__name__)


async def collect_trusted_tokens() -> dict[int, list[Token]]:
    data = await asyncio.gather(
        *[provider.get_tokenlists() for provider in
            tokenlists_providers]
        )
    provider_data: dict[str, dict[str, list[Token]]] = {}
    for prov in data:
        provider_data |= prov

    res: dict[int, dict[Address, Token]] = defaultdict(dict)
    for provider_name, tokens_by_chains in provider_data.items():
        for _chain_id, tokens in tokens_by_chains.items():
            chain_id = int(_chain_id)
            for token in tokens:
                addr = Address(token.address.lower())
                if addr.lower() in NATIVE_ADDRESSES:  # skip native tokens
                    continue
                if addr in res[chain_id]:
                    if provider_name not in res[chain_id][addr].listedIn:
                        res[chain_id][addr].listedIn.append(provider_name)
                else:
                    res[chain_id][addr] = token
                    res[chain_id][addr].listedIn.append(provider_name)

    all_tokens = {
        k: list(sorted(v.values(), key=lambda x: x.address, reverse=True)) for k, v in res.items() if len(v) > 0
    }

    trusted = {k: [t for t in v if len(t.listedIn) > 1] for k, v in all_tokens.items()}

    # trusted tokens
    for chain_id, tokens in trusted.items():
        filename = f"{TOKENLISTS_FOLDER}/{CHAIN_NAMES_BY_ID[str(chain_id)]}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([t.dict() for t in tokens], f, ensure_ascii=False, indent=4)
    with open(f"{TOKENLISTS_FOLDER}/all.json", "w", encoding="utf-8") as f:
        json.dump({k: [t.dict() for t in v] for k, v in trusted.items()}, f, ensure_ascii=False, indent=4)

    # all tokens found
    for chain_id, tokens in all_tokens.items():
        filename = f"{ALL_TOKENS_FOLDER}/{CHAIN_NAMES_BY_ID[str(chain_id)]}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([t.dict() for t in tokens], f, ensure_ascii=False, indent=4)
    with open(f"{ALL_TOKENS_FOLDER}/all.json", "w", encoding="utf-8") as f:
        json.dump({k: [t.dict() for t in v] for k, v in all_tokens.items()}, f, ensure_ascii=False, indent=4)

    log.info("Succesfully collected trusted tokens")
    return trusted


if __name__ == "__main__":
    asyncio.run(collect_trusted_tokens())
