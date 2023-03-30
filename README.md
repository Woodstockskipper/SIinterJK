# SIinterJK
## Interface zur Übertragung der Daten vom JiKong-BMS (RS485) zum SMA Sunny Island 6.0 (CAN)
### Vorgeschichte
Seit etwa einem Jahr besitze ich eine selbst gebaute LiFePo4 Batterie zur Zwischenspeicherung meiner PV-Energie. Die Batterie besteht aus vier parallel geschalteten Blöcken mit je 7 kWh Kapazität. Jeder Block von 16 in Reihe geschalteten 3,2V Zellen wird mit einem Batteriemanagementsystem (BMS), Typ JiKong BD6A20S-10P, überwacht und aktiv balanciert.
Als Batterieumrichter benutze ich den Sunny Island 6.0 (SI) von SMA. Dieser besitzt zwei Betriebsmodi: 1) für Litium Batterien mit einem eigenen BMS und CAN-Bus Kommunikation mit dem SI und 2) für Bleibatterien, für die er entsprechende Lade- und Entladeprogramme besitzt.
Da das BMS von JK über eine RS485 Schnittstelle verfügt, die natürlich nicht mit dem SI interagiert, habe ich meine LiFePo4 Batterie im Modus für Bleibatterien am SI betrieben, was funktioniert, jedoch wird nur etwa 50% der Batteriekapazität genutzt. Die Bleibatterie hat eine relativ linearen Verlauf der Kapazität über der Spannung, wodurch der SI die Bleibatterie sehr gut managen kann und der SOC (State Of Charge) gut bestimmt wird. Da jedoch die LiFePo4 Batterien über 85% ihrer Kapazität bei etwa 3,2V verharren, kommt es zu der fehlerhaften SOC Berechnung des SI und der eingeschränkten Kapazitätsnutzung.
Daher reifte der Wunsch heran einen Adapter zwischen der RS485 Schnittstelle des JK BMS und dem CAN Anschluss des SI zu bauen.
### Hardware
Da ich ein wenig Vorkenntnisse im Betrieb von Raspberry Pi habe, lag es nahe den auch für diese Aufgabe zu verwenden. So besorgte ich mir einen Raspberry Pi 3B (2B und 3A funktionieren ebenfalls), den RS485/CAN HAT von WaveShare und den passenden RS485 Adapter von JiKong, wobei bei letzterem darauf geachtet werden muss, dass dieser zum BMS Typ passt. Daher bei Bestellung unbedingt den BMS Typen angeben!
Dann RS485 Adapter an den GPS-Anschluss des BMS anschließen (möglichst spannungsfrei, die Dinger sind sehr empfindlich!) Dann die gelbe Ader des freien Endes an Anschluss A des HATs und Die weiße Ader an Anschluss B des Hats.
Anschließend die Adern 4 und 5 eines CAT5 Kabels mit RJ45 Stecker an CAN_H (4) und CAN_L (5) des HATs anschließen. Die Adern 3 und 6 mit einem 120 Ohm Widerstand terminieren. Siehe auch Datei "SMA CAN protocol(2).pdf".
Anschließend den RJ45 Stecker in die entsprechende Buchse des SI einstecken.
### Einrichten des Raspberry Pi
Zunächst wird ein Rasbian Image auf eine Micro SD Karte geschrieben. Hierbei darauf achten, dass eine SSH Verbindung ermöglicht wird.
Anschließend werden zur config.txt mittels eines Editors folgende Zeilen hinzugefügt:
```
dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=12000000,interrupt=25,spimaxfrequency=2000000
enable_uart=1
# Bluetooth (UART(0)) nicht deaktivieren!
```
Nun kann die SD Karte in den Raspberry Pi geschoben werden und dieser gestartet werden.
Mit SSH loggst Du Dich auf dem Raspberry Pi ein und installierst nun einige Bibliotheken:
```
cd
sudo apt-get install python3-pip
sudo pip3 install pillow
sudo pip3 install numpy
sudo apt-get install libopenjp2-7
sudo apt install libtiff
sudo apt install libtiff5
sudo apt-get install libatlas-base-dev

sudo apt-get update
sudo apt-get install screen
sudo pip3 install python-can
sudo pip3 install RPi.GPIO
sudo pip3 install smbus
```







work in progress....


### Sehr hilfreiche Quellen bei GitHub:
https://github.com/jblance/mpp-solar/issues/112
