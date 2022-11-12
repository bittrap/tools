import logging
import urllib.request

from ecies import decrypt

from .command import Command


class DownloadCommand(Command):
    name = 'download'
    help = 'download last signed transaction'
    bucket_url = 'https://bittrap-public-bucket.s3.amazonaws.com'

    def _add_arguments(self):
        self.parser.add_argument(
            'wif',
            help='hexadecimal string extracted from wif.txt'
        )

    def _run(self, wif, **kwargs):
        self.electrum.load_wallet(wif)
        for address in self.electrum.list_addresses():
            url = f'{self.bucket_url}/{address}'
            logging.info('Downloading transaction from %s', url)
            response = urllib.request.urlopen(url)
            data = response.read()
            encrypted = data.decode('utf-8')
            private_key = self.electrum.decode_private_key(wif)
            transaction = decrypt(
                private_key, 
                bytes.fromhex(encrypted)
            ).decode('utf-8')
            logging.info("Downloaded transaction:\n\n%s\n", transaction)
            return transaction
