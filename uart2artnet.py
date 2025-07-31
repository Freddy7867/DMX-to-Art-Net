import serial
import socket
import json
import threading
import logging
import time
import subprocess
from flask import Flask, request, render_template_string

# Logging
logging.basicConfig(filename='uart2artnet.log', level=logging.INFO, format='%(asctime)s %(message)s>

# Flask Webserver
app = Flask(__name__)
config_path = "config.json"

def load_config():
    with open(config_path, "r") as f:
        return json.load(f)

def save_config(data):
    with open(config_path, "w") as f:
        json.dump(data, f, indent=2)

config = load_config()

# Art-Net Sender
def send_artnet(dmx_data):
    packet = bytearray()
    packet.extend(b'Art-Net\x00')  # Art-Net Header
    packet.extend(b'\x00\x50')     # OpCode ArtDmx (0x5000)
    packet.extend(b'\x00\x0e')     # Protocol Version
    packet.extend(b'\x00')         # Sequence
    packet.extend(b'\x00')         # Physical
    packet.extend(b'\x00\x00')     # Universe
    length = len(dmx_data)
    packet.extend(length.to_bytes(2, 'big'))
    packet.extend(dmx_data)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(packet, (config["ARTNET_IP"], config["ARTNET_PORT"]))
    sock.close()
    logging.info(f"Art-Net gesendet: {dmx_data.hex()}")

# UART Reader
def uart_read_loop():
    global config
    ser = serial.Serial(config["UART_PORT"], config["BAUDRATE"], timeout=1)
    buffer = bytearray()
    last_values = {}

    # START_PATTERN verarbeiten
    try:
        start_pattern = bytes.fromhex(config["START_PATTERN"])
    except Exception as e:
        logging.error(f"Ungültiges START_PATTERN: {e}")
        return

    while True:
        byte = ser.read(1)
        if byte:
            buffer += byte
            if start_pattern in buffer:
                start_index = buffer.index(start_pattern) + len(start_pattern)
                if len(buffer) >= start_index + config["FADER_PRO_BLOCK"] * config["BLOCKS"]:
                    payload = buffer[start_index:start_index + config["FADER_PRO_BLOCK"] * config[">
                    buffer = buffer[start_index + config["FADER_PRO_BLOCK"] * config["BLOCKS"]:]
                    
                    # Nur geänderte Werte senden
                    changed = False
                    for i, val in enumerate(payload):
                        if last_values.get(i) != val:
                            last_values[i] = val
                            changed = True
                    if changed:
                        send_artnet(payload)

# Web-Konfiguration
@app.route("/", methods=["GET", "POST"])
def config_page():
    if request.method == "POST":
        try:
            new_config = {
                "UART_PORT": request.form["UART_PORT"],
                "BAUDRATE": int(request.form["BAUDRATE"]),
                "ARTNET_PORT": int(request.form["ARTNET_PORT"]),
                "ARTNET_IP": request.form["ARTNET_IP"],
                "FADER_PRO_BLOCK": int(request.form["FADER_PRO_BLOCK"]),
                "BLOCKS": int(request.form["BLOCKS"]),
                "START_PATTERN": request.form["START_PATTERN"].strip().lower()
            }
            save_config(new_config)
            return "<h2>✅ Konfiguration gespeichert.</h2><a href='/'>Zurück</a>"
        except Exception as e:
            logging.error(f"Fehler beim Speichern der Konfiguration: {e}")
            return f"<h2>❌ Fehler beim Speichern: {e}</h2><a href='/'>Zurück</a>"

    return render_template_string("""
        <h2>UART to Art-Net Konfiguration</h2>
        <form method="post">
            <label>UART Port:</label><br>
            <input name="UART_PORT" value="{{config.UART_PORT}}"><br><br>
            <label>Baudrate:</label><br>
            <input name="BAUDRATE" value="{{config.BAUDRATE}}"><br><br>
            <label>Art-Net IP:</label><br>
            <input name="ARTNET_IP" value="{{config.ARTNET_IP}}"><br><br>
            <label>Art-Net Port:</label><br>
            <input name="ARTNET_PORT" value="{{config.ARTNET_PORT}}"><br><br>
            <label>Fader pro Block:</label><br>
            <input name="FADER_PRO_BLOCK" value="{{config.FADER_PRO_BLOCK}}"><br><br>
            <label>Anzahl Blöcke:</label><br>
            <input name="BLOCKS" value="{{config.BLOCKS}}"><br><br>
            <label>Startmuster (Hex ohne Leerzeichen, z.B. 00000000e000):</label><br>
            <input name="START_PATTERN" value="{{config.START_PATTERN}}"><br><br>
            <button type="submit">💾 Speichern</button>
        </form>
        <hr>
        <form action="/restart" method="post">
            <button type="submit" style="background-color:red; color:white;">🔄 Neustart Service</b>
        </form>
    """, config=config)

# Service-Neustart
@app.route("/restart", methods=["POST"])
def restart_service():
    try:
        subprocess.run(["sudo", "systemctl", "restart", "uart2artnet.service"], check=True)
        return "<h2>🔄 Service wurde neu gestartet.</h2><a href='/'>Zurück</a>"
    except subprocess.CalledProcessError as e:
        logging.error(f"Fehler beim Neustart: {e}")
        return f"<h2>❌ Fehler beim Neustart: {e}</h2><a href='/'>Zurück</a>"

# Hintergrund-Thread starten
def start_uart_thread():
    thread = threading.Thread(target=uart_read_loop, daemon=True)
    thread.start()

if __name__ == "__main__":
    start_uart_thread()
    app.run(host="0.0.0.0", port=8080)
