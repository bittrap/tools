import glob
import json
import logging
import time
import re
import subprocess
from datetime import datetime
from pathlib import Path

import base58

working_dir = Path(__file__).resolve().absolute().parent


class Electrum:
    """
    Helper class for handling the Electrum CLI.
    """

    confirmation_retry = 30  # secs
    confirmation_sleep = 3  # secs

    def __init__(self, flags=None):
        self.flags = flags or ''
        self.wallet_name = f'proxy.wallet.{self._timestamp()}'
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
            error = e.stderr
            if not error:
                error = e.stdout
            raise RuntimeError(f"[Electrum] {error.decode('utf-8')}")

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
        time.sleep(self.confirmation_sleep)
        while True:
            response = self._run(f'getbalance -w {self.wallet_name}')
            balance = json.loads(response.stdout)
            logging.info(balance)
            if float(balance.get('confirmed', 0)) > 0:
                return float(balance['confirmed'])
            time.sleep(self.confirmation_retry)

    def sweep(self, wif, address, fee):
        response = self._run(f'sweep {wif} {address} --fee {fee}')
        return response.stdout.strip().decode('utf-8')

    def list_addresses(self):
        response = self._run(f'listaddresses -w {self.wallet_name}')
        return json.loads(response.stdout)

    @staticmethod
    def decode_private_key(wif):
        private_key = base58.b58decode(wif)
        # Remove checksum bytes and header.
        private_key = private_key.hex()[:-10][2:]
        return private_key
    
    @staticmethod
    def _timestamp():
        dt = datetime.now()
        ts = datetime.timestamp(dt)
        return ts


#
# Base class for all commands.
# All commands must inherit from this one.
#
class Command:
    name = 'command'
    help = 'Define me in a subclass'

    def __init__(self, parser_root):
        self.electrum = None
        self.cwd = working_dir
        self.parser = parser_root.add_parser(self.name, help=self.help)
        self.parser.set_defaults(func=self.run)
        self._add_arguments()

    def _add_arguments(self):
        pass  # Define in subclasses.

    def _run(self, **kwargs):
        pass  # Define in subclasses.

    def run(self, **kwargs):
        logging.info("Running command %s...", self.name)
        self.electrum = Electrum(
            flags='--testnet' if kwargs.get('testnet') else ''
        )
        result = self._run(**kwargs)
        return result

    @staticmethod
    def all_commands():
        regex = re.compile('.*command_(?P<command>.+).py')
        paths = glob.glob(str(working_dir.joinpath('command_*.py')))
        commands = [regex.match(path).group('command') for path in paths]
        commands.sort()
        return commands
