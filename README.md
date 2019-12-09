# LiveInteractiveBirdFeeder DIY Guide Walkthrough

# Finished Product: https://www.youtube.com/channel/UCErXmjslZq1scwuezZL9UCQ
Link to my youtube channel. Click on the LiveStream to view the finished product. 

Link to Bird Watching HQ: https://www.youtube.com/channel/UCuL60_Ko4m9xCaa4QDNgJrw
- Bird Watching HQ may obtain and host my stream in the future in an effort to expand both our audiences.


# Preface:
This guide includes detailed instructions to create your own automatic bird feeder. The bird feeder feeds on a schedule and also when you send a signal to it (or send money).


# Purpose: 
The purpose of this project is to expose more people to wildlife/animals and provide food for them. The more people that create something like this, the more people become aware of the natural beauty around us. All made possible by RPi, Arduino, and of course the Blockchain.

# Necessary Items: 
Total Cost: $150-$400 Depending on Camera Choice

These specific items were used and different configurations/versions are possible

	- RPi 4 (could run on any RPi)
		- $20-80 
		- You will need SD Card and Power cord of course
	- Arduino Mega 2560 (could run on any Arduino)
		- $20-50
		- Also Power Cord. I am using 800milliamp 12V unit.
	- Motor Controller Dual H Bridge L298N
	- Motor (12Volt DC Motor 120RPM)
	- 2 DiGi Xbee 1mW Wire Antenna Series 1
		- $60
		- I think other RF communication would work too
	- Solu Xbee USB to Serial Port Xbee Adapter Module
		- $5
	- Some Jumper Wires (Get a variety pack of male-male, male-female etc...)
		- $0-5
	- IPC-HDW5231R-ZE IP Camera
		- $50-200
		- Any IP Camera works, this brand supports RTMP for easy live streaming
	- TL-PoE150S PoE Injector (Power camera with the ethernet cord)
		- $20
		- Any PoE injector should work (Check your Camera power specs)
	- Wood
		- As much or as little as necessary for you to build a platform and enclosure for the fragile feeder/arduino components
	- Nails/Screws
	- Hammer/Screwdriver
	- Handheld Crank Spreader
		- This was the solution I chose for the feed dispenser. I found it at a thrift store. 
		- There are probably better alternatives but this hopper/dispenser works for now
	- Plastic Container
		- This was to ‘weatherproof’ the electrical components within the wood box. 
		- So far it has been pretty humid and moist in the mornings but everything is still functioning (for now)



# Design and Construction:
Create a wooden platform for the feed to land on. Also create an enclosure/box to house the feeder and electrical components outside. This should be wind and water resistant if your climate has these weather effects. Be creative. Anything works. The size of the platform does not matter and neither do any other dimensions. I suggest a small border surrounding the platform to prevent seed from falling off. I believe that a small hole or notch in the side walls would be nice to help with cleaning the platform.

# Wallet Setup:
Wallets allow people to send money to a specific receive address which can be queried using a multitude of API’s. There are functions in the code which query these specific receive addresses over and over again to detect a value change. I have decided to create Nano wallet using the Natrium app on Android. I used other apps to create Bitcoin wallets on my Android but there is no clear leader like Natrium so feel free to try many. Venmo is a newer application which was developed by CS students like myself. The Venmo API is locked (dumb) and therefore a workaround was implemented to react to payments. Instead of an HTTP request polling engine calling the API, the actual app notification generated when payment is received interrupts my Android and processing continues from there.


# Arduino Configuration:
- With wires attached to the TX/RX pins of the Arduino, it cannot communicate via USB. (uploading code to the device will fail) unplug the wires and try reuploading. 

# RPi Configuration:
- Install Raspbian (I am using July 2019 Version)
- Establish WiFi connectivity for the RPi
- Install at least Python 3 to the RPi
	- There are many tutorials online to do this.
	- After following one, ensure the latest version of Python is installed and used by default by running version command: python -v 
- The RPi must have SSH enabled in preferences
- The RPi must have Serial Communication enabled in preferences




# XBEE Configuration:
With the XBEE’s I could only find limited information detailing how to communicate between an Arduino and Raspberry Pi. A couple things to remember are that you must enable serial communication on the RPi and make sure that the Arduino does not have anything plugged into the tx/rx pins when uploading a sketch. Furthermore, in the links provided below, the tx/rx pins are flipped for RPi. Just remember that if you’re receiving communication use the RX pin, and transmitting something should go out on the TX line. 

I found these tutorials extremely helpful.
- Circuit Digest XBEE Raspberry Pi: https://circuitdigest.com/microcontroller-projects/raspberry-pi-xbee-module-interfacing
- Circuit Digest XBEE Arduino: https://circuitdigest.com/microcontroller-projects/arduino-xbee-module-interfacing-tutorial
These are essentially the same tutorial except each one connects a computer to either an arduino or a raspberry pi. I followed both of these to flash the receiver/sender info to the XBEE modules. There are specific places in the code I provide that send a signal over the serial output (RPi to XBEE send signal) and certain places (loop) in the Arduino code where I listen for a signal (XBEE to Arduino receive signal).


# Code:
There are Four basic elements to the RPi (transmitter) code: A polling engine which queries the blockchain for wallet balance change; A timer which feeds regularly, Code to send a feed signal to the Arduino (receiver); and a separate program to only send feed signal once (to be triggered by Tasker or for testing purposes). The comments within the code are, I believe, sufficient to explain what is going on. Remember to edit the Keys.txt file to contain your API keys for querying!

