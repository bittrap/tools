#!/usr/bin/env python3.9
import argparse
import json
import logging
import os
import subprocess
import time

from pathlib import Path


DEFAULT_FEE_RATE = 70  # sat/byte
CONFIRMATION_RETRY = 30  # secs
os.environ["PATH"] += os.pathsep + '/root/.local/bin'
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname).4s | %(message)s')


class Electrum:
    """
    Helper class for handling the Electrum CLI.
    """

    def __init__(self, flags=None):
        self.flags = flags or ''
        self.wallet_name = 'proxy.wallet'
        self._run('daemon -d')

    def _run(self, command):
        try:
            return subprocess.run(
                f'electrum {self.flags} {command}',
                capture_output=True,
                check=True,
                shell=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Electrum error: {e.stderr.decode('utf-8')}")

    def get_fee_for(self, wif, address, balance, fee_rate):
        # Call sweep just to get the transaction length in bytes.
        # (The transaction will NOT be broadcasted over the Bitcoin network.)
        response = self._run(f'sweep {wif} {address}')
        tx_bytes = len(response.stdout) / 2
        fee_in_satoshis = tx_bytes * fee_rate
        fee = fee_in_satoshis / 100000000
        if fee > balance:
            fee = max(balance/8, 0.00000001)
        return fee

    def load_wallet(self, wif):
        Path(self.wallet_name).unlink(missing_ok=True)
        self._run(f'restore {wif} -w {self.wallet_name}')
        self._run(f'load_wallet -w {self.wallet_name}')

    def broadcast(self, transaction):
        response = self._run(f'broadcast {transaction}')
        return response.stdout.strip().decode('utf-8')

    def wait_for_balance_confirmed(self):
        time.sleep(3)
        while True:
            response = self._run(f'getbalance -w {self.wallet_name}')
            balance = json.loads(response.stdout)
            logging.info(balance)
            if float(balance.get('confirmed', 0)) > 0:
                return float(balance['confirmed'])
            time.sleep(CONFIRMATION_RETRY)

    def sweep(self, wif, address, fee):
        response = self._run(f'sweep {wif} {address} --fee {fee}')
        return response.stdout.strip().decode('utf-8')


def main():
    # Define the command line arguments.
    parser = argparse.ArgumentParser(description='BitTrap transfer tool.')
    parser.add_argument(
        'transaction',
        help='Hexadecimal string extracted from transaction.txt.'
    )
    parser.add_argument(
        'wif',
        help='Hexadecimal string extracted from wif.txt.'
    )
    parser.add_argument(
        'address',
        help='The mainnet (livenet) address to transfer the BTCs.'
    )
    parser.add_argument(
        '--fee-rate',
        help=f"Fee rate to be used to sweep funds (default: {DEFAULT_FEE_RATE} sat/byte).",
        default=DEFAULT_FEE_RATE
    )
    parser.add_argument(
        '--testnet',
        help='Use testnet network (for debugging purposes only).',
        action='store_true'
    )

    # Parse the command line.
    args = parser.parse_args()
    address = args.address
    transaction = args.transaction
    wif = args.wif
    fee_rate = float(args.fee_rate)
    flags = '--testnet' if args.testnet else ''

    # Broadcast the transaction to collect funds in a proxy wallet,
    # then sweep the proxy wallet transferring all BTC to the
    # destination address.
    electrum = Electrum(flags=flags)
    logging.info("Transferring funds to proxy wallet")
    electrum.load_wallet(wif)
    tx1 = electrum.broadcast(transaction)
    logging.info(f"Proxy transaction broadcasted (txId: {tx1})")
    logging.info("Waiting for confirmation...")
    logging.info(f"PLEASE WAIT, THIS COULD TAKE SOME MINUTES (retry time: {CONFIRMATION_RETRY} secs)")
    balance = electrum.wait_for_balance_confirmed()
    fee = electrum.get_fee_for(wif, address, balance, fee_rate)
    logging.info(f"Balance confirmed ({balance} BTC)")
    logging.info(f"Sweeping funds from proxy wallet to destination address {address}")
    logging.info(f" > amount: {balance-fee} BTC")
    logging.info(f" >    fee: {fee} BTC")
    sweep_transaction = electrum.sweep(wif, address, fee)
    tx2 = electrum.broadcast(sweep_transaction)
    logging.info(f"Sweep transaction broadcasted (txId: {tx2})")
    logging.info("DONE")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(e)
        exit(1)
