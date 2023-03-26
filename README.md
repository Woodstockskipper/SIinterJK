# SIinterJK
## Interface zur Übertragung der Daten von RS485 JK-BMS t zum SMA Sunny Island CAN
### Vorgeschichte
Seit etwa einem Jahr besitze ich eine selbst gebaute LiFePo4 Batterie zur Zwischenspeicherung meiner PV-Energie. Die Batterie besteht aus vier parallel geschalteten Blöcken mit je 7 kWh Kapazität. Jeder Block von 16 in Reihe geschalteten 3,2V Zellen wird mit einem Batteriemanagementsystem (BMS), Typ JiKong BD6A20S-10P, überwacht und aktiv balanciert.
Als Batterieumrichter benutze ich den Sunny Island 6.0 (SI) von SMA. Dieser besitzt zwei Betriebsmodi: 1) für Litium Batterien mit einem eigenen BMS und CAN-Bus Kommunikation mit dem SI und 2) für Bleibatterien, für die er entsprechende Lade- und Entladeprogramme besitzt.
Da das BMS von JK über eine RS485 Schnittstelle verfügt, die natürlich nicht mit dem SI interagiert, habe ich meine LiFePo4 Batterie im Modus für Bleibatterien am SI betrieben, was funktioniert, jedoch wird nur etwa 50% der Batteriekapazität genutzt. Die Bleibatterie hat eine relativ linearen Verlauf der Kapazität über der Spannung, wodurch der SI die Bleibatterie sehr gut managen kann und der SOC (State Of Charge) gut bestimmt wird. Da jedoch die LiFePo4 Batterien über 85% ihrer Kapazität bei etwa 3,2V verharren, kommt es zu der fehlerhaften SOC Berechnung des SI und der eingeschränkten Kapazitätsnutzung.
Daher reifte der Wunsch heran einen Adapter zwischen der RS485 Schnittstelle des JK BMS und dem CAN Anschluss des SI zu bauen.
### Hardware
Da ich ein wenig Vorkenntnisse im Betrieb von Raspberry Pi habe, lag es nahe den auch für diese Aufgabe zu verwenden. So besorgte ich mir einen Raspberry Pi 3B (2B und 3A funktionieren ebenfalls), den RS485/CAN Hat von WaveShare und den passenden RS485 Adapter von JiKong, wobei bei letzterem darauf geachtet werden muss, dass dieser zum BMS Typ passt. Daher bei Bestellung unbedingt den BMS Typen angeben!
Dann RS485 Adapter an den GPS-Anschluss des BMS anschließen (möglichst spannungsfrei, die Dinger sind sehr empfindlich!) Dann die gelbe Ader des freien Endes an Anschluss A des HATs und Die weiße Ader an Anschluss B des Hats.
Anschließend ein CAT5 Kabel mit RJ45 Stecker....



work in progress....
