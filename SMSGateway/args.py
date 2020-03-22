import argparse
import sys

parser = argparse.ArgumentParser(description="SMS Gateway & Routing Toolkit. https://github.com/Jamesits/SMSGateway")
parser.add_argument('--config', type=str, default="", help='Path to the TOML formatted config file')


def parse_args():
    return parser.parse_args()


def print_help():
    return parser.print_help(file=sys.stderr)
