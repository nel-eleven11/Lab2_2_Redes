#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>

#define MAX_MSG_LEN 256

// --- CAPA DE PRESENTACIÓN: ASCII -> binario ---
void ascii_a_binario(const char *msg, char *binario) {
    int k = 0;
    for (int i = 0; msg[i] != '\0'; i++) {
        for (int j = 7; j >= 0; j--) {
            binario[k++] = ((msg[i] >> j) & 1) ? '1' : '0';
        }
    }
    binario[k] = '\0';
}

// --- CAPA DE ENLACE: Checksum ---
void fletcher16(const char *data, int len, uint16_t *c1, uint16_t *c2) {
    *c1 = 0;
    *c2 = 0;
    // Convierte los bytes de '0'/'1' a 0/1 numérico para checksum.
    for (int i = 0; i < len; i++) {
        uint8_t val = data[i] == '1' ? 1 : 0;
        *c1 = (*c1 + val) % 255;
        *c2 = (*c2 + *c1) % 255;
    }
}

// --- CAPA DE RUIDO ---
void aplicar_ruido(char *trama, double tasa_error) {
    int len = strlen(trama);
    srand((unsigned int) time(NULL));
    for (int i = 0; i < len; i++) {
        double r = rand() / (RAND_MAX + 1.0);
        if (r < tasa_error) {
            trama[i] = (trama[i] == '1') ? '0' : '1'; // Flip bit
        }
    }
}

// --- CAPA DE APLICACIÓN ---
void solicitar_mensaje(char *mensaje, double *tasa_error) {
    printf("Ingrese el mensaje de texto: ");
    fgets(mensaje, MAX_MSG_LEN, stdin);
    mensaje[strcspn(mensaje, "\n")] = 0; // Quita el salto de línea
    printf("Ingrese la tasa de error (ejemplo 0.01 para 1%%): ");
    scanf("%lf", tasa_error);
    getchar(); // Limpia el buffer
}

int main() {
    char mensaje[MAX_MSG_LEN];
    double tasa_error;
    solicitar_mensaje(mensaje, &tasa_error);

    // PRESENTACIÓN
    char binario[MAX_MSG_LEN * 8 + 1];
    ascii_a_binario(mensaje, binario);
    printf("Mensaje en binario (ASCII): %s\n", binario);

    // ENLACE
    uint16_t c1, c2;
    fletcher16(binario, strlen(binario), &c1, &c2);

    // Convierte checksum a binario de 8 bits c/u
    char checksum[17];
    for (int i = 7; i >= 0; i--) checksum[7-i] = ((c1 >> i) & 1) ? '1' : '0';
    for (int i = 7; i >= 0; i--) checksum[15-i] = ((c2 >> i) & 1) ? '1' : '0';
    checksum[16] = '\0';

    char trama[MAX_MSG_LEN * 8 + 17];
    strcpy(trama, binario);
    strcat(trama, checksum);

    printf("Trama + checksum: %s\n", trama);

    // RUIDO
    aplicar_ruido(trama, tasa_error);
    printf("Trama después de ruido: %s\n", trama);

    // Guarda en archivo
    FILE *f = fopen("message.txt", "w");
    fprintf(f, "%s", trama);
    fclose(f);

    printf("Trama final guardada en message.txt\n");
    return 0;
}