There are Two basic elements to the Arduino (receiver) code: A polling engine which queries the serial for input from the attached XBEE module; and the code necessary to send a signal to the motor to spin. Again, I believe the comments are sufficient to understand.

There is an additional file called Keys.txt where you will place your SnapyIO API key and BlockIO API key. This was created so that you do not accidentally upload any sensitive information like API keys!

Another fun file, called: "forever" is a linux bash script which will run any python program forever. It starts the process via a Popen() command and then waits for it to quit before looping back and starting it again. This way, if ever the program crashes unexpectedly, it will restart automatically. The only reason Birds.py should crash is a connection error stemming from a request. I have built in some smart requesting functionality to handle most exceptions, however in the unlikely event that the program crashes, this will provide a good failsafe. The uptime of my program running 24/7 is now 100% since November 2019.


# Tasker:
Tasker is necessary to respond to Venmo receipts. It could, theoretically, be used to respond to all forms of payment so long as a notification is generated. It can even do the HTTP get requests if needed. Tasker is extremely powerful and can be tailored to suit any Android automation needs. There is an extremely friendly and responsive community on reddit called r/Tasker which is quick to provide help to anyone using the application. Anyways, here is the link to my finished task which monitors for a Venmo notification and checks to see if it contains payment of greater than $0.49 and afterwards launches ConnectBot which does the rest…
https://taskernet.com/shares/?user=AS35m8m280j%2FFPGkbE9OvPhH4%2B%2FKd%2FFUPCMieeBd%2Batj8tVemNusHuhvDvo0rwACAjrS40KR&id=Task%3ATest


# ConnectBot:
ConnectBot is used to SSH into the RPi and start the program FeedOnce.py which will send one signal outside to dispense food. There is a guide online which covers how to set this up. The android device running tasked must be on the same network (and probably band: 2.4;5.1) as the RPi.
1. Install the free SSH client ConnectBot.
2. Key-based authentication with ConnectBot is required. A good tutorial: http://michaelchelen.net/0f3e/android-connectbot-ssh-key-auth-howto/
3. When you have set up the connection, long-press the connection in ConnectBot’s host list and select Edit host. Change the name to some nickname, e.g., myconnection.
4. Configure the post-login automation. Enter the command or script you’d like to run followed by a semicolon, exit and enter, e.g.: /home/me/somescript.sh; exit ↩. This is to make sure ConnectBot just runs the command and returns.
5. Now let’s use it in Tasker. Create a Task, select +, System, Send Intent. Configure the action as follows:
	- Action: android.intent.action.VIEW
	- Cat: None
	- Data: ssh://user@host:port#myconnection
	- Target: Activity
When you run the Task, the remote command should execute. Note that for every different command you want to run on the host, you need to create a separate profile in ConnectBot, with different nicknames.


# Testing:
There are many print statements left in the code. Uncomment them to see results in the console. Otherwise there is logging enabled, check the log file for important notifications!


# Live Stream:
The camera I have chosen, the (redacted, banned from US distribution), is capable of RTMP (RealTimeMessagingProtocol) transmission which allows the camera itself to bypass the encoder (or act as one idk) and send the frames/audio it captures directly to an RTMP receiver (youtube livestream). Thanks to this technology, after launching your IP Camera configuration settings (by connecting via ip address to your network connected camera) you may specify an RTMP address and pre-shared key to connect the IP Cam to the Live Stream. I used this tutorial to understand how to do this with my specific camera: https://www.youtube.com/watch?v=caGFCowzN74
Some things to note are that Youtube digests H264 Video format and AAC Audio format. Also play around with bitrate settings until youtube stops complaining. Your ISP may (Almost Guaranteed!) throttle a high bitrate. I have 100 up and down, which is sustainable for 1080p60fps

My camera video settings are as follows:

	- Format: H.264
	- FPS: 50
	- Keyframe: 100 (Should be double FPS)
	- Bit Rate Type: CBR
	- Bitrate: 4096
My camera audio settings are as follows:

	- Format: AAC
	- Sampling Frequency: 64000


# Credit:
These people inspired me: tanglesheep IOTA (Live Interactive Sheep Feeding) and Mr. Dove (Live Interactive Bird Feeding) on youtube. These projects I have reverse engineered and intend to provide step by step instructions for anyone else to do the same. Furthermore, all the links I used for research will be provided throughout the guide and included in the bibliography at the end of this document.

# Bibliography:

- Linking WebCam to Youtube Livestream RTMP tutorial: https://www.youtube.com/watch?v=caGFCowzN74
- Circuit Digest XBEE Raspberry Pi: https://circuitdigest.com/microcontroller-projects/raspberry-pi-xbee-module-interfacing
- Circuit Digest XBEE Arduino: https://circuitdigest.com/microcontroller-projects/arduino-xbee-module-interfacing-tutorial
- Tasker Export: https://taskernet.com/shares/?user=AS35m8m280j%2FFPGkbE9OvPhH4%2B%2FKd%2FFUPCMieeBd%2Batj8tVemNusHuhvDvo0rwACAjrS40KR&id=Task%3ATest
- ConnectBot Key Based Authentication: http://michaelchelen.net/0f3e/android-connectbot-ssh-key-auth-howto/
- RTMP YouTube LiveStream Guide for Dahua (America: Empire Tech) Cameras: https://www.youtube.com/watch?v=caGFCowzN74
- Python Requests Tutorial: https://realpython.com/python-requests/
- Python Requests Retries Info: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
- Python Linux run forever script: https://www.alexkras.com/how-to-restart-python-script-after-exception-and-run-it-forever/




