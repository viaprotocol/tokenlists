
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

- Ethereum, 1818 tokens
- Bsc, 1354 tokens
- Solana, 925 tokens
- Polygon, 780 tokens
- Avax, 362 tokens
- Ftm, 332 tokens
- Gnosis, 307 tokens
- Heco, 197 tokens
- Arbitrum, 173 tokens
- Harmony, 89 tokens
- Aurora, 85 tokens
- Cronos, 66 tokens
- Celo, 65 tokens
- Moonriver, 63 tokens
- Okex, 47 tokens
- Optimism, 45 tokens
- Moonbeam, 31 tokens
- Fuse, 18 tokens
- Astar, 15 tokens
- Boba, 12 tokens
- Telos, 10 tokens
- Kcc, 9 tokens
- Evmos, 7 tokens
- Cube, 7 tokens

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
