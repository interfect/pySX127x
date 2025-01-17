""" Defines the board pin mappings and RF module HF/LF info for a Modtronix
inAir9B connected to a Raspberry Pi, as follows:
| Proto board pin | RaspPi GPIO | Direction |
|:----------------|:-----------:|:---------:|
| inAir9B DIO0    | GPIO 22     |    IN     |
| inAir9B DIO1    | GPIO 23     |    IN     |
| inAir9B DIO2    | GPIO 24     |    IN     |
| inAir9B DIO3    | GPIO 25     |    IN     |
| inAir9b Reset   | GPIO ?      |    OUT    |
| LED             | GPIO 18     |    OUT    |
| Switch          | GPIO 4      |    IN     |
"""
# -*- coding: utf-8 -*-

# Copyright 2015-2018 Mayer Analytics Ltd.
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

# Importing this board config requires the RPi module to be installed.
import RPi.GPIO as GPIO
import spidev

from . import BaseBoard


class BOARD(BaseBoard):
    """ 
        This is the Raspberry Pi board with one LED and a modtronix inAir9B.
    """
    # Note that the BCOM numbering for the GPIOs is used.
    DIO0 = 22   # RaspPi GPIO 22
    DIO1 = 23   # RaspPi GPIO 23
    DIO2 = 24   # RaspPi GPIO 24
    DIO3 = 25   # RaspPi GPIO 25
    LED  = 18   # RaspPi GPIO 18 connects to the LED on the proto shield
    SWITCH = 4  # RaspPi GPIO 4 connects to a switch

    # The spi object is kept here
    spi = None
    
    # tell spi-lora here whether the attached RF module uses low-band (RF*_LF pins) or high-band (RF*_HF pins).
    # low band (called band 1&2) are 137-175 and 410-525
    # high band (called band 3) is 862-1020
    low_band = True

    @classmethod
    def setup(cls):
        """ Configure the Raspberry GPIOs
        :rtype : None
        """
        GPIO.setmode(GPIO.BCM)
        # LED
        GPIO.setup(cls.LED, GPIO.OUT)
        GPIO.output(cls.LED, 0)
        # switch
        GPIO.setup(cls.SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
        # DIOx
        for gpio_pin in [cls.DIO0, cls.DIO1, cls.DIO2, cls.DIO3]:
            GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # blink 2 times to signal the board is set up
        cls.blink(.1, 2)

    @classmethod
    def teardown(cls):
        """ Cleanup GPIO and SpiDev """
        GPIO.cleanup()
        cls.spi.close()

    @classmethod
    def SpiDev(cls, spi_bus=0, spi_cs=0):
        """ Init and return the SpiDev object
        :return: SpiDev object
        :param spi_bus: The RPi SPI bus to use: 0 or 1
        :param spi_cs: The RPi SPI chip select to use: 0 or 1
        :rtype: SpiDev
        """
        cls.spi = spidev.SpiDev()
        cls.spi.open(spi_bus, spi_cs)
        cls.spi.max_speed_hz = 5000000    # SX127x can go up to 10MHz, pick half that to be safe
        return cls.spi

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
        cls.add_event_detect(cls.DIO0, callback=cb_dio0)
        cls.add_event_detect(cls.DIO1, callback=cb_dio1)
        cls.add_event_detect(cls.DIO2, callback=cb_dio2)
        cls.add_event_detect(cls.DIO3, callback=cb_dio3)
        # the modtronix inAir9B does not expose DIO4 and DIO5
        if switch_cb is not None:
            GPIO.add_event_detect(cls.SWITCH, GPIO.RISING, callback=switch_cb, bouncetime=300)

    @classmethod
    def led_on(cls, value=1):
        """ Switch the proto shields LED
        :param value: 0/1 for off/on. Default is 1.
        :return: value
        :rtype : int
        """
        GPIO.output(cls.LED, value)
        return value

