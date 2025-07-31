Dieses Projekt ermöglicht es, DMX-Daten von analogen DMX-512-3-Pin-Pulten einzulesen und über Art-Net z. B. in QLC+ zu importieren.
(Aktuell getestet auf einem Raspberry Pi 3B+ mit einem MAX485-Modul. Getestet wurden 16 Kanäle mit Unterstützung von Fadern.
Über die Weboberfläche lassen sich weitere Einstellungen vornehmen – diese sind jedoch bisher noch nicht vollständig getestet.)

Die Konfiguration kann bequem über eine integrierte Weboberfläche erfolgen.

# Verwendete Hardware
Raspberry Pi 3B+
MAX485-Modul (z. B. via AliExpress)
XLR-Einbaubuchse (z. B. via AliExpress)
Lüfter zur Kühlung des Raspberry Pi
und ein 3D Druck Case 

# Verwendete Software
Raspberry Pi OS Lite
Python 3
Flask (für die Weboberfläche)
pyserial (für die UART-Kommunikation)
systemd (für den Autostart des Services)
Konfiguration der UART-Schnittstelle per sudo raspi-config:
Login: Nein
Schnittstelle: Ja
Midnight Commander (mc) zur Dateiverwaltung und Rechtevergabe

# Installation der benötigten Software
sudo apt update
sudo apt install python3 python3-pip
sudo apt install python3-flask python3-serial
sudo apt install mc
Systemd-Service aktivieren

# Software als Service Hinzufügen 
sudo cp uart2artnet.service /etc/systemd/system/
sudo systemctl daemon-reexec
sudo systemctl enable uart2artnet.service
sudo systemctl start uart2artnet.service
 
# Konfiguration der config.json
Stelle mit mc sicher, dass die Datei config.json für alle Benutzer les- und schreibbar ist.
(Du kannst z. B. im Midnight Commander F9 → Datei → Rechte ändern auswählen.)


