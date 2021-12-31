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

import time

class BaseBoard(object):
    """
    Base borad class which user-defined boards or pre-defined boards will
    implement.
    
    Responsible for producing an spidev SPI connection to the modem and hooking
    up interrupt handlers on the modem's DIO lines, if connected.
    
    Is not instantiated; methods are static.
    """
    
    # Set this field to True if the modem on this board is a low-band modem, and Flase otherwise.
    # low band (called band 1&2) are 137-175 MHz and 410-525 MHz
    # high band (called band 3) is 862-1020 MHz
    low_band = True
    
    @classmethod
    def setup(cls):
        """ Configure the board's GPIO connections, if necessary.
        :rtype : None
        """
        # Boards may not have this optional feature, so do nothing by default.
        pass

    @classmethod
    def teardown(cls):
        """ Clean up GPIO and SPI devices, if necessary. """
        # Boards may not have this optional feature, so do nothing by default.
        pass

    @classmethod
    def SpiDev(cls, spi_bus=None, spi_cs=None):
        """ Init and return the SpiDev object used to talk to the modem.
        Responsible for setting a reasonable SPI speed.
        :return: SpiDev object
        :param spi_bus: The SPI bus to use, if the board has several. Some boards may only allow using one at a time.
        :param spi_cs: The SPI chip select to use, if the board has several. Some boards may only allow using one at a time.
        :rtype: spidev.SpiDev
        """
        raise NotImplementedError()

    # If the board supports interrupt lines, it should add an add_events class
    # method. This method must take 5 DIO callbacks and one optional switch_cb
    # callback. It will call the given callbacks when the modem DIO pins are
    # triggered. If switch_cb is set and the board has a switch, call it when
    # the switch is activated.

    @classmethod
    def led_on(cls, value=1):
        """ If the board has an LED, swithc it on (or off). Returns the
        argument passed.
        :param value: 0/1 for off/on. Default is 1.
        :return: value
        :rtype : int
        """
        # Boards may not have this optional feature, so pass through the argument by default.
        return value
        

    @classmethod
    def led_off(cls):
        """ Switch LED off
        :return: 0
        """
        return cls.led_on(0)

    @classmethod
    def blink(cls, time_sec, n_blink):
        """
        Blink the board's LED, if present.
        """
        if n_blink == 0:
            return
        cls.led_on()
        for i in range(n_blink):
            time.sleep(time_sec)
            cls.led_off()
            time.sleep(time_sec)
            cls.led_on()
        cls.led_off()
