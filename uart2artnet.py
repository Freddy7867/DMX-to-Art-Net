{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 Menlo-Bold;\f1\fnil\fcharset0 Menlo-Regular;}
{\colortbl;\red255\green255\blue255;\red46\green174\blue187;\red0\green0\blue0;\red180\green36\blue25;
\red47\green180\blue29;\red255\green255\blue255;\red64\green11\blue217;\red173\green224\blue24;\red200\green20\blue201;
\red20\green153\blue2;}
{\*\expandedcolortbl;;\cssrgb\c20199\c73241\c78251;\csgray\c0;\cssrgb\c76411\c21697\c12527;
\cssrgb\c20241\c73898\c14950;\csgray\c100000;\cssrgb\c32309\c18666\c88229;\cssrgb\c72966\c88555\c11287;\cssrgb\c83397\c23074\c82666;
\cssrgb\c0\c65000\c0;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0

\f0\b\fs22 \cf2 \CocoaLigature0 import
\f1\b0 \cf3  serial\

\f0\b \cf2 import
\f1\b0 \cf3  socket\

\f0\b \cf2 import
\f1\b0 \cf3  json\

\f0\b \cf2 import
\f1\b0 \cf3  threading\

\f0\b \cf2 import
\f1\b0 \cf3  logging\

\f0\b \cf2 import
\f1\b0 \cf3  time\

\f0\b \cf2 import
\f1\b0 \cf3  subprocess\

\f0\b \cf2 from
\f1\b0 \cf3  flask 
\f0\b \cf2 import
\f1\b0 \cf3  Flask, request, render_template_string\
\

\f0\b \cf4 # Logging
\f1\b0 \cf3 \
logging.basicConfig(filename=
\f0\b \cf5 'uart2artnet.log'
\f1\b0 \cf3 , level=logging.INFO, format=
\f0\b \cf5 '%(asctime)s %(message)s
\f1\b0 \cf6 \cb3 >\cf3 \cb1 \
\

\f0\b \cf4 # Flask Webserver
\f1\b0 \cf3 \
app = Flask(__name__)\
config_path = 
\f0\b \cf5 "config.json"
\f1\b0 \cf3 \
\

\f0\b \cf2 def\cf7  load_config
\f1\b0 \cf3 ():\
    
\f0\b \cf2 with
\f1\b0 \cf3  open(config_path, 
\f0\b \cf5 "r"
\f1\b0 \cf3 ) 
\f0\b \cf2 as
\f1\b0 \cf3  f:\
        
\f0\b \cf2 return
\f1\b0 \cf3  json.load(f)\
\

\f0\b \cf2 def\cf7  save_config
\f1\b0 \cf3 (data):\
    
\f0\b \cf2 with
\f1\b0 \cf3  open(config_path, 
\f0\b \cf5 "w"
\f1\b0 \cf3 ) 
\f0\b \cf2 as
\f1\b0 \cf3  f:\
        json.dump(data, f, indent=2)\
\
config = load_config()\
\

\f0\b \cf4 # Art-Net Sender
\f1\b0 \cf3 \

\f0\b \cf2 def\cf7  send_artnet
\f1\b0 \cf3 (dmx_data):\
    packet = bytearray()\
    packet.extend(b
\f0\b \cf5 'Art-Net
\f1\b0 \cf8 \\x00
\f0\b \cf5 '
\f1\b0 \cf3 ) 
\f0\b \cf4  # Art-Net Header
\f1\b0 \cf3 \
    packet.extend(b
\f0\b \cf5 '
\f1\b0 \cf8 \\x00\\x50
\f0\b \cf5 '
\f1\b0 \cf3 )    
\f0\b \cf4  # OpCode ArtDmx (0x5000)
\f1\b0 \cf3 \
    packet.extend(b
\f0\b \cf5 '
\f1\b0 \cf8 \\x00\\x0e
\f0\b \cf5 '
\f1\b0 \cf3 )    
\f0\b \cf4  # Protocol Version
\f1\b0 \cf3 \
    packet.extend(b
\f0\b \cf5 '
\f1\b0 \cf8 \\x00
\f0\b \cf5 '
\f1\b0 \cf3 )        
\f0\b \cf4  # Sequence
\f1\b0 \cf3 \
    packet.extend(b
\f0\b \cf5 '
\f1\b0 \cf8 \\x00
\f0\b \cf5 '
\f1\b0 \cf3 )        
\f0\b \cf4  # Physical
\f1\b0 \cf3 \
    packet.extend(b
\f0\b \cf5 '
\f1\b0 \cf8 \\x00\\x00
\f0\b \cf5 '
\f1\b0 \cf3 )    
\f0\b \cf4  # Universe
\f1\b0 \cf3 \
    length = len(dmx_data)\
    packet.extend(length.to_bytes(2, 
\f0\b \cf5 'big'
\f1\b0 \cf3 ))\
    packet.extend(dmx_data)\
\
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\
    sock.sendto(packet, (config[
\f0\b \cf5 "ARTNET_IP"
\f1\b0 \cf3 ], config[
\f0\b \cf5 "ARTNET_PORT"
\f1\b0 \cf3 ]))\
    sock.close()\
    logging.info(f
\f0\b \cf5 "Art-Net gesendet: \{dmx_data.hex()\}"
\f1\b0 \cf3 )\
\

\f0\b \cf4 # UART Reader
\f1\b0 \cf3 \

\f0\b \cf2 def\cf7  uart_read_loop
\f1\b0 \cf3 ():\
    
\f0\b \cf2 global
\f1\b0 \cf3  config\
    ser = serial.Serial(config[
\f0\b \cf5 "UART_PORT"
\f1\b0 \cf3 ], config[
\f0\b \cf5 "BAUDRATE"
\f1\b0 \cf3 ], timeout=1)\
    buffer = bytearray()\
    last_values = \{\}\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0
\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0
   
\f0\b \cf4  # START_PATTERN verarbeiten
\f1\b0 \cf3 \
    
\f0\b \cf2 try
\f1\b0 \cf3 :\
        start_pattern = bytes.fromhex(config[
\f0\b \cf5 "START_PATTERN"
\f1\b0 \cf3 ])\
    
\f0\b \cf2 except
\f1\b0 \cf3  Exception 
\f0\b \cf2 as
\f1\b0 \cf3  e:\
        logging.error(f
\f0\b \cf5 "Ung\'fcltiges START_PATTERN: \{e\}"
\f1\b0 \cf3 )\
        
\f0\b \cf2 return
\f1\b0 \cf3 \
\
    
\f0\b \cf2 while
\f1\b0 \cf3  
\f0\b \cf9 True
\f1\b0 \cf3 :\
        byte = ser.read(1)\
        
\f0\b \cf2 if
\f1\b0 \cf3  byte:\
            buffer += byte\
            
\f0\b \cf2 if
\f1\b0 \cf3  start_pattern 
\f0\b \cf2 in
\f1\b0 \cf3  buffer:\
                start_index = buffer.index(start_pattern) + len(start_pattern)\
                
\f0\b \cf2 if
\f1\b0 \cf3  len(buffer) >= start_index + config[
\f0\b \cf5 "FADER_PRO_BLOCK"
\f1\b0 \cf3 ] * config[
\f0\b \cf5 "BLOCKS"
\f1\b0 \cf3 ]:\
                    payload = buffer[start_index:start_index + config[
\f0\b \cf5 "FADER_PRO_BLOCK"
\f1\b0 \cf3 ] * config[
\f0\b \cf5 "
\f1\b0 \cf6 \cb3 >\cf3 \cb1 \
                    buffer = buffer[start_index + config[
\f0\b \cf5 "FADER_PRO_BLOCK"
\f1\b0 \cf3 ] * config[
\f0\b \cf5 "BLOCKS"
\f1\b0 \cf3 ]:]\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0
\cb10                     \cb1 \
                   
\f0\b \cf4  # Nur ge\'e4nderte Werte senden
\f1\b0 \cf3 \
                    changed = 
\f0\b \cf9 False
\f1\b0 \cf3 \
                    
\f0\b \cf2 for
\f1\b0 \cf3  i, val 
\f0\b \cf2 in
\f1\b0 \cf3  enumerate(payload):\
                        
\f0\b \cf2 if
\f1\b0 \cf3  last_values.get(i) != val:\
                            last_values[i] = val\
                            changed = 
\f0\b \cf9 True
\f1\b0 \cf3 \
                    
\f0\b \cf2 if
\f1\b0 \cf3  changed:\
                        send_artnet(payload)\
\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0

\f0\b \cf4 # Web-Konfiguration
\f1\b0 \cf3 \
@app.route(
\f0\b \cf5 "/"
\f1\b0 \cf3 , methods=[
\f0\b \cf5 "GET"
\f1\b0 \cf3 , 
\f0\b \cf5 "POST"
\f1\b0 \cf3 ])\

\f0\b \cf2 def\cf7  config_page
\f1\b0 \cf3 ():\
    
\f0\b \cf2 if
\f1\b0 \cf3  request.method == 
\f0\b \cf5 "POST"
\f1\b0 \cf3 :\
        
\f0\b \cf2 try
\f1\b0 \cf3 :\
            new_config = \{\
                
\f0\b \cf5 "UART_PORT"
\f1\b0 \cf3 : request.form[
\f0\b \cf5 "UART_PORT"
\f1\b0 \cf3 ],\
                
\f0\b \cf5 "BAUDRATE"
\f1\b0 \cf3 : int(request.form[
\f0\b \cf5 "BAUDRATE"
\f1\b0 \cf3 ]),\
                
\f0\b \cf5 "ARTNET_PORT"
\f1\b0 \cf3 : int(request.form[
\f0\b \cf5 "ARTNET_PORT"
\f1\b0 \cf3 ]),\
                
\f0\b \cf5 "ARTNET_IP"
\f1\b0 \cf3 : request.form[
\f0\b \cf5 "ARTNET_IP"
\f1\b0 \cf3 ],\
                
\f0\b \cf5 "FADER_PRO_BLOCK"
\f1\b0 \cf3 : int(request.form[
\f0\b \cf5 "FADER_PRO_BLOCK"
\f1\b0 \cf3 ]),\
                
\f0\b \cf5 "BLOCKS"
\f1\b0 \cf3 : int(request.form[
\f0\b \cf5 "BLOCKS"
\f1\b0 \cf3 ]),\
                
\f0\b \cf5 "START_PATTERN"
\f1\b0 \cf3 : request.form[
\f0\b \cf5 "START_PATTERN"
\f1\b0 \cf3 ].strip().lower()\
            \}\
            save_config(new_config)\
            
\f0\b \cf2 return
\f1\b0 \cf3  
\f0\b \cf5 "<h2>\uc0\u9989  Konfiguration gespeichert.</h2><a href='/'>Zur\'fcck</a>"
\f1\b0 \cf3 \
        
\f0\b \cf2 except
\f1\b0 \cf3  Exception 
\f0\b \cf2 as
\f1\b0 \cf3  e:\
            logging.error(f
\f0\b \cf5 "Fehler beim Speichern der Konfiguration: \{e\}"
\f1\b0 \cf3 )\
            
\f0\b \cf2 return
\f1\b0 \cf3  f
\f0\b \cf5 "<h2>\uc0\u10060  Fehler beim Speichern: \{e\}</h2><a href='/'>Zur\'fcck</a>"
\f1\b0 \cf3 \
\
    
\f0\b \cf2 return
\f1\b0 \cf3  render_template_string(
\f0\b \cf5 """
\f1\b0 \cf3 \

\f0\b \cf5         <h2>UART to Art-Net Konfiguration</h2>
\f1\b0 \cf3 \

\f0\b \cf5         <form method="post">
\f1\b0 \cf3 \

\f0\b \cf5             <label>UART Port:</label><br>
\f1\b0 \cf3 \

\f0\b \cf5             <input name="UART_PORT" value="\{\{config.UART_PORT\}\}"><br><br>
\f1\b0 \cf3 \

\f0\b \cf5             <label>Baudrate:</label><br>
\f1\b0 \cf3 \

\f0\b \cf5             <input name="BAUDRATE" value="\{\{config.BAUDRATE\}\}"><br><br>
\f1\b0 \cf3 \

\f0\b \cf5             <label>Art-Net IP:</label><br>
\f1\b0 \cf3 \

\f0\b \cf5             <input name="ARTNET_IP" value="\{\{config.ARTNET_IP\}\}"><br><br>
\f1\b0 \cf3 \

\f0\b \cf5             <label>Art-Net Port:</label><br>
\f1\b0 \cf3 \

\f0\b \cf5             <input name="ARTNET_PORT" value="\{\{config.ARTNET_PORT\}\}"><br><br>
\f1\b0 \cf3 \

\f0\b \cf5             <label>Fader pro Block:</label><br>
\f1\b0 \cf3 \

\f0\b \cf5             <input name="FADER_PRO_BLOCK" value="\{\{config.FADER_PRO_BLOCK\}\}"><br><br>
\f1\b0 \cf3 \

\f0\b \cf5             <label>Anzahl Bl\'f6cke:</label><br>
\f1\b0 \cf3 \

\f0\b \cf5             <input name="BLOCKS" value="\{\{config.BLOCKS\}\}"><br><br>
\f1\b0 \cf3 \

\f0\b \cf5             <label>Startmuster (Hex ohne Leerzeichen, z.B. 00000000e000):</label><br>
\f1\b0 \cf3 \

\f0\b \cf5             <input name="START_PATTERN" value="\{\{config.START_PATTERN\}\}"><br><br>
\f1\b0 \cf3 \

\f0\b \cf5             <button type="submit">\uc0\u55357 \u56510  Speichern</button>
\f1\b0 \cf3 \

\f0\b \cf5         </form>
\f1\b0 \cf3 \

\f0\b \cf5         <hr>
\f1\b0 \cf3 \

\f0\b \cf5         <form action="/restart" method="post">
\f1\b0 \cf3 \

\f0\b \cf5             <button type="submit" style="background-color:red; color:white;">\uc0\u55357 \u56580  Neustart Service</b
\f1\b0 \cf6 \cb3 >\cf3 \cb1 \

\f0\b \cf5         </form>
\f1\b0 \cf3 \

\f0\b \cf5     """
\f1\b0 \cf3 , config=config)\
\

\f0\b \cf4 # Service-Neustart
\f1\b0 \cf3 \
@app.route(
\f0\b \cf5 "/restart"
\f1\b0 \cf3 , methods=[
\f0\b \cf5 "POST"
\f1\b0 \cf3 ])\

\f0\b \cf2 def\cf7  restart_service
\f1\b0 \cf3 ():\
    
\f0\b \cf2 try
\f1\b0 \cf3 :\
        subprocess.run([
\f0\b \cf5 "sudo"
\f1\b0 \cf3 , 
\f0\b \cf5 "systemctl"
\f1\b0 \cf3 , 
\f0\b \cf5 "restart"
\f1\b0 \cf3 , 
\f0\b \cf5 "uart2artnet.service"
\f1\b0 \cf3 ], check=
\f0\b \cf9 True
\f1\b0 \cf3 )\
        
\f0\b \cf2 return
\f1\b0 \cf3  
\f0\b \cf5 "<h2>\uc0\u55357 \u56580  Service wurde neu gestartet.</h2><a href='/'>Zur\'fcck</a>"
\f1\b0 \cf3 \
    
\f0\b \cf2 except
\f1\b0 \cf3  subprocess.CalledProcessError 
\f0\b \cf2 as
\f1\b0 \cf3  e:\
        logging.error(f
\f0\b \cf5 "Fehler beim Neustart: \{e\}"
\f1\b0 \cf3 )\
        
\f0\b \cf2 return
\f1\b0 \cf3  f
\f0\b \cf5 "<h2>\uc0\u10060  Fehler beim Neustart: \{e\}</h2><a href='/'>Zur\'fcck</a>"
\f1\b0 \cf3 \
\

\f0\b \cf4 # Hintergrund-Thread starten
\f1\b0 \cf3 \

\f0\b \cf2 def\cf7  start_uart_thread
\f1\b0 \cf3 ():\
    thread = threading.Thread(target=uart_read_loop, daemon=
\f0\b \cf9 True
\f1\b0 \cf3 )\
    thread.start()\
\

\f0\b \cf2 if
\f1\b0 \cf3  __name__ == 
\f0\b \cf5 "__main__"
\f1\b0 \cf3 :\
    start_uart_thread()\
    app.run(host=
\f0\b \cf5 "0.0.0.0"
\f1\b0 \cf3 , port=8080)\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\cf6 \cb3   }