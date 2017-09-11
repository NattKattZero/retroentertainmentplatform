#!/usr/bin/env python3

import argparse
import functools
import sys
import os

def compile_cart(filepath):
    header = b''
    palette = b''
    tiles = b''
    tile_map = b''
    attr_map = b''
    map_map = b''
    with open(filepath, 'r') as cart_source:
        current_section = ''
        for line in cart_source:
            if line.startswith('-'):
                section = line[1:].strip()
                current_section = section
            elif line.startswith('#'):
                pass
            elif len(line.strip()) == 0:
                pass
            else:
                raw_bytes = convert_to_bytes(line.strip())
                if current_section == 'palette':
                    palette += raw_bytes
                elif current_section == 'tiles':
                    tiles += raw_bytes
                elif current_section == 'map':
                    tile_map += raw_bytes
                elif current_section == 'attr':
                    attr_map += raw_bytes
                elif current_section == 'mapmap':
                    map_map += raw_bytes
    # populating these feels really in-elegant, but I'm too stupid right now
    # to do it right
    header_values = [20]
    header_values.append(len(palette) + header_values[0])
    header_values.append(len(tiles) + header_values[1])
    header_values.append(len(tile_map) + header_values[2])
    header_values.append(len(attr_map) + header_values[3])
    header_bytes = [x.to_bytes(4, byteorder='big') for x in header_values]
    header = functools.reduce(lambda x,y: x + y, header_bytes)
    filename, _ = os.path.splitext(filepath)
    with open(filename + '.cart', 'wb') as output_cart:
        output_cart.write(header
            + palette
            + tiles
            + tile_map
            + attr_map
            + map_map)


def convert_to_bytes(line):
    int_values = [int(x, base=16) for x in line.split(' ')]
    byte_values = bytes(int_values)
    return byte_values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cart_file')
    args = parser.parse_args()
    compile_cart(args.cart_file)
    return 0


if __name__ == '__main__':
    sys.exit(main())
