# `spi-lora`: a Python package for using SPI-connected LoRa modems

This package, based on [`pySX127x`](https://github.com/mayeranalytics/pySX127x), provides a Python interface for working with LoRa modules such as the [HopeRF RFM95W](http://anarduino.com/docs/RFM95_96_97_98W.pdf), those based on the [Semtech SX1276/7/8/9](http://www.semtech.com/wireless-rf/rf-transceivers/) series of chips, or the Microchip [RN2483](http://ww1.microchip.com/downloads/en/DeviceDoc/50002346A.pdf).

This package intends to allow using these devices over a generic Linux SPI bus, from a Raspberry Pi or similar single-board computer, or from any linux system with a `/dev/spidev0.0` to attach the modem to. While it supports using the dedicated DIO interrupt request lines on the HopeRF RFM95W series modules, they do not need to be available.


# Hardware

To use this package, you usually want to use a board definition, inheriting from `spi_lora.boards.BaseBoard`. The module currently provides a couple of pre-defined boards:
* `spi_lora.boards.Generic_RFM95.BOARD`, for an RFM95 module attached via SPI only on SPI bus 0 device 0.
* `spi_lora.boards.RPi_inAir9B.BOARD`, for the inAir9B on a Raspberry Pi system that `pySX127x` is designed for. This can only be safely imported if `RPi.GPIO` is available.

If you aren't using one of these hardware configurations, you can define your own board definition by extending `spi_lora.boards.BaseBoard`.

If you do not want to use a board definition, you can use the `spi_lora.LoRa.GenericLoRa` class, which requires only an SPI connection and a low/high band flag, but you will need to manage creating and setting the data rate on the SPI connection yourself.

If your board does not support dedicated interrupt event lines (and `irq_events_available` is false on your `LoRa` or `GenericLoRa`), you will need to poll for interrupts by occasionally calling the `handle_irq_flags()` method.

# Code Examples

### Overview
First import the LoRa class, constants you plan to use, and a board definition: 
```python
from spi_lora.LoRa import LoRa
from spi_lora.constants import MODE, CODING_RATE
from spi_lora.boards.Generic_RFM95 import BOARD
```

Some board definitions require setup:
```python
BOARD.setup()
```

The LoRa object is instantiated using the board definition, and put into standby mode:
```python
lora = LoRa(BOARD)
lora.set_mode(MODE.STDBY)
```

Registers are queried like so:
```python
print(lora.version())      # this prints the sx127x chip version
print(lora.get_freq())     # this prints the frequency setting 
```

Most registers have idiomatic setters, using either numbers or the package constants:
```python
lora.set_freq(433.0)       # Set the frequency to 433 MHz 
```

In applications the `LoRa` class should be subclassed while overriding one or
more of the callback functions that are invoked on successful RX or TX
operations. You also generally will want an application main loop that will
poll for interrupts if your board does not automatically invoke them in
threads. For example:
```python
class MyLoRa(LoRa):

  def __init__(self, board=None, verbose=False):
    super(MyLoRa, self).__init__(board=board, verbose=verbose)
    # setup registers etc.

  def on_rx_done(self):
    payload = self.read_payload(nocheck=True) 
    # etc.
    
  def start():
    while True:
      if not self.irq_events_available:
        self.handle_irq_flags()
```

Some board definitions also require teardown at the end of the program to e.g.
return GPIO pins to their default state:
```python
BOARD.teardown()
```

### More details
Most functions in this package are setter and getter functions. For example, the setter and getter for 
the coding rate are demonstrated here
```python 
print(lora.get_coding_rate())               # print the current coding rate
lora.set_coding_rate(CODING_RATE.CR4_6)     # set it to CR4_6
```

@todo


# Installation

Make sure SPI is activated on your device. For a Raspberry Pi, you may need to [put `dtparam=spi=on` in your `/boot/config.txt`](https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/README.md). You may also need to grant permissions on `/dev/spidev0.0` or similar device nodes to the user you intend to work as.

## From PyPi

Simply `pip install spi-lora`, or depend on the `spi-lora` package in your package.

## From Source

If using this package from source, make sure `spidev` is installed:

```bash
pip install spidev>=3.1
```

Then you can clone the repo:

```bash
git clone https://github.com/interfect/spi-lora.git
cd spi-lora
```

At this point you may want to confirm that the unit tests pass. See the section [Tests](#tests) below.

You can now run the scripts. For example dump the registers with `lora_util.py`: 
```bash
$ ./lora_util.py
SX127x LoRa registers:
 mode               SLEEP
 freq               434.000000 MHz
 coding_rate        CR4_5
 bw                 BW125
 spreading_factor   128 chips/symb
 implicit_hdr_mode  OFF
 ... and so on ....
```


# Class Reference

The interface to the LoRa modem is implemented in the class `spi_lora.LoRa.LoRa`.
The most important modem configuration parameters are:
 
| Function         | Description                                 |
|------------------|---------------------------------------------|
| set_mode         | Change OpMode, use the constants.MODE class |
| set_freq         | Set the frequency                           |
| set_bw           | Set the bandwidth 7.8kHz ... 500kHz         |
| set_coding_rate  | Set the coding rate 4/5, 4/6, 4/7, 4/8      |
| | |
| @todo            |                              |

Most `set_*` functions have a mirror `get_*` function, but beware that the getter return types do not necessarily match 
the setter input types.

### Register naming convention
The register addresses are defined in class `spi_lora.constants.REG` and we use a specific naming convention which 
is best illustrated by a few examples:

| Register | Modem | Semtech doc.      | spi-lora                   |
|----------|-------|-------------------| ---------------------------|
| 0x0E     | LoRa  | RegFifoTxBaseAddr | REG.LORA.FIFO_TX_BASE_ADDR |
| 0x0E     | FSK   | RegRssiCOnfig     | REG.FSK.RSSI_CONFIG        |
| 0x1D     | LoRa  | RegModemConfig1   | REG.LORA.MODEM_CONFIG_1    |
| etc.     |       |                   |                            |

# Script references

### Continuous receiver `rx_cont.py`
The modem is put in RXCONT mode and continuously waits for transmissions. Upon a successful read the
payload and the irq flags are printed to screen.
```
usage: rx_cont.py [-h] [--ocp OCP] [--sf SF] [--freq FREQ] [--bw BW]
                  [--cr CODING_RATE] [--preamble PREAMBLE]

Continous LoRa receiver

optional arguments:
  -h, --help            show this help message and exit
  --ocp OCP, -c OCP     Over current protection in mA (45 .. 240 mA)
  --sf SF, -s SF        Spreading factor (6...12). Default is 7.
  --freq FREQ, -f FREQ  . Default is 869 MHz, a European frequency. US users might try 903.
  --bw BW, -b BW        Bandwidth (one of BW7_8 BW10_4 BW15_6 BW20_8 BW31_25
                        BW41_7 BW62_5 BW125 BW250 BW500). Default is BW125.
  --cr CODING_RATE, -r CODING_RATE
                        Coding rate (one of CR4_5 CR4_6 CR4_7 CR4_8). Default
                        is CR4_5.
  --preamble PREAMBLE, -p PREAMBLE
                        Preamble length. Default is 8.
```

### Simple LoRa beacon `tx_beacon.py`
A small payload is transmitted in regular intervals.
```
usage: tx_beacon.py [-h] [--ocp OCP] [--sf SF] [--freq FREQ] [--bw BW]
                    [--cr CODING_RATE] [--preamble PREAMBLE] [--single]
                    [--wait WAIT]

A simple LoRa beacon

optional arguments:
  -h, --help            show this help message and exit
  --ocp OCP, -c OCP     Over current protection in mA (45 .. 240 mA)
  --sf SF, -s SF        Spreading factor (6...12). Default is 7.
  --freq FREQ, -f FREQ  Frequency. Default is 869 MHz, a European frequency. US users might try 903.
  --bw BW, -b BW        Bandwidth (one of BW7_8 BW10_4 BW15_6 BW20_8 BW31_25
                        BW41_7 BW62_5 BW125 BW250 BW500). Default is BW125.
  --cr CODING_RATE, -r CODING_RATE
                        Coding rate (one of CR4_5 CR4_6 CR4_7 CR4_8). Default
                        is CR4_5.
  --preamble PREAMBLE, -p PREAMBLE
                        Preamble length. Default is 8.
  --single, -S          Single transmission
  --wait WAIT, -w WAIT  Waiting time between transmissions (default is 0s)
```


# Tests

Execute `test_lora.py` to run a few unit tests. 


# Contributors

Please feel free to comment, report issues, or contribute!

The `pySX127x` package on which this package is based is by [Markus C Mayer](http://mcmayer.net) of [Mayer Analytics](http://mayeranalytics.com).

# LoRaWAN
LoRaWAN is a LPWAN (low power WAN) and, and  **spi-lora** has almost no relationship with LoRaWAN. Here we only deal with the interface into the chip(s) that enable the physical layer of LoRaWAN networks. If you need a LoRaWAN implementation have a look at [Jeroennijhof](https://github.com/jeroennijhof)s [LoRaWAN](https://github.com/jeroennijhof/LoRaWAN) which is based on pySX127x.

By the way, LoRaWAN is what you need when you want to talk to the [TheThingsNetwork](https://www.thethingsnetwork.org/), a "global open LoRaWAN network". The site has a lot of information and links to products and projects.

# References

# Copyright and License

&copy; 2021 Adam Novak
&copy; 2015 Mayer Analytics Ltd., All Rights Reserved.

### Short version
The license is [GNU AGPL](http://www.gnu.org/licenses/agpl-3.0.en.html).

### Long version
spi-lora is free software: you can redistribute it and/or modify it under the terms of the 
GNU Affero General Public License as published by the Free Software Foundation, 
either version 3 of the License, or (at your option) any later version.

spi-lora is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
See the GNU Affero General Public License for more details.

You can be released from the requirements of the license by obtaining a commercial license. 
Such a license is mandatory as soon as you develop commercial activities involving 
spi-lora without disclosing the source code of your own applications, or shipping spi-lora with a closed source product.

You should have received a copy of the GNU General Public License
aling with spi-lora.  If not, see <http://www.gnu.org/licenses/>.

# Other legal boredom
LoRa, LoRaWAN, LoRa Alliance are all trademarks by ... someone.
