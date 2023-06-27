# python3
import argparse
import logging
import os

from commands import *


PROGRAM_NAME = 'bittrap/tools'
VERSION = '2.1.0'

os.environ["PATH"] += os.pathsep + '/root/.local/bin'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname).4s | %(message)s'
)


def main():
    logging.info(f"BitTrap tools v{VERSION}")
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME)
    parser.add_argument(
        '--testnet',
        help='use testnet network (for debugging purposes only)',
        action='store_true'
    )
    sub_parsers = parser.add_subparsers()
    commands = [
        DownloadCommand,
        TransferToCommand,
    ]
    for command in commands:
        command(sub_parsers)
    args = parser.parse_args()
    assert 'func' in args, RuntimeError(
        f"Please, specify a command to run: {Command.all_commands()} "
        f"or type --help for more information."
    )
    args.func(**vars(args))
    logging.info('DONE')


if __name__ == '__main__':
    try:
        main()
    except SystemExit as e:
        exit(e.code)
    except BaseException as e:
        logging.error(e)
        exit(1)
