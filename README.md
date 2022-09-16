# BitTrap transfer tool

This tool will help you to transfer the funds of a BitTrap wallet to 
your own wallet.

## How BitTrap works?

* BitTrap installs a Bitcoin signed transaction with a bounty in every device of an organization.
* This transaction (when it's broadcast in the Bitcoin network) will transfer the bounty to a "proxy wallet".
* If you hack a device where BitTrap is installed, you'll find 2 files:
  1. `transaction.txt`: The signed Bitcoin transaction with a risk-adjusted amount of BTC (the device bounty).
  2. `wif.txt`: The encoded private key of the proxy wallet.
* You will be able to collect funds by following these steps:
  1. Broadcast `transaction.txt` in the Bitcoin network to send fund to the proxy wallet.
  2. Broadcast a new transaction to send the proxy wallet funds to a Bitcoin address that belongs to you. 
     You'll need the private key provided in `wif.txt` to do this. 
* **The scripts provided here will help you to transfer all funds in an easy way.**

## How this tool works?

Just run the Dockerized version of this tool with the proper parameters 
`docker run bittrap/tools <transaction> <wif> <address>`.

**Example (using testnet values)**

```
docker run bittrap/tools \ 
   020000000001019203bd6e43cd84 ... bc0bf27c5fe13ccf29cf400000000 \
   cRLEa65yZEHfXwkeYWMuhNYEM98sMKADBgH7SgdjM5ngdxHYyUwn \
   tb1qat7xdhvnp8zwyzp453u273v2qnfqe8yk5zlfer
```

## About BitTrap

BitTrap is a hard evidence-based intrusion detection system that provides 
immediate alarms without compromising endpoints’ performance, reducing the cost of 
an attack by granting hackers an economic incentive to reveal their position.

Unlike most cybersecurity solutions in the market, BitTrap does not focus on reducing 
intrusions, but actually on providing attackers a fair economic incentive to reveal 
their presence in the compromised system. 

### More Info

* https://bittrap.com
* https://twitter.com/bittrapsec
* https://www.linkedin.com/company/bittrap
