import glob
import json
import os


_template = """
# Multi-chain token list standard. 

## TLDR

In this repo you may find tokenlists aggregated from various trusted providers, such as sushiswap or 1inch. We only list a token
if it appeared in 2 or more different tokenlists. So we believe that if 2 or more providers list a token, than it is
most likely not a scam.

## Usage example
If you want to use tokenlist in your dApp — simply download json with needed chain tokens. Head for raw link like 

https://raw.githubusercontent.com/viaprotocol/tokenlists/main/tokenlists/ethereum.json (Ethereum tokenlist)

or 

https://raw.githubusercontent.com/viaprotocol/tokenlists/main/tokenlists/bsc.json (Binance Smart Chain Tokenlist)

## Providers

We collect tokenlists from github repos or open APIs from various platforms, currently:
- [CoinGecko](https://www.coingecko.com/)
- [1inch](https://app.1inch.io/)
- [Uniswap](https://uniswap.org/)
- [Sushiswap](https://www.sushi.com/)
- [OpenOcean](https://openocean.finance/)
- [SolanaLabs](https://solanalabs.com/)
- [ElkFinance](https://elk.finance/)
- [OneSol](https://1sol.io/)
- [QuickSwap](https://quickswap.exchange/#/swap)
- [FuseSwap](https://beta.fuseswap.com/#/swap)
- [TrisolarisLabs](https://www.trisolaris.io/#/swap)
- [Rubic](https://app.rubic.exchange/)

Feel free to add new provider if you think it is trusted and if it has opensource tokenlists, on github 
or in API.

## Chains with trusted tokens

Here are chains presented in our tokenlists with current token count. You can find out more in `/tokenlists` folder.
Token counts are approximate and may vary as providers update their tokenlists.

{tokens_count_by_chain}

Testnets:

- Rinkeby
- Ropsten
- Goerli
- Mumbai
- etc.

## How are tokenlists formed

We collect many tokenlists from many providers, then we aggregate them by chains and tokens addresses. 
For each token we check whether it is listed in 2 or more tokenlists from different providers. If so, 
we add it to our trusted tokenlist.


## Run aggregation script yourself
Install requirements
```$ pip3 install -r requirements.txt```
Run the script from repo root folder
```python3 aggregate_tokens.py```

## Generate readme.md based on aggregated data
```bash
python generate_readme.py
```


## Contribute
Feel free to open issues and PRs with tokens, chains or providers that you want to add.

Developed by [Via.Exchange](https://Via.Exchange) team
"""


def _count_tokens(json_file_name: str, file) -> dict[str, int]:
    name_without_json = json_file_name.split('.')[0].lower()
    if name_without_json == "all":
        return {}

    tokens = json.loads(file.read())
    return {name_without_json.capitalize(): len(tokens)}


MIN_TOKEN_COUNT_TO_INCLUDE_IN_DOCS = 5


def generate_readme() -> None:
    _counts: dict[str, int] = {}
    for filename in glob.glob('tokenlists/*.json'):
        with open(os.path.join(os.getcwd(), filename), 'r') as f:  # open in readonly mode
            json_file_name = filename.split('/')[-1]
            _counts |= _count_tokens(json_file_name, f)

    _token_count_by_chain_name = {
        chain_name: tokens_count for chain_name, tokens_count in sorted(
            _counts.items(), key=lambda item: -item[1]
        )
        if tokens_count >= MIN_TOKEN_COUNT_TO_INCLUDE_IN_DOCS
    }
    token_count_by_chain_name = [
        f"- {chain_name}, {count} tokens" for chain_name, count in _token_count_by_chain_name.items()
    ]

    text = _template.format(tokens_count_by_chain='\n'.join(token_count_by_chain_name))
    with open("README.md", "w") as readme_file:
        readme_file.write(text)


if __name__ == "__main__":
    generate_readme()
