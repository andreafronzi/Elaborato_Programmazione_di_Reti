# Corso di Programmazione di Reti - Laboratorio - Università di Bologna
# Socket_Programming_Assignment - WebServer - Versione migliorata
# Combina robustezza e semplicità

import sys
import os
from socket import *

# Configurazione server
serverPort = 8080
address = '127.0.0.1'
serverSocket = socket(AF_INET, SOCK_STREAM)
server_address = (address, serverPort)
serverSocket.bind(server_address)
serverSocket.listen(1)
print(f" The web server is up on http://{address}:{serverPort}")

# Funzione per determinare il MIME type del file
def get_mime_type(filename):
    if filename.endswith('.html'):
        return 'text/html'
    elif filename.endswith('.css'):
        return 'text/css'
    elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        return 'image/jpeg'
    elif filename.endswith('.png'):
        return 'image/png'
    elif filename.endswith('.ico'):
        return 'image/x-icon'
    else:
        return 'application/octet-stream'  # default binario

while True:
    print(" Waiting for a connection...")
    connectionSocket, addr = serverSocket.accept()
    print(f" Connessione stabilita da: {addr}")

    try:
        # riceve richiesta dal client
        message = connectionSocket.recv(4096)

        if not message:
            connectionSocket.close()
            continue

        parts = message.split()
        if len(parts) > 1:
            method = parts[0].decode(errors='replace')
            path = parts[1].decode(errors='replace')

            print(f" Richiesta ricevuta: {method} {path}")

            # percorso del file richiesto dentro www/
            filepath = os.path.join("www", path.lstrip("/"))

            # se la richiesta è alla root, manda index.html
            if path == "/":
                filepath = os.path.join("www", "index.html")

            # determina MIME type
            mime_type = get_mime_type(filepath)

            # apertura corretta (testo o binario)
            mode = "rb" if mime_type.startswith("image/") else "r"
            with open(filepath, mode) as f:
                outputdata = f.read()

            # invio header + contenuto
            header = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\n\r\n"
            connectionSocket.send(header.encode())

            if mode == "rb":
                connectionSocket.send(outputdata)
            else:
                connectionSocket.send(outputdata.encode())

            connectionSocket.send(b"\r\n")
            connectionSocket.close()

            print(f" Risposta inviata con successo: {filepath}")

    except IOError:
        # file non trovato
        error_msg = "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n"
        connectionSocket.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
        connectionSocket.send(error_msg.encode())
        connectionSocket.close()

        print(f" File non trovato: {path}")
