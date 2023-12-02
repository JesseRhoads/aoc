#!/bin/env python3
# Advent of Code 2023, Day 1
# Jesse Rhoads

import argparse
import logging
import os
import signal
import re
import sys
from collections import defaultdict

# Simple 'what are we' to use for later
prog_name = "aoc-1"
prog_description = "Does something"

# Set up Logging to stderr/stdout
log = logging.getLogger()


class IsCorrect(Exception):
    pass


class NotCorrect(Exception):
    pass


# Lookup table for converting number words to digits
digit_map = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
}


class ElfTrack:
    # We use this function when the thing we want to process is only one line at a time.
    # For cases where the data spans multiple lines, we don't do this, we use a generator further down.
    def parse_input(self):
        line_counter = 0
        data = []
        with open(self.args.my_file) as input:
            for unsanitized_line in input:
                line = unsanitized_line.strip()
                line_counter += 1
                if line == "":
                    continue
                else:
                    data.append(line)
        return data

    # Simple find the numbers, get first and last
    def parse_data_method_one(self, data):
        rex = "(\d)"
        total = 0
        for line in data:
            matches = re.findall(rex, line)
            log.debug(f"Matches: {matches}")
            result = f"{matches[0]}{matches[-1]}"
            log.debug(f"result {result}")
            results = int(result)
            total += results
        log.info(total)

    # Now we have to find number strings as well.
    # After getting the data and failing a few times, discovered that some words were portmanteaud together, so we handle them ad-hoc
    def parse_data_method_two(self, data):
        rex = "(nineight|threeight|eightwo|oneight|twone|one|two|three|four|five|six|seven|eight|nine|\d)"
        total = 0
        for line in data:
            matches = re.findall(rex, line)
            sane_matches = []
            for match in matches:
                if match == "twone":
                    sane_matches.append(2)
                    sane_matches.append(1)
                elif match == "oneight":
                    sane_matches.append(1)
                    sane_matches.append(8)
                elif match == "eightwo":
                    sane_matches.append(8)
                    sane_matches.append(2)
                elif match == "threeight":
                    sane_matches.append(3)
                    sane_matches.append(8)
                elif match == "nineight":
                    sane_matches.append(9)
                    sane_matches.append(8)
                else:
                    sane_matches.append(match)
            log.debug(f":: {line} Matches: {sane_matches}")
            result = f"{sane_matches[0]}{sane_matches[-1]}"
            first = sane_matches[0]
            last = sane_matches[-1]
            if first in digit_map:
                first_digit = str(digit_map[first])
            else:
                first_digit = str(first)
            if last in digit_map:
                last_digit = str(digit_map[last])
            else:
                last_digit = str(last)
            result = int("".join([first_digit, last_digit]))
            log.debug(f"result {result}")
            total += result
            log.debug(result)
        log.info(total)

    def __init__(self, args):
        # Take the command line args and store them as an instance variable for quick access.
        self.args = args


# Let's Get our command line parameters
def get_parameters():
    parser = argparse.ArgumentParser(description=prog_description)
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        default=False,
        help="Enable Debug Logging",
        action="store_true",
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="my_file",
        help="File to load",
        required=True,
    )

    return parser.parse_args()


def main():
    cli_args = get_parameters()

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    log.addHandler(stdout_handler)

    if cli_args.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    log.debug(f"{prog_name} Starting up. Arguments: {cli_args}")
    # Set up a managment object to handle scope more readily.
    elf_tracker = ElfTrack(cli_args)
    # Initialize whatever else here.
    data = elf_tracker.parse_input()

    elf_tracker.parse_data_method_one(data)
    elf_tracker.parse_data_method_two(data)


if __name__ == "__main__":
    main()
