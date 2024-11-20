import socket
import pickle
import struct
import cv2
import configparser
import pyautogui
import numpy as np

# Configuración del archivo INI
config = configparser.ConfigParser()
config.read('config.ini')

# Carga la IP y el puerto desde el archivo de configuración
ip = config.get('network', 'ip')
port = config.getint('network', 'port')

# Configuración del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((ip, port))
server_socket.listen(5)
print(f"Servidor escuchando en {ip}:{port}")

def send_screenshot(conn):
    # Capturar la pantalla en tiempo real usando pyautogui
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Codificar la imagen como JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    data = pickle.dumps(buffer)
    msg_size = struct.pack("Q", len(data))

    # Enviar el tamaño de los datos seguido de los datos mismos
    conn.sendall(msg_size + data)
    print("Captura enviada al cliente.")

while True:
    conn, addr = server_socket.accept()
    print(f"Conexión establecida con {addr}")

    try:
        # Esperar la solicitud del cliente
        request = conn.recv(1024).decode('utf-8')
        if request == "SEND_SCREENSHOT":
            send_screenshot(conn)
        else:
            print("Solicitud desconocida.")
    except Exception as e:
        print(f"Error durante la comunicación: {e}")
    finally:
        conn.close()
