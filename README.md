# SIinterJK
## Interface zur Übertragung der Batteriedaten vom JiKong-BMS (RS485) zum SMA Sunny Island 6.0 (CAN)
### Vorgeschichte
Seit etwa einem Jahr besitze ich eine selbst gebaute LiFePo4 Batterie zur Zwischenspeicherung meiner PV-Energie. Die Batterie besteht aus vier parallel geschalteten Blöcken mit je 7 kWh Kapazität. Jeder Block von 16 in Reihe geschalteten 3,2V Zellen wird mit einem Batteriemanagementsystem (BMS), Typ JiKong BD6A20S-10P, überwacht und aktiv balanciert.

Als Batterieumrichter benutze ich den Sunny Island 6.0 (SI) von SMA. Dieser besitzt zwei Betriebsmodi: 

1) für Litium Batterien mit einem eigenen BMS und CAN-Bus Kommunikation mit dem SI und 
2) für Bleibatterien, für die der SI entsprechende Lade- und Entladeprogramme besitzt.

Da das BMS von JK über eine RS485 Schnittstelle verfügt, die nicht mit dem CAN- Protokoll des SI interagiert, habe ich meine LiFePo4 Batterie im Modus für Bleibatterien am SI betrieben, was funktioniert, jedoch werden nur etwa 50% der Batteriekapazität genutzt. Bleibatterien haben einen relativ linearen Verlauf der Kapazität über der Spannung, wodurch der SI die Bleibatterie sehr gut managen kann und der SOC (State Of Charge) gut bestimmt wird. Da jedoch LiFePo4 Batterien über 85% ihrer Kapazität bei etwa 3,2V verharren, kommt es zu der fehlerhaften SOC Berechnung des SI und der eingeschränkten Kapazitätsnutzung.

Daher reifte der Wunsch heran einen Adapter zwischen der RS485 Schnittstelle des JK BMS und dem CAN Anschluss des SI zu bauen, um die Möglichkeiten des SI voll zu nutzen.
Meine letzten Programmiererfahrungen waren allerdings über 40 Jahre alt (Fortran, Pascal) und so habe ich mich mit Hilfe der Dokumentation des WaveShare HATs, einigen Repositorys aus Github (siehe Verweise) und ChatGBT an Python versucht. Ich bitte daher zu entschuldigen, wenn der Code u.U. ein wenig holperig ist. Ich lade jeden ein Verbesserungen vorzuschlagen und ggf. eine kleine Oberfläche zu bauen um die Werte attraktiv z.B. per Browser darzustellen.
### Hardware
Da ich ein wenig Vorkenntnisse in der Anwendung von Raspberry Pi habe, lag es nahe den auch für diese Aufgabe zu verwenden. So besorgte ich mir einen Raspberry Pi 3B (2B, 3A und zero funktionieren ebenfalls), den RS485/CAN HAT von WaveShare und den passenden RS485 Adapter von JiKong, wobei bei letzterem darauf geachtet werden muss, dass dieser zum BMS Typ passt. Daher bei Bestellung unbedingt den BMS Typen angeben!

Ich habe die JiKong Hardware JK-BD6A20S10P V10.X-W und die Software V10.05 und V10.09 getestet.

Dann RS485 Adapter an den GPS-Anschluss des BMS anschließen (möglichst spannungsfrei, die Dinger sind sehr empfindlich!) Dann die gelbe Ader des freien Endes an Anschluss A des HATs und die weiße Ader an Anschluss B des HATs. (Die schwarze Ader bleibt unbelegt)
Anschließend die Adern 4 und 5 eines CAT5 Kabels mit RJ45 Stecker an CAN_H (4) und CAN_L (5) des HATs anschließen. Die Adern 3 und 6 mit einem 120 Ohm Widerstand terminieren (verbinden). Siehe auch Datei "SMA CAN protocol(2).pdf".

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
In einem letzten Schritt muss noch das Konfigurationsmenü angepasst werden:
```
sudo raspi-config
```
Dann Interface Optionen wählen -> Serial -> no -> yes ->
Damit ist der Raspberry Pi fertig für die Installation der Software
### Software
Im Code SIinterJKp.py werden nach dem Laden der Libraries zunächst die Parameter der Schnittstellen definiert und anschließend die festen Parameter für den SI gesetzt. 
Damit der SI möglichst nur kritische Fehler detektiert, die z.B. bei defektem BMS auftreten könnten, setze ich den erlaubten Bereich für Spannungen und Ströme größer, gerade noch im unkritischen Bereich für die verwendeten Zellen, an, als im BMS eingestellt. Diese Werte setzen dann den äußeren Rahmen für die Arbeit des (der) BMS, welche(s) vollkommen unabhängig die Batterieblocks absichern. Der SI schaltet sich dann nur bei Abschaltung der Batterie durch das BMS oder Erreichen des unteren Entladegrenze ab.
Die maximalen Lade- und Entladeströme setze ich ebenfalls kleiner an als SI und Batterie leisten können und größer als im BMS eingestellt.

