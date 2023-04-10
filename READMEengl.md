# SIinterJK
## Interface for transmission of battery data from JiKong BMS (RS485) to SMA Sunny Island 6.0 (CAN)
[German version](README.md)
### Introduction
For about a year I have owned a self-built LiFePo4 battery for intermediate storage of my PV energy. The battery consists of four blocks connected in parallel, each with 7 kWh capacity. Each block of 16 series-connected 3.2V cells is monitored and actively balanced with a battery management system (BMS), type JiKong BD6A20S-10P.

I use the Sunny Island 6.0 (SI) from SMA as the battery inverter. This has two operating modes: 

1) for lithium batteries with their own BMS and CAN bus communication with the SI, and 
2) for lead-acid batteries, for which the SI has appropriate charge and discharge programs.

Since JK's BMS has a UART interface that does not interact with the SI's CAN- protocol, I ran my LiFePo4 battery in lead-acid battery mode on the SI, which works, but only about 50% of the battery capacity is used. Lead acid batteries have a relatively linear curve of capacity versus voltage, which allows the SI to manage the lead acid battery very well, and the SOC (State Of Charge) is well determined. However, since LiFePo4 batteries remain at about 3.2V for over 85% of their capacity, the SI's erroneous SOC calculation and limited capacity utilization occurs.

Therefore, the desire to build an adapter between the RS485 interface available for the JK BMS UART port and the CAN port of the SI matured to take full advantage of the SI's capabilities.
However, my last programming experience was over 40 years old (Fortran, Pascal) and so I tried my hand at Python with the help of the WaveShare HAT's documentation, some repositories from Github (see references) and ChatGBT. So I apologize if the code may be a bit bumpy. I invite everyone to suggest improvements and possibly build a small interface to display the values attractively e.g. via browser.
### Hardware
Since I have some knowledge in using Raspberry Pi, it was obvious to use it for this task. So I got a Raspberry Pi 3B (2B, 3A and zero work as well), the RS485/CAN HAT from WaveShare and the appropriate RS485 adapter from JiKong, but with the latter you have to make sure that it fits to the BMS type. Therefore please specify the BMS type when ordering!

I tested the JiKong hardware JK-BD6A20S10P V10.X-W and the software V10.05 and V10.09.

Having the parts in hand, connect the RS485 adapter to the GPS connector of the BMS (as voltage free as possible, these things are very sensitive!) Then connect the yellow wire of the free end to connector A of the HAT and the white wire to connector B of the HAT. (The black wire remains unused)
Then connect wires 4 and 5 of a CAT5 cable with RJ45 connector to CAN_H (4) and CAN_L (5) of the HAT. Terminate (connect) the wires 3 and 6 with a 120 Ohm resistor. See also the [SMA-CAN documentation](sma%20can%20protocol%20(2).pdf).

Then plug the RJ45 connector into the corresponding socket of the SI.
### Setting up the Raspberry Pi
First write a Rasbian image to a Micro SD card. Make sure that an SSH connection is enabled.
Then the following lines must be added to config.txt using an editor:
```
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=12000000,interrupt=25,spimaxfrequency=2000000
enable_uart=1
# Do not disable Bluetooth (UART(0))!
```
Now you can put the SD card into the Raspberry Pi and start it.
Use SSH to log in to the Raspberry Pi and install some libraries:
```
cd
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install libopenjp2-7
sudo apt install libtiff
sudo apt install libtiff5
sudo apt-get install libatlas-base-dev
sudo apt-get install screen
sudo python3 -m pip install pyserial
sudo pip3 install pillow
sudo pip3 install numpy
sudo pip3 install python-can
sudo pip3 install RPi.GPIO
sudo pip3 install smbus
sudo apt-get update
```
In a last step you have to change the Raspi Configuration:
```
sudo raspi-config
```
Choose Interfaces Options -> Serial-> no -> yes ->
### Software
In the code siinterjkp.py, after loading the libraries, first the parameters of the interfaces are defined and then the fixed parameters for the SI are set:
To make sure that the SI detects only critical errors, which could occur if the BMS is defective, I set the allowed range for voltages and currents larger, just in the uncritical range for the used cells, than set in the BMS. These values then set the outer frame for the work of the BMS(s), which completely independently protect the battery block(s). The SI then only shuts down when the battery is disconnected by the BMS or reaches the lower discharge limit.
I also set the maximum charge and discharge currents smaller than the SI and battery can provide and larger than set in the BMS.

The parameter "n" is set to the number of battery blocks connected in parallel, if any, since only one BMS is read out. For example, I use four battery blocks in parallel, each with its own BMS, but read out only one BMS and multiply the values for current and capacity by the factor n=4. This has proven to be sufficient when the capacity of the blocks is the same.

The State Of Health (SOH) is not determined by the JK-BMS and is therefore fixed at 100%.

In the next lines, the data is requested from the BMS. The corresponding value pairs are then read from the hex string received. The code is written for a LiFePo4 battery with 16 cells. When using lithium-ion batteries, fewer cells are usually used on the SI due to the higher cell voltage.  Since the response string varies in length depending on the number of cells, the position of the required values changes. However, the addresses of the values can be determined from the documentation of the [BMS Protokoll description](bms.protocol.v2.5.english.pdf). The lines commented with * must then be adapted accordingly.

For control purposes, the read and processed values are output in the terminal window when SIinterJK is started discretely (not in the background).
The alarm and warning messages of the BMS are sent to the SI only as warnings, since the batteries are intrinsically safe by the BMS, it does not make sense to switch off the SI when alarms of the BMS occur.

Then the processed values are formatted for CAN output and sent.

Finally, the buffer is emptied so that it does not overflow when the SI is switched off.
The whole process is repeated about every 10s. If there is no data at the SI for 60s, it switches off.

I put "siinterjkb.py" in an own directory under the user "pi": /home/pi/SIinterJK/siinterjkp.py

The application is then started after changing to the correct directory with the command: 
```
sudo python3 siinterjkp.py
```

In the terminal window you can see the current values received by the BMS and the strings sent to the CAN bus.
If you make your own adjustments to the code, you can see here if the changes lead to the correct result.

If someone has an idea how to display this information over a local network in a browser, he is welcome to extend the code accordingly and share the result here.
### Starting the application in the background
To make sure that the code is automatically executed, e.g. after a blackout, when the Raspberry Pi is booted and always 
runs in the background, you can create a systemd service:
Create a file named my_service.service in the /etc/system/system/ directory:
```
sudo nano /etc/systemd/system/my_service.service
```
Paste the following content into the my_service.service file:
```
[Unit]
Description=my service
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /path/to/your/script.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```
Replace /path/to/your/script.py with the path to siinterjkp.py. For example, I saved SIinterJKp under: /home/pi/SIinterJK/siinterjkp.py.
Save and close the file.

Then activate the service with the following command:
```
sudo systemctl enable my_service.service
```
Then start the service with the following command:
```
sudo systemctl start my_service.service
```
Now SIinterJKp will start automatically when the Raspberry Pi boots up and will run in the background.

### Very helpful sources:
https://github.com/jblance/mpp-solar/issues/112 starting with entry from 05/18/21, this describes the commands to the JK-BMS as well as the response format. (better than the original documentation)

https://github.com/camueller/SmartApplianceEnabler Great tool for measuring and switching loads in conjunction with SMA Homemanager 2.0.

I wish you a great success with your battery storage project!

Lueneburg, April 8th, 2023

Stephan Brabeck
