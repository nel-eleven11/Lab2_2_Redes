import pandas as pd
import matplotlib.pyplot as plt

# Carga ambos archivos
df_emisor = pd.read_csv("resultados_emisor.csv")
df_receptor = pd.read_csv("resultados_receptor.csv")

# Une por trama enviada/recibida
df = pd.merge(
    df_emisor,
    df_receptor,
    left_on="trama_enviada",
    right_on="trama_recibida",
    how="inner"
)

# Calcula la longitud del mensaje
df['msg_len'] = df['mensaje_original'].apply(len)

# Normaliza tasa de error (puede ser float o string)
df['tasa_error'] = df['tasa_error'].astype(float)

# Mensaje exitoso si error_detectado == 0
df['exito'] = (df['error_detectado'] == 0).astype(int)


# Solo estas combinaciones
longitudes = [5, 10]
tasas = [0.0, 0.05, 0.5]

fig, axes = plt.subplots(1, len(longitudes), figsize=(15, 5), sharey=True)

for idx, l in enumerate(longitudes):
    datos = []
    for t in tasas:
        subset = df[(df['msg_len'] == l) & (df['tasa_error'].round(2) == t)]
        if len(subset) == 0:
            porcentaje = 0
        else:
            porcentaje = subset['exito'].mean() * 100
        datos.append(porcentaje)
    axes[idx].bar([f"{int(x*100)}%" for x in tasas], datos, color="steelblue")
    axes[idx].set_title(f"Longitud = {l}")
    axes[idx].set_xlabel("Probabilidad de Ruido")
    if idx == 0:
        axes[idx].set_ylabel("Porcentaje de Mensajes Exitosos (%)")
    axes[idx].set_ylim(0, 100)

plt.suptitle('Mensajes Recibidos Exitosamente por Longitud y Ruido')
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()