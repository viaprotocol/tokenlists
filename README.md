# Multi-chain token list standard. 

## TLDR

In this repo you may find tokenlists aggregated from various trusted providers, such as sushiswap or 1inch. We only list a token
if it appeared in 2 or more different tokenlists. So we believe that if 2 or more providers list a token, than it is
most likely not a scam.

## Providers

We collect tokenlists from github repos or open APIs from various platforms, currently:
- CoinGecko
- 1inch
- Uniswap
- Sushiswap
- OpenOcean
- SolanaLabs
- ElkFinance
- OneSol
- QuickSwap
- FuseSwap

Feel free to add new provider if you think it is trusted and if it has opensource tokenlists, on github 
or in API.

## Chains with trusted tokens

Here are chains presented in our tokenlists with current token count. You can find out more in `/tokenlists` folder.
Token counts are approximate and may vary as providers update their tokenlists.
- Ethereum, 1131 tokens
- Solana, 697 tokens
- Bsc, 526 tokens
- Polygon, 330 tokens
- Heco, 197 tokens
- Avax, 123 tokens
- Ftm, 85 tokens
- Farms, 72 tokens
- Xdai, 58 tokens
- Harmony, 40 tokens
- Okex, 32 tokens
- Moonriver, 26 tokens
- Fuse, 16 tokens
- Optimistic-ethereum, 15 tokens
- Celo, 12 tokens
- Cronos, 10 tokens
- Telos, 10 tokens
- Boba, 7 tokens
- Hoo, 2 tokens
- Fuji, 1 tokens


Testnets:

- Rinkeby
- Ropsten
- Goerli
- Mumbai
- etc.

## How are tokenlists formed

We collect many tokenlists from many providers, than we aggregate them by chains and tokens addresses. 
For each token we check whether it is listed in 2 or more tokenlists from different providers. If so, 
we add it to our trusted tokenlist.


## Run aggregation script yourself
Install requirements
```$ pip3 install -r requirements.txt```
Run the script from repo root folder
```python3 aggregate_tokens.py```


## Contribute
Feel free to open issues and PRs with tokens, chains or providers that you want to add.

Developed by [Via.Exchange](https://Via.Exchange) team
