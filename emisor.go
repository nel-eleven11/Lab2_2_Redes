package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"net"
	"os"
	"strconv"
	"strings"
	"time"
)

// CAPA DE APLICACIÓN
func solicitarMensaje() (string, float64) {
	reader := bufio.NewReader(os.Stdin)
	
	fmt.Print("Ingrese el mensaje de texto: ")
	mensaje, _ := reader.ReadString('\n')
	mensaje = strings.TrimSpace(mensaje)
	
	fmt.Print("Ingrese la tasa de error (ejemplo 0.01 para 1%): ")
	errorStr, _ := reader.ReadString('\n')
	errorStr = strings.TrimSpace(errorStr)
	tasaError, _ := strconv.ParseFloat(errorStr, 64)
	
	fmt.Printf("[APPLICATION] Message: \"%s\"\n", mensaje)
	return mensaje, tasaError
}

// CAPA DE PRESENTACIÓN
func codificarMensaje(mensaje string) string {
	var binario strings.Builder
	
	for _, char := range mensaje {
		for i := 7; i >= 0; i-- {
			bit := (int(char) >> i) & 1
			binario.WriteString(strconv.Itoa(bit))
		}
	}
	
	resultado := binario.String()
	fmt.Printf("[PRESENTATION] ASCII Binary: \"%s\"\n", resultado)
	return resultado
}

// CAPA DE ENLACE - Algoritmo de Hamming
func calcularIntegridad(datos string) string {
	dataBits := len(datos)
	
	// Calcular número de bits de paridad necesarios
	parityBits := 0
	for (1 << parityBits) < (dataBits + parityBits + 1) {
		parityBits++
	}
	
	totalBits := dataBits + parityBits
	hamming := make([]int, totalBits+1) // 1-indexed
	
	// Colocar bits de datos en posiciones que no son potencias de 2
	dataIndex := 0
	for i := 1; i <= totalBits; i++ {
		if !esPotenciaDe2(i) {
			if dataIndex < len(datos) {
				hamming[i] = int(datos[dataIndex] - '0')
				dataIndex++
			}
		}
	}
	
	// Calcular bits de paridad
	for i := 0; i < parityBits; i++ {
		parityPos := 1 << i
		parity := 0
		
		for j := 1; j <= totalBits; j++ {
			if (j & parityPos) != 0 {
				parity ^= hamming[j]
			}
		}
		
		hamming[parityPos] = parity
	}
	
	// Convertir a string
	var resultado strings.Builder
	for i := 1; i <= totalBits; i++ {
		resultado.WriteString(strconv.Itoa(hamming[i]))
	}
	
	hammingStr := resultado.String()
	fmt.Printf("[LINK] With Hamming: \"%s\"\n", hammingStr)
	return hammingStr
}

func esPotenciaDe2(n int) bool {
	return n > 0 && (n&(n-1)) == 0
}

// CAPA DE RUIDO
func aplicarRuido(trama string, tasaError float64) string {
	rand.Seed(time.Now().UnixNano())
	bits := []rune(trama)
	
	erroresAplicados := 0
	for i := range bits {
		if rand.Float64() < tasaError {
			if bits[i] == '1' {
				bits[i] = '0'
			} else {
				bits[i] = '1'
			}
			erroresAplicados++
		}
	}
	
	resultado := string(bits)
	fmt.Printf("[NOISE] After noise (error rate %.3f, %d errors applied): \"%s\"\n", 
		tasaError, erroresAplicados, resultado)
	return resultado
}

// CAPA DE TRANSMISIÓN
func enviarInformacion(trama string) {
	fmt.Println("[TRANSMISSION] Sending via socket...")
	
	conn, err := net.Dial("tcp", "127.0.0.1:5000")
	if err != nil {
		fmt.Printf("Error conectando al receptor: %v\n", err)
		return
	}
	defer conn.Close()
	
	_, err = conn.Write([]byte(trama))
	if err != nil {
		fmt.Printf("Error enviando datos: %v\n", err)
		return
	}
	
	fmt.Println("Mensaje enviado correctamente!")
}

func main() {
	fmt.Println("=== EMISOR - Algoritmo de Hamming ===")
	
	// 1. CAPA DE APLICACIÓN
	mensaje, tasaError := solicitarMensaje()
	
	// 2. CAPA DE PRESENTACIÓN
	binario := codificarMensaje(mensaje)
	
	// 3. CAPA DE ENLACE
	hammingCode := calcularIntegridad(binario)
	
	// 4. CAPA DE RUIDO
	tramaConRuido := aplicarRuido(hammingCode, tasaError)
	
	// 5. CAPA DE TRANSMISIÓN
	enviarInformacion(tramaConRuido)
}
