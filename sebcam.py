#!/usr/bin/env python3
# ########################################################################### #
#         _____ ___________   _____   ___  ___  ___ ___________  ___          #
#        /  ___|  ___| ___ \ /  __ \ / _ \ |  \/  ||  ___| ___ \/ _ \         #
#        \ `--.| |__ | |_/ / | /  \// /_\ \| .  . || |__ | |_/ / /_\ \        #
#         `--. \  __|| ___ \ | |    |  _  || |\/| ||  __||    /|  _  |        #
#        /\__/ / |___| |_/ / | \__/\| | | || |  | || |___| |\ \| | | |        #
#        \____/\____/\____/   \____/\_| |_/\_|  |_/\____/\_| \_\_| |_/        #
# ########################################################################### #
"""An application to control a SEB camera automatically during a flight

(C) Canadian Space Agency, 2021
Author      : J-F Cusson
Contributors: n/a
===============================================================================
Target platform     : Raspberry pi zero, TBD OS
Peripherals         : MIPI Camera
Development platform: Raspberry pi 3B+, Raspbian Buster
Language            : Python 3.7.3 or later
IDE                 : Thonny Python IDE
Packages            : picamera
===============================================================================
Version History:
2021-10-07 JFC V1.00 Initial version
2021-10-15 JFC V1.01 Added necessary stuff for init.d execution control
===============================================================================
TODO:
- Import settings from a configuration file
- Detect shutdown request and stop operations gracefully
- Allow more image configuration
- Take control of automatic gain and white balance so that start of each
  video is more consistant
- Implement a socket listener so that commands can be sent for remote control
- etc...
===============================================================================
Description
-----------
This software takes control of the MIPI camera. Depending on what is specified
in the setup section, it will take series of images or videos, saved on the
SD card with a timestamp in the name. Images are of JPG format, video H264.

Usage
-----
Locate, at the start of the code, these lines and set ACTION to either
"TAKE_VIDEOS" or "TAKE_IMAGES" (put the other one in comment). Set the
associated parameters to correct values. For example, with this setup
you will take 30 seconds videos indefinitely:

ACTION = "TAKE_VIDEOS"
LENGTH_OF_VIDEOS_SECONDS = 30 
NUMBER_OF_VIDEOS = 0 #Put '0' for infinite
SECONDS_BETWEEN_VIDEOS = 1
# ACTION = "TAKE_IMAGES"
# NUMBER_OF_IMAGES = 0 # Put '0' for infinite
# SECONDS_BETWEEN_IMAGES = 30

Development and execution environment setup instructions
--------------------------------------------------------
Ref = https://www.raspberrypi.org/documentation/computers/os.html
      https://picamera.readthedocs.io/en/release-1.13/install.html

1. Update the raspberry pi (upgrade is required to get latest firmware):
       sudo apt update
       sudo apt full-upgrade

2. Make sure you have a correct version of Python3:
       python
   ==> if Python 3.7.3 or later is displayed, you are ok. Otherwise you will need
   to update your Python (procedure TBD)

3. Verify that you have the "picamera" Python library.
       python3 -c "import picamera"
   ==> If no error is displayed, you have the picamera (it is normally there by
   default on the raspberry pi. Otherwise, install it:
       sudo apt-get update
       sudo apt-get install python-picamera python3-picamera
   Alternatively, you can install using the Python "pip" tool:
       sudo pip install picamera
       
4. Install and enable your camera (using "sudo raspi-config" on the command line
   or the graphical configuration tool.
   Camera can be tested with:
       raspistill -o tst.jpg

Tools:
   Image cam be viewed using a tool like "feh" that can be installed using:
       sudo apt install feh -y
       feh tst.jpg
   To view videos, you can use VLC:
       sudo apt install -y vlc
       
Examples:
-----------------------------------
(1) Take a single 1024x768 picture:
-----------------------------------
camera = PiCamera()
camera.resolution = (1024, 768)
camera.start_preview()
# Camera warm-up time
sleep(2)
camera.capture('tst.jpg')
----------------------------------------
(2) Take 10 pictures in sequence at 2Hz:
----------------------------------------
camera = PiCamera()
camera.framerate = 2
camera.capture_sequence(['image%02d.jpg' % i for i in range(10)])
----------------------------------------------
(3) Take images continuously, every 2 seconds:
----------------------------------------------
camera = PiCamera()
camera.start_preview()
sleep(2) # Camera warm-up time
for filename in camera.capture_continuous('img{timestamp:%Y-%m-%dT%H:%M:%S}.jpg'):
    print('captured %s' % filename)
    sleep(2)
---------------------
(4) Take a 30s video:
---------------------
camera = PiCamera()
camera.start_recording('tstvid.h264')
camera.wait_recording(30)
camera.stop_recording()


Setup for AUTOMATIC STARTUP when Pi boots up
--------------------------------------------
Using init.d (System V): The directory /etc/init.d contains the scripts that are 
used to start the services at boot time. They must be formatted as Linux Standard 
Base (LSB) i.e. have a standard header filled with information (e.g. dependencies, 
description). The command update.rc will configure the system with these scripts 
(i.e. it is NOT the script contained in this folder that are directly executed).

For this setup example, we’ll assume that this script is located at
“/home/seb/sebcam.py” and that a script called "sebcamctrl" will be created
to control execution:

a)	cd /etc/init.d
b)	sudo nano sebcamctrl

Create the following content and save the file afterward (CTRL-O and CTRL-X):
IMPORTANT NOTE: If you use COPY-PASTE from this header to the new file,
the quotes '"' might be copied as the wrong caracter. So if you are having
problems (e.g. you get a "not found" error), make sure to edit the file and
replace with standard quote characters manually.

#!/bin/sh
# /etc/init.d/sebcamctrl
### BEGIN INIT INFO
# Provides:        sebcamctrl
# Required-Start:  $local_fs $network $remote_fs $syslog $time
# Required-Stop:   $local_fs $network $remote_fs $syslog $time
# Default-Start:   2 3 4 5
# Default-Stop:    0 1 6
# Short-Description: Controls sebcam.py app. exec.
# Description:       Controls sebcam.py application execution (CSA STRATOS)
### END INIT INFO
PATHAPP="/home/seb/sebcam.py &"
PIDAPP="/home/seb/sebcam_pid.txt"
case $1 in
        start)
                echo "starting"
                $PATHAPP
        ;;
        stop)
                echo "stopping"
                PID=$(cat $PIDAPP)
                kill $PID
        ;;
esac

c)	sudo chmod +x sebcamctrl
d)	sudo update-rc.d sebcamctrl defaults
e)	sudo reboot

Notes:
•	$local_fs = All local files are mounted
•	$network = Low level networking is initialized
•	$remote_fs = All file systems are mounted (includes $local_fs)
•	$syslog = System logger is operational
•	$time = The system time has been set
•	Note that another script could wait for this script to be initialized
by specifying $sebcamctrl (TBC if we need the “$” here).

Note that the sebcam Python script must start with the following
lines, so that the process id is recorded in file /home/seb/sebcam_pid.txt
(it was done for version V1.01):
#!/usr/bin/env python3
import os
pid = os.getpid()
op  = open("/home/seb/sebcam_pid.txt")
op.write("%s" % pid)
op.close()

When the system reboots, sebcamctrl should run.
If you need to stop it:
sudo /etc/init.d/sebcamctrl stop
To start it again:
sudo /etc/init.d/sebcamctrl start &
To remove the service (i.e. prevent automatic startup):
a)	cd /etc/init.d/
b)	Remove sebcamctrl
c)	sudo update-rc.d sebcamctrl remove
Note: the fact that “sebcamctrl” is not in the folder anymore is of no
concern: update-rc clears all occurences of myscript in the startup 
configuration files (it was copied there by update-rc sebcamctrl defaults)
===============================================================================
"""
import os
from time import strftime
from time import sleep
from picamera import PiCamera