Der Parameter "n" wird auf die Anzahl der ggf. parallel geschalteten Batterieblöcke gesetzt, da ja nur ein BMS ausgelesen wird. Ich nutze z.B. vier Batterieblöcke parallel, jedes mit einem eigenen BMS, lese jedoch nur ein BMS aus und multipliziere die Werte für Strom und Kapazität mit dem Faktor n=4. Dies hat sich bei gleicher Kapazität der Blöcke als ausreichend erwiesen.

Der State Of Health (SOH) wird vom JK-BMS nicht ermittelt und wird daher auf 100% fest eingestellt.

Im nächsten Schritt werden die Daten vom BMS angefordert. Aus dem daraufhin emfangenen Hex String werden dann die entsprechenden Wertepaare ausgelesen. Der Code ist für eine LiFePo4 Batterie mit 16 Zellen geschrieben. Bei Verwendung von Litium-Ionen Batterien kommen aufgrund der höheren Zellenspannung in der Regel weniger Zellen am SI zum Einsatz.  Da der Antwortstring je nach Zellenzahl unterschiedlich lang ist, verändert sich die Position der benötigten Werte. Die Adressen der Werte können aber anhand der Dokumentation des Protokolls (bms.protocol.v2.5.english.pdf) bestimmt werden. Entsprechend müssen dann die mit * kommentierten Zeilen angepasst werden.

Zur Kontrolle werden die ausgelesenen und verarbeiteten Werte im Terminalfenster ausgegeben, wenn SIinterJK diskret gestartet wird (nicht im Hintergrund).
Die Alarm- und Warnmeldungen des BMS werden an den SI nur als Warnungen gesendet, da die Batterien durch die BMS eigensicher sind, ist eine Abschaltung des SI bei Alarmen des BMS nicht sinnvoll.

Anschließend werden die verarbeiteten Werte für die CAN-Ausgabe formatiert und abgeschickt.

Abschließend wird der Puffer geleert, damit dieser bei abgeschaltetem SI nicht überläuft.
Der gesamte Vorgang wird etwa alle 10s wiederholt. Bleiben am SI für 60s die Daten aus, schaltet sich dieser ab.

Ich habe "siinterjkb.py" in einem eigenen Verzeichnis unter dem Benutzer "pi" abgelegt: /home/pi/SIinterJK/siinterjkp.py

Die Anwendung wird dann nach dem Wechsel is richtige Verzeichnis mit dem Befehl: 
```
sudo python3 siinterjkp.py
```
gestartet.

Im Terminalfenster kann man dann die aktuell vom BMS empfangenen Werte und die an den CAN Bus ausgegebenen Strings verfolgen.
Bei eigenen Anpassungen des Codes kann man hier sehen, ob die Änderungen zum korrekten Ergebnis führen.

Falls jemand eine Idee hat, wie man sich diese Informationen über ein lokales Netzwerk in einem Browser anzeigen lassen kann, so ist er herzlich eingeladen den Code entsprechend zu erweitern und das Ergebnis hier zu teilen.
### Start der Anwendung im Hintergrund
Um sicherzustellen, dass der Code z.B. nach einem Blackout beim Hochfahren des Raspberry Pi automatisch ausgeführt wird und immer 
im Hintergrund läuft, kann man einen Systemd-Service erstellen:
Erstelle eine Datei mit dem Namen my_service.service im Verzeichnis /etc/systemd/system/:
```
sudo nano /etc/systemd/system/my_service.service
```
Füge den folgenden Inhalt in die my_service.service-Datei ein:
```
[Unit]
Description=My Service
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /path/to/your/script.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```
Ersetze /path/to/your/script.py durch den Pfad zu siinterjkp.py. Ich habe siinterjkp z.B. unter: /home/pi/SIinterJK/siinterjkp.py abgespeichert.
Speichere und schließe die Datei.

Aktiviere den Service dann mit dem folgenden Befehl:
```
sudo systemctl enable my_service.service
```
Starte anschließend den Service mit dem folgenden Befehl:
```
sudo systemctl start my_service.service
```
Jetzt wird SIinterJKp automatisch beim Hochfahren des Raspberry Pi gestartet und läuft im Hintergrund.

### Sehr hilfreiche Quellen:
https://github.com/jblance/mpp-solar/issues/112  ab Eintrag vom 18.05.21 werden hier die Befehle an das JK-BMS sowie das Antwortformat beschrieben. (besser als in der Originaldokumentation)

https://github.com/camueller/SmartApplianceEnabler  Tolles Tool zum Messen und Schalten von Verbrauchern in Verbindung mit dem SMA Homemanager 2.0.
