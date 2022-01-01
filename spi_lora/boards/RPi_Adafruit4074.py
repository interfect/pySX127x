""" Defines the board pin mappings and RF module HF/LF info for an Adafruit
4074 "Adafruit LoRa Radio Bonnet with OLED - RFM95W @ 915MHz - RadioFruit"
<https://www.adafruit.com/product/4074> connected to a Raspberry Pi.
"""
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
# You should have received a copy of the GNU General Public License along with spi-lora.  If not, see
# <http://www.gnu.org/licenses/>.


# Importing this board config requires the RPi module to be installed.
import RPi.GPIO as GPIO
import spidev

import time

from . import BaseBoard


class BOARD(BaseBoard):
    """ This is the Adafruit LoRa Radio Bonnet.
    """
    # Note that the BCOM numbering for the GPIOs is used.
    DIO0 = 22   # RaspPi GPIO 22
    DIO1 = 23   # RaspPi GPIO 23
    DIO2 = 24   # RaspPi GPIO 24
    RESET = 25

    # The spi object is kept here
    spi = None

    @classmethod
    def setup(cls):
        """ Configure the Raspberry GPIOs
        :rtype : None
        """
        GPIO.setmode(GPIO.BCM)

        for gpio_pin in [BOARD.DIO0, BOARD.DIO1, BOARD.DIO2]:
            GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # blink 2 times to signal the board is set up
        BOARD.blink(.1, 2)

    @classmethod
    def teardown(cls):
        """ Cleanup GPIO and SpiDev """
        GPIO.cleanup()
        BOARD.spi.close()

    @classmethod
    def SpiDev(cls, spi_bus=0, spi_cs=1):
        """ Init and return the SpiDev object.
        
        On this board, the modem is on SPI bus 0 as chip 1, by default.
        
        :return: SpiDev object
        :param spi_bus: The RPi SPI bus to use: 0 or 1
        :param spi_cs: The RPi SPI chip select to use: 0 or 1
        :rtype: SpiDev
        # """
        #         self,
        # spi,
        # cs,
        # reset,
        # frequency,
        # *,
        # preamble_length=8,
        # high_power=True,
        baudrate=5000000
        #         self._device = spidev.SPIDevice(spi, cs, baudrate=baudrate, polarity=0, phase=0)
        BOARD.spi = spidev.SpiDev()
        BOARD.spi.open(spi_bus, spi_cs)
        BOARD.spi.max_speed_hz = baudrate
        return BOARD.spi

    @classmethod
    def add_event_detect(cls, dio_number, callback):
        """ Wraps around the GPIO.add_event_detect function
        :param dio_number: DIO pin 0...5
        :param callback: The function to call when the DIO triggers an IRQ.
        :return: None
        """
        GPIO.add_event_detect(dio_number, GPIO.RISING, callback=callback)

    @classmethod
    def add_events(cls, cb_dio0, cb_dio1, cb_dio2, cb_dio3, cb_dio4, cb_dio5, switch_cb=None):
        BOARD.add_event_detect(BOARD.DIO0, callback=cb_dio0)
        BOARD.add_event_detect(BOARD.DIO1, callback=cb_dio1)
        BOARD.add_event_detect(BOARD.DIO2, callback=cb_dio2)
        # BOARD.add_event_detect(BOARD.DIO3, callback=cb_dio3)
        # the modtronix inAir9B does not expose DIO4 and DIO5
        if switch_cb is not None:
            GPIO.add_event_detect(BOARD.SWITCH, GPIO.RISING, callback=switch_cb, bouncetime=300)

