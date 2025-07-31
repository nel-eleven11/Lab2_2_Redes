import socket
import sys
import math

# CAPA DE APLICACIÓN
def mostrar_mensaje(mensaje, error=False):
    if error:
        print("ERROR: No fue posible recuperar el mensaje original.")
    else:
        print(f"Mensaje recibido y verificado: \"{mensaje}\"")

# CAPA DE PRESENTACIÓN
def decodificar_mensaje(binario):
    chars = []
    for i in range(0, len(binario), 7):
        seven_bits = binario[i:i+7]
        if len(seven_bits) == 7:
            chars.append(chr(int(seven_bits, 2)))
    
    resultado = ''.join(chars)
    print(f"[PRESENTATION] Decoded 7-bit ASCII message: \"{resultado}\"")
    return resultado

# CAPA DE ENLACE - Algoritmo de Hamming
def verificar_integridad(hamming_code):
    print(f"[LINK] Received Hamming code: \"{hamming_code}\"")
    
    if not hamming_code:
        return None, True
    
    # Convert to list of integers
    bits = [int(b) for b in hamming_code]
    total_bits = len(bits)
    
    # Calculate number of parity bits
    parity_bits = 0
    while (1 << parity_bits) < total_bits + 1:
        parity_bits += 1
    
    # Create 1-indexed array
    hamming = [0] + bits
    
    # Calculate syndrome
    syndrome = 0
    for i in range(parity_bits):
        parity_pos = 1 << i
        parity = 0
        
        for j in range(1, total_bits + 1):
            if (j & parity_pos) != 0:
                parity ^= hamming[j]
        
        if parity != 0:
            syndrome += parity_pos
    
    # Check for errors
    if syndrome == 0:
        print("[LINK] No errors detected")
        return extraer_datos(hamming[1:]), False
    elif syndrome <= total_bits:
        print(f"[LINK] Single bit error detected at position {syndrome}, correcting...")
        # Correct the error
        hamming[syndrome] = 1 - hamming[syndrome]
        return extraer_datos(hamming[1:]), False
    else:
        print("[LINK] Multiple bit errors detected - uncorrectable")
        return None, True

def extraer_datos(hamming_bits):
    datos = []
    for i in range(1, len(hamming_bits) + 1):
        if not es_potencia_de_2(i):
            if i - 1 < len(hamming_bits):
                datos.append(str(hamming_bits[i - 1]))
    
    return ''.join(datos)

def es_potencia_de_2(n):
    return n > 0 and (n & (n - 1)) == 0

def corregir_mensaje(datos_corregidos):
    if datos_corregidos is None:
        return None
    
    print(f"[LINK] Corrected data bits: \"{datos_corregidos}\"")
    return datos_corregidos

# CAPA DE TRANSMISIÓN
def recibir_informacion():
    host = '127.0.0.1'
    port = 5000
    
    print(f"[TRANSMISSION] Esperando datos en {host}:{port}...")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            print("[TRANSMISSION] Servidor listo, esperando conexiones...")
            
            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"[TRANSMISSION] Conexión establecida desde {addr}")
                    data = b""
                    while True:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                    
                    if data:
                        trama = data.decode()
                        print(f"[TRANSMISSION] Trama recibida: \"{trama}\"")
                        
                        # Procesar a través de las capas
                        procesar_trama(trama)
                    
                    # Continue listening for more connections
                    
    except KeyboardInterrupt:
        print("\n[TRANSMISSION] Receptor detenido por el usuario")
    except Exception as e:
        print(f"[TRANSMISSION] Error: {e}")

def procesar_trama(trama):
    # 3. CAPA DE ENLACE: Verificar integridad
    datos_corregidos, hay_error = verificar_integridad(trama)
    
    if hay_error:
        # 1. CAPA DE APLICACIÓN: Mostrar error
        mostrar_mensaje("", error=True)
        return
    
    # Corregir mensaje si es necesario
    datos_finales = corregir_mensaje(datos_corregidos)
    
    if datos_finales is None:
        mostrar_mensaje("", error=True)
        return
    
    # 2. CAPA DE PRESENTACIÓN: Decodificar mensaje
    try:
        mensaje_ascii = decodificar_mensaje(datos_finales)
        
        # 1. CAPA DE APLICACIÓN: Mostrar mensaje
        mostrar_mensaje(mensaje_ascii)
        
    except Exception as e:
        print(f"[PRESENTATION] Error decodificando mensaje: {e}")
        mostrar_mensaje("", error=True)

def main():
    print("=== RECEPTOR - Algoritmo de Hamming ===")
    print("Presione Ctrl+C para detener el receptor")
    
    # CAPA DE TRANSMISIÓN: Recibir información
    recibir_informacion()

if __name__ == "__main__":
    main()