# ---------------------------------------- #
# Software version identifier - Increment! #
# ---------------------------------------- #
VERSION_STRING = "SEBCAM V1.01"

# ---------------------------------------- #
# PATHS: Very important to setup correctly #
# Folders must ALREADY exist!!             #
# ---------------------------------------- #
PATH_EXEC = "/home/seb/"
PATH_IMAGES = "/home/seb/images/"
PATH_VIDEOS = "/home/seb/videos/"

# ----------------------------------- #
# Needed for init.d execution control #
# MUST CORRESPOND TO INIT.D SETUP,    #
# SEE INFOS IN HEADER!!!!             #
# ----------------------------------- #
pid = os.getpid()
op  = open(PATH_EXEC+"sebcam_pid.txt","w")
op.write("%s" % pid)
op.close()

# ---------------------------------- #
#             S E T U P              #
# Comment out one of these sections: #
# ---------------------------------- #
ACTION = "TAKE_VIDEOS"
LENGTH_OF_VIDEOS_SECONDS = 10 
NUMBER_OF_VIDEOS = 0 #Put '0' for infinite
SECONDS_BETWEEN_VIDEOS = 10
# ---------------------------------- #
# ACTION = "TAKE_IMAGES"
# NUMBER_OF_IMAGES = 0 # Put '0' for infinite
# SECONDS_BETWEEN_IMAGES = 20
# ---------------------------------- #

