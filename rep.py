#!/usr/bin/env python3

import sys
import argparse

import cart
from renderer import Renderer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cart_file', help='Cartridige file')
    args = parser.parse_args()
    cart_file = args.cart_file
    cartridge = cart.load_cart(cart_file)
    renderer = Renderer(cartridge)
    renderer.render()
    return 0


if __name__ == '__main__':
    sys.exit(main())
