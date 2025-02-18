#! /usr/bin/env python
import argparse
import os
from distutils.util import strtobool

from canarytokens.queries import (
    block_domain,
    block_email,
    is_email_blocked,
    unblock_domain,
    unblock_email,
)
from canarytokens.redismanager import DB

parser = argparse.ArgumentParser(
    description="Block emails or domains from creating canarytokens"
)
parser.add_argument(
    "users",
    metavar="user",
    type=str,
    nargs="+",
    help="an email address or domain to block",
)
parser.add_argument(
    "-u",
    "--unblock",
    dest="mode",
    action="store_const",
    const="unblock",
    default="block",
    help="unblock instead",
)
args = parser.parse_args()

redis_hostname = "localhost" if strtobool(os.getenv("CI", "False")) else "redis"
DB.set_db_details(hostname=redis_hostname, port=6379)

funcs = {
    "block": {"domain": block_domain, "email": block_email},
    "unblock": {"domain": unblock_domain, "email": unblock_email},
}

for user in args.users:
    if "@" in user:
        kind, test_target = "email", user
    else:
        kind, test_target = "domain", "anything@" + user
    block_func = funcs[args.mode][kind]
    try:
        print('\n[*] {}ing {}: "{}"'.format(args.mode, kind, user))
        block_func(user)
        print('[>]     checking if "{}" is blocked'.format(test_target))
        assert (
            is_email_blocked(test_target)
            if args.mode == "block"
            else not is_email_blocked(test_target)
        )
        print('[o]     successfully {}ed "{}"'.format(args.mode, test_target))
    except Exception:
        print('[x]     failed to {} "{}"'.format(args.mode, test_target))

print("\n[;] done blocking")
