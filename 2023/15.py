#!/bin/env python3

import argparse
import logging
import os
import signal
import re
import sys
from collections import defaultdict

# Simple 'what are we' to use for later
prog_name = "aoc-15"
prog_description = "Does something"

# Set up Logging to stderr/stdout
log = logging.getLogger()


class IsCorrect(Exception):
    pass


class NotCorrect(Exception):
    pass


# I think part two needs a linked list object that can drop elements easily.
# That's easier than trying to shuffle a normal list.
class LinkedList(object):
    def __init__(self):
        self.head = None

    def add_to_front(self, node):
        self.refresh_nodes()
        log.debug(f"Nodes before add: {self.nodes}")
        old_head = self.head
        self.head = node
        if old_head is not None:
            node.next = old_head
            old_head.prev = node

    def add(self, node):
        self.refresh_nodes()
        if len(self.node_objects) > 1:
            tail = self.node_objects[-1]
            log.debug(f"In Add Node: Found tail {tail}")
            node.prev = tail
            tail.next = node
        elif len(self.node_objects) == 1:
            tail = self.node_objects[0]
            node.prev = tail
            tail.next = node
        else:
            self.head = node

    def remove(self, node):
        log.debug(f"Removing node {node}")
        if node is None:
            log.debug(f"Tried to remove null node {node}")
            return False
        if node.prev == None:
            log.debug(f"Removing head or detached node {node}")
            new_head = node.next
            self.head = new_head
            if new_head:
                new_head.prev = None
        elif node.next == None:
            log.debug("Remove Node: Next node not found")
            new_tail = node.prev
            new_tail.next = None
        else:
            log.debug("Removing node from the middle")
            new_middle = node.prev
            new_next = node.next
            new_middle.next = new_next
            new_next.prev = new_middle

    def refresh_nodes(self):
        node = self.head
        nodes = []
        node_objects = []
        while node is not None:
            nodes.append(str(node))
            node_objects.append(node)
            node = node.next
        nodes.append("None")
        self.nodes = nodes
        self.node_objects = node_objects

    def __repr__(self):
        self.refresh_nodes()
        return " -> ".join(self.nodes)

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node
            node = node.next


class Node:
    def __init__(self, tag, power):
        self.power = power
        self.next = None
        self.prev = None
        self.tag = tag

    def __repr__(self):
        return f"[{self.tag} {self.power}]"


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

    def parse_data_method_one(self, data):
        values = []
        coordinates = data[0].split(",")
        for coord in coordinates:
            result = self.hashify(coord)
            values.append(result)
        log.debug(values)
        log.info(f"Sum of hashes: {self.sum_of_values(values)}")

    def sum_of_values(self, values):
        sum = 0
        for value in values:
            sum += value
        return sum

    def parse_data_method_two(self, data):
        lenses = data[0].split(",")
        # There are 256 lens boxes numbered 0 through 255.
        # In each box we can have lenses added and removed but order must be preserved.
        # So to track these, each box needs a map of label to a linked list element (node)

        self.lens_box = defaultdict(LinkedList)
        self.lens_map = defaultdict(dict)
        for lens in lenses:
            result = self.lensify(lens)
            if result:
                log.debug(f"Lens {lens} result {result}")
            else:
                log.debug(f"Lens {lens} no results")
            log.debug(f"{self.lens_box} {self.lens_map}")
        focus_sum = self.focusify()
        log.info(f"Focus sum is {focus_sum}")

    def hashify(self, data):
        value = 0
        for letter in data:
            value += ord(letter)
            value = value * 17
            value = value % 256
            log.debug(f"{letter} value is {value}")
        return value

    # Take each lens identifier and break it down to an actionable
    def lensify(self, data):
        if "=" in data:
            lens_tag = data.partition("=")[0]
            lens_value = data.partition("=")[2]
            lens_hash = self.hashify(lens_tag)
            self.modify_lens(lens_hash, lens_tag, lens_value)
            return True
        elif "-" in data:
            lens_tag = data.partition("-")[0]
            lens_hash = self.hashify(lens_tag)
            self.remove_lens(lens_hash, lens_tag)
            return True
        else:
            log.debug("Lens found without = or -: {data}")
            return False

    def modify_lens(self, lens_hash, lens_tag, lens_value):
        lens_box = self.lens_box[lens_hash]
        lens_map = self.lens_map[lens_hash]
        if lens_tag in lens_map:
            lens = lens_map[lens_tag]
            log.debug(f"Updating lens {lens} to {lens_value}")
            lens.power = lens_value
        else:
            lens = Node(lens_tag, lens_value)
            log.debug(f"Created new lens {lens}")
            lens_box.add(lens)
            lens_map[lens_tag] = lens

    def remove_lens(self, lens_hash, lens_tag):
        lens_box = self.lens_box[lens_hash]
        lens_map = self.lens_map[lens_hash]
        log.debug(f"Lens Tag in Remove Lens: {lens_tag}")
        log.debug(f"Lens Box in Remove Lens: {lens_box}")
        log.debug(f"Lens map in Remove Lens: {lens_map}")
        if lens_tag in lens_map:
            lens = lens_map[lens_tag]
            lens_box.remove(lens)
            del lens_map[lens_tag]

    def focusify(self):
        # x = One plus the box number of the lens in question
        # y = The slot number of the lens within the box: 1 for the first lens, 2 for the second lens, etc
        # z = lens power
        # E(x*y*z)
        sum = 0
        for box_number in range(0, 256):
            box_sum = 0
            box = self.lens_box[box_number]
            if box is not None:
                lens_count = 1
                for lens in box:
                    log.debug(f"BOX {box_number} LENS {lens_count} IS {lens}")
                    lens_focus = (box_number + 1) * lens_count * int(lens.power)
                    box_sum += lens_focus
                    lens_count += 1
            sum += box_sum
        return sum

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
