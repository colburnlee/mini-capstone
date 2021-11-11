# Decentralized Finance (DeFi) Arbitrage Opportunities
## So What's Defi?
![DeFi TVL](/screenshots/DEFI_TVL.png)<br>*Image courtesy defillama.com*</br>

Defi's explosive growth has fueled the construction of many automated market makers (AMMs) that are fully autonomous trading mechanisms that have no centralized control over price making (aside from market force). [Here's an article](https://www.coindesk.com/learn/2021/08/20/what-is-an-automated-market-maker/#:~:text=An%20automated%20market%20maker%20%28AMM,how%20automated%20market%20makers%20work.) explaining how they function and why they are important to the growing landscape of DeFi.

## This Project
The API provided by the 0x protocol (more information [here](https://0x.org/docs/api)) is used to search for the best price available over multiple protocols (Ethereum, Polygon, Binance Smart Chain, and the Fantom Network) at a given time (0x searches 30+ AMMs alone on the Ethereum network) to find the maximum price difference to execute the same trade across each. This will help us determine price inefficiencies that persist between protocols, and shed light on how long it takes for significant price gaps to be closed by market forces and/or arbitrage traders.

![Graph](/screenshots/Combined_Arbs_.png)<br>*Data output example*</br>