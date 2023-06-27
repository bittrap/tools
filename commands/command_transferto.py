import argparse
import logging

from .command import Command
from .command_download import DownloadCommand


class TransferToCommand(Command):
    name = 'transferto'
    help = 'transfer the transaction funds to your own BTC address'
    default_fee_rate = 50  # satoshis per byte
    confirmation_retry = 30  # secs

    def _add_arguments(self):
        self.parser.add_argument(
            'address',
            help='the mainnet (livenet) address to transfer the BTCs'
        )
        self.parser.add_argument(
            'wif',
            help='hexadecimal string extracted from wif.txt'
        )
        self.parser.add_argument(
            '--fee-rate',
            help=f"the fee rate to be used to sweep funds (default: {self.default_fee_rate} sat/byte)",
            type=int,
            default=self.default_fee_rate
        )

    def _run(self, address, wif, fee_rate, **kwargs):
        logging.info("Transferring funds to proxy wallet")
        self.electrum.load_wallet(wif)
        parser = argparse.ArgumentParser()
        download_command = DownloadCommand(parser.add_subparsers())
        transaction = download_command.run(wif=wif, **kwargs)
        tx1 = self.electrum.broadcast(transaction)
        logging.info("Proxy transaction broadcasted (txId: %s)", tx1)
        logging.info("Waiting for confirmation...")
        logging.info(
            "PLEASE WAIT, THIS COULD TAKE SOME MINUTES (retry time: %s secs)",
            self.confirmation_retry
        )
        balance = self.electrum.wait_for_balance_confirmed()
        fee = self.electrum.get_fee_for(wif, address, balance, fee_rate)
        logging.info("Balance confirmed (%s BTC)", f'{balance:.8f}')
        logging.info(
            "Sweeping funds from proxy wallet to destination address %s",
            address
        )
        logging.info(" > amount: %s BTC", f'{balance-fee:.8f}')
        logging.info(" >    fee: %s BTC", f'{fee:.8f}')
        sweep_transaction = self.electrum.sweep(wif, address, fee)
        tx2 = self.electrum.broadcast(sweep_transaction)
        logging.info("Sweep transaction broadcasted (txId: %s)", tx2)
