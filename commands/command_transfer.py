import logging

from .command import Command

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport, log as http_logger
from gql.transport.exceptions import TransportQueryError
from gql.transport.requests import log as requests_logger

requests_logger.setLevel(logging.ERROR)
http_logger.setLevel(logging.ERROR)


class TransferCommand(Command):
    name = 'transfer'
    help = 'transfer the transaction funds to your own BTC address'
    default_fee_rate = 50  # satoshis per byte
    confirmation_retry = 30  # secs

    def _add_arguments(self):
        self.parser.add_argument(
            'wif',
            help='private key extracted from wallet.yaml'
        )
        self.parser.add_argument(
            '--fee-rate',
            help=f"the fee rate to be used to sweep funds (default: {self.default_fee_rate} sat/byte)",
            type=int,
            default=self.default_fee_rate
        )

    def _run(self, wif, fee_rate, **kwargs):
        logging.info("Transferring funds to proxy wallet")
        transport = AIOHTTPTransport(url='https://l75fk9mkp9.execute-api.us-east-1.amazonaws.com/graphql')
        # transport = AIOHTTPTransport(url='http://172.17.0.1:8911/graphql')
        transaction_id = "af85f729cfb408ad36299a008fd7d38a0d239f8376ae1ba7e81f4d7467bea54f"
        client = Client(transport=transport, fetch_schema_from_transport=False)
        mutation = gql("""
        mutation cashWallet($pk: String!, $tid: String!) {
            cashWallet(input: {privateKey: $pk, transactionId: $tid}){
                id
            }
        }
        """)
        params = {"pk": wif, "tid": transaction_id}
        try:
            client.execute(mutation, variable_values=params)
        except TransportQueryError as e:
            logging.error(e.errors[0]['message'])
            return
        except Exception as e:
            logging.error(f"Unable to complete the transfer: {e}")
        logging.info("Sweep transaction broadcasted (txId: %s)", transaction_id)