# -------------------------------------- #
# Power up the camera and let it warm up #
# -------------------------------------- #
camera = PiCamera()
# camera.start_preview()
sleep(2) # Camera warm-up time

# ---------------------------------- #
# Perform what is requested in SETUP #
# ---------------------------------- #
print( "Starting " + VERSION_STRING )
#.............................................................................
if ACTION == "TAKE_IMAGES":
#.............................................................................
    if( NUMBER_OF_IMAGES == 0 ):
        print(f"Configured to take images every {SECONDS_BETWEEN_IMAGES} second(s)")
    else:
        print(f"Configured to take {NUMBER_OF_IMAGES} images, one every {SECONDS_BETWEEN_IMAGES} second(s)")
    camera.resolution = (1024, 768)   #Comment out to use default resolution
    currentImageIndex = 1
    for filename in camera.capture_continuous(PATH_IMAGES+'img{timestamp:%Y-%m-%dT%H:%M:%S}.jpg'):
        print('captured %s' % filename)
        sleep(SECONDS_BETWEEN_IMAGES)
        if( (currentImageIndex >= NUMBER_OF_IMAGES) and (NUMBER_OF_IMAGES != 0) ):
            break
        currentImageIndex += 1
    print('Took all images requested')
#.............................................................................
elif ACTION == "TAKE_VIDEOS":
#.............................................................................
    if( NUMBER_OF_VIDEOS == 0 ):
        print(f"Configured to take {LENGTH_OF_VIDEOS_SECONDS} seconds videos at {SECONDS_BETWEEN_VIDEOS} second(s) intervals")
    else:
        print(f"Configured to take {NUMBER_OF_VIDEOS} {LENGTH_OF_VIDEOS_SECONDS} seconds videos, at {SECONDS_BETWEEN_IMAGES} second(s) intervals")
    camera.resolution = (640, 480)    #Comment out to use default resolution
    currentVideoIndex = 1
    while True:
        filename = PATH_VIDEOS+"vid_"+strftime("%Y-%m-%d_%H:%M:%S")+".h264"
        camera.start_recording(filename)
        camera.wait_recording(LENGTH_OF_VIDEOS_SECONDS)
        camera.stop_recording()
        print('captured %s' % filename)
        sleep(SECONDS_BETWEEN_VIDEOS)
        if( (currentVideoIndex >= NUMBER_OF_VIDEOS) and (NUMBER_OF_VIDEOS != 0) ):
            break
        currentVideoIndex += 1
    print('Took all videos requested')
else:
    print('Invalid action requested')

#end of sebcam code
