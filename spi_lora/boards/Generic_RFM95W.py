""" Defines the board pin mappings and RF module HF/LF info for a HopeRF RFM95W
connected via Linux SPI, by default as bus 0 peripheral 0.
"""
# -*- coding: utf-8 -*-

# Copyright 2021 Adam Novak
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
# You should have received a copy of the GNU General Public License along with pySX127.  If not, see
# <http://www.gnu.org/licenses/>.

import spidev

from . import BaseBoard

class BOARD(BaseBoard):
    """ This is a generic SPI-only RFM95W board.
    """

    # RFM95W is 915 MHz band and so is not low band.
    low_band = False

    # We don't persist the SPI object ourselves, so we don't need setup or
    # teardown.
    
    @classmethod
    def SpiDev(cls, spi_bus=0, spi_cs=0):
        """ Init and return the SpiDev object
        :return: SpiDev object
        :param spi_bus: The SPI bus to use.
        :param spi_cs: The SPI chip select to use.
        :rtype: SpiDev
        """
        cls.spi = spidev.SpiDev()
        cls.spi.open(spi_bus, spi_cs)
        cls.spi.max_speed_hz = 5000000    # SX127x can go up to 10MHz, pick half that to be safe
        return cls.spi


