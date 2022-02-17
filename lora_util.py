#!/usr/bin/env python2.7

""" This is a utility script for the SX127x (LoRa mode). It dumps all registers. """

# Copyright 2015 Mayer Analytics Ltd.
#
# This file is part of spi-lora.
#
# spi-lora is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# spi-lora is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You can be released from the requirements of the license by obtaining a commercial license. Such a license is
# mandatory as soon as you develop commercial activities involving spi-lora without disclosing the source code of your
# own applications, or shipping spi-lora with a closed source product.
#
# You should have received a copy of the GNU General Public License aling with spi-lora.  If not, see
# <http://www.gnu.org/licenses/>.


from spi_lora.LoRa import LoRa
from spi_lora.boards.Generic_RFM95W import BOARD
import argparse

BOARD.setup()

parser = argparse.ArgumentParser(description='LoRa utility functions')
parser.add_argument('--dump', '-d', dest='dump', default=False, action="store_true", help="dump all registers")
args = parser.parse_args()

lora = LoRa(BOARD, verbose=False)

if args.dump:

    print("LoRa register dump:\n")
    print("%02s %18s %2s %8s" % ('i', 'reg_name', 'v', 'v'))
    print("-- ------------------ -- --------")
    for reg_i, reg_name, val in lora.dump_registers():
        if val is not None:
            print("%02X %18s %02X %s" % (reg_i, reg_name, val, format(val, '#010b')[2:]))
        else:
            print("%02X %18s XX XXXXXXXX" % (reg_i, reg_name))
    print("")

else:
    print(lora)

BOARD.teardown()
