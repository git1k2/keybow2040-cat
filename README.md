# Keybow 2040 CAT keyboard for Yaesu FTdx10 transceiver

This is using the UART pads on the Keybow 2040 to communicate with a radio transceiver via RS232. It gives you extra buttons you might miss on your radio's frontpanel.

<img src="https://github.com/git1k2/keybow2040-cat/raw/main/kb-cat.jpg" width="640">

<img src="https://github.com/git1k2/keybow2040-cat/raw/main/max3232.jpg" width="640">


## What you need
* Pimoroni Keybow 2040.
* Relegendable MX-compatible keycaps.
* A max3232 level shifter from the 3.3v UART to -/+ 5 V.

## Steps
* Update circuitpython to the latest version, download here: https://circuitpython.org/board/pimoroni_keybow2040/
* Update the adafruit_is31fl3731 library, download here: https://github.com/adafruit/Adafruit_CircuitPython_IS31FL3731
* Upload the code.py example.

