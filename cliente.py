import socket
import pickle
import struct
import cv2
import configparser

# Configuración del archivo INI
config = configparser.ConfigParser()
config.read('config.ini')

# Carga la IP y el puerto desde el archivo de configuración
ip = config.get('network', 'ip')
port = config.getint('network', 'port')

# Configuración del cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Intentar conectar al servidor con la IP y el puerto del archivo de configuración
    print(f"Conectando al servidor en {ip}:{port}...")
    client_socket.connect((ip, port))
    print("Conectado exitosamente al servidor.")
except socket.error as e:
    print(f"No se pudo conectar al servidor: {e}")
    exit()

def request_screenshot():
    try:
        print("Solicitando captura de pantalla al servidor...")
        client_socket.send("SEND_SCREENSHOT".encode('utf-8'))

        # Recibir tamaño del mensaje
        data = b""
        payload_size = struct.calcsize("Q")
        while len(data) < payload_size:
            packet = client_socket.recv(4 * 1024)
            if not packet:
                return None
            data += packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        # Recibir y decodificar la imagen
        while len(data) < msg_size:
            data += client_socket.recv(4 * 1024)
        frame_data = data[:msg_size]
        frame = pickle.loads(frame_data)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        print("Imagen recibida correctamente.")
        return frame

    except Exception as e:
        print(f"Error al recibir la captura: {e}")
        return None

def capture_screen():
    print("Presiona 'c' para capturar pantalla, 'q' para salir.")
    while True:
        key = input("Presiona 'c' o 'q': ").strip().lower()
        if key == 'c':
            frame = request_screenshot()
            if frame is not None:
                cv2.imshow("Escritorio remoto", frame)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                print("No se pudo obtener la captura.")
        elif key == 'q':
            print("Saliendo...")
            break

    client_socket.close()

capture_screen()
