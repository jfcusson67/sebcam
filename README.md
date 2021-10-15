# sebcam
Automate picture or video shots on raspberry pi for Stratospheric Expandable Balloons (SEB) flights
(C) Canadian Space Agency, 2021
Author      : J-F Cusson
===============================================================================
Target platform     : Raspberry pi zero, TBD OS
Peripherals         : MIPI Camera
Development platform: Raspberry pi 3B+, Raspbian Buster
Language            : Python 3.7.3 or later
IDE                 : n/a
Packages            : TBD

Description
-----------
This software takes control of the MIPI camera. Depending on what is specified
in the setup section, it will take series of images or videos, saved on the
SD card with a timestamp in the name. Images are of JPG format, video H264.

Development and execution environment setup instructions
--------------------------------------------------------
See header of sebcam.py
