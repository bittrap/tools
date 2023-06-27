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

    def _download(self, address):
        urls = [
            f'{self.bucket_url}/v3/{address}',
            f'{self.bucket_url}/{address}'
        ]
        for url in urls:
            try:
                logging.info('Downloading transaction from %s', url)
                response = urllib.request.urlopen(url)
                return response.read()
            except:
                pass
        raise RuntimeError("Transaction not found or not generated yet, try again in few hours.")

    def _run(self, wif, **kwargs):
        self.electrum.load_wallet(wif)
        for address in self.electrum.list_addresses():
            data = self._download(address)
            encrypted = data.decode('utf-8')
            private_key = self.electrum.decode_private_key(wif)
            transaction = decrypt(
                private_key,
                bytes.fromhex(encrypted)
            ).decode('utf-8')
            logging.info("Downloaded transaction:\n\n%s\n", transaction)
            return transaction
