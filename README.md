blinkenPI
=========

This Script can play back files in the Blinkenlights Markup Language (BML) on the Cisceo PI Lite LED Matrix. You can draw BML animations with [blinkenpaint](http://blinkenlights.net/blinkenlights/blinkenpaint). Other versions that may work better for you are [stereoscope paint](http://www.blinkenpaint.de) or [ArcadePaint](http://blinkenlights.net/arcade/arcadepaint), which seems to be the only one compatible with OSX 10.8.
You can also generate them with Processing using [this library made by Robin Senior](http://robinsenior.com/blinkenlights/) or from a series of images using [this converter made by Dan Fraser](http://www.capybara.org/~dfraser/archives/261).

The script assumes that the serial port where the Pi Lite is connected is /dev/ttyAMA0.

Works best with monochrome animations 14 pixels wide and 9 pixels high. If there are shades of grey, only black will mean the pixel is off. Everything else means the pixel is on.

Usage
-----


Make sure you have [set up your Raspberry Pi to work with the Pi Light](http://openmicros.org/index.php/articles/94-ciseco-product-documentation/raspberry-pi/280-b040-pi-lite-beginners-guide#Setting%20up%20the%20Raspberry%20Pi%20for%20the%20Pi-Lite).
To play an animation run the script with the filename as an argument:
```
python blinkenpi.py test.bml
```
To quit just hit CTRL+C.

Requirements
------------
pySerial

You can install this on a vanilla raspbian setup with:
```
sudo apt-get install python-serial
```
Or just use your prefered method of installing python packages.

