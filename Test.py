import serial

def main():
    port = '/dev/serial0'   # UART Port auf Raspberry Pi
    baudrate = 250000       # Übliche Baudrate, anpassen je nach Setup

    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Verbunden mit {port} @ {baudrate} Baud.")
    except serial.SerialException as e:
        print(f"Fehler beim Öffnen des Ports: {e}")
        return

    buffer = bytearray()

    try:
        while True:
            data = ser.read(512 - len(buffer))
            if data:
                buffer.extend(data)

                if len(buffer) >= 512:
                    print("=== Paket (512 Bytes) ===")
                    print(buffer[:512].hex(' ', 1))
                    print()
                    buffer = buffer[512:]
    except KeyboardInterrupt:
        print("Beendet vom Benutzer")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
