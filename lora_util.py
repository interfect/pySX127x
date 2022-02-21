#!/usr/bin/env python2.7

""" This is a utility script for the SX127x (LoRa mode). It dumps and loads register values. """

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
from spi_lora.constants import REG, MODE
from spi_lora.boards.Generic_RFM95W import BOARD
import argparse
import re
import sys

BOARD.setup()
try:

    parser = argparse.ArgumentParser(description='LoRa utility functions')
    parser.add_argument('--dump', '-d', dest='dump', default=False, action="store_true", help="dump all registers")
    parser.add_argument('--load', '-l', dest='load', default=None, type=argparse.FileType('r'), help="load and apply register dump file")
    args = parser.parse_args()

    lora = LoRa(BOARD, verbose=False, do_calibration=False)

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
        
    elif args.load:
        sys.stderr.write("Applying register dump file\n")
        # Some registers aren't allowed to be set unless the device is in the right
        # mode. We don't really enforce that, but we do refuse to set anything
        # before op mode is set.
        op_mode_set = False
        
        # We want to store all the things we applied so we can check them.
        applied_values = {}
        
        for line in args.load:
            # Parse out the register number and the hex value
            parsed = re.match('([0-9A-F][0-9A-F]) +[0-9A-Z_]+ ([0-9A-F][0-9A-F]) [0-1]+', line)
            if parsed:
                # This is a line that means something
                reg_number = int(parsed.group(1), 16)
                reg_value = int(parsed.group(2), 16)
            
                if reg_number == REG.LORA.OP_MODE:
                    if reg_value not in MODE.lookup:
                        sys.stderr.write("Refusing to set unrecognized operating mode %02X\n" % reg_value)
                        sys.exit(1)
                    op_mode_set = True
                elif not op_mode_set:
                    sys.stderr.write("Refusing to set register %02X before OP_MODE\n" % reg_number)
                    sys.exit(1)
                
                sys.stderr.write("Setting %02X to %02X\n" % (reg_number, reg_value))
                lora.set_register(reg_number, reg_value)
                applied_values[reg_number] = reg_value
        
        sys.stderr.write("Verifying register values\n")
        
        for reg_number, stored in applied_values.items():
            got = lora.get_register(reg_number)
            if stored != got:
                sys.stderr.write("Failed to apply register %02X: stored %02X but got %02X\n" % (reg_number, stored, got))
                sys.exit(1)

        sys.stderr.write("Applied register dump file successfully\n")

    else:
        print(lora)

finally:
    BOARD.teardown()
