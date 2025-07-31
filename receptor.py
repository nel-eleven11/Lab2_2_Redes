import socket

# --- ENLACE ---
def fletcher16_binstr(data):
    c1, c2 = 0, 0
    for bit in data:
        val = 1 if bit == '1' else 0
        c1 = (c1 + val) % 255
        c2 = (c2 + c1) % 255
    return c1, c2

# --- PRESENTACIÓN ---
def binario_a_ascii(binario):
    chars = []
    for i in range(0, len(binario), 8):
        byte = binario[i:i+8]
        if len(byte) < 8:
            continue  # Salta bytes incompletos
        chars.append(chr(int(byte, 2)))
    return ''.join(chars)

# --- APLICACIÓN ---
def mostrar_mensaje(mensaje, error=False):
    if error:
        print("ERROR: No fue posible recuperar el mensaje original.")
    else:
        print("Mensaje recibido y verificado:", mensaje)

# --- TRANSMISIÓN ---
def receptor():
    host = '127.0.0.1'
    port = 5000

    print(f"[TRANSMISIÓN] Esperando datos en {host}:{port}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"[TRANSMISIÓN] Conexión establecida desde {addr}")
            data = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
            trama = data.decode()
            print(f"[TRANSMISIÓN] Trama recibida: {trama}")

    # --- ENLACE: Separar mensaje y checksum ---
    if len(trama) < 16:
        mostrar_mensaje("", error=True)
        return
    mensaje_bin = trama[:-16]
    c1_recv = int(trama[-16:-8], 2)
    c2_recv = int(trama[-8:], 2)
    c1, c2 = fletcher16_binstr(mensaje_bin)

    if (c1, c2) == (c1_recv, c2_recv):
        # --- PRESENTACIÓN: Decodifica el mensaje ---
        mensaje_ascii = binario_a_ascii(mensaje_bin)
        mostrar_mensaje(mensaje_ascii)
    else:
        mostrar_mensaje("", error=True)

if __name__ == "__main__":
    receptor()
