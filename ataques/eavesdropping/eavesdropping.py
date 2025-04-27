# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# Fecha: 27/04/2025
# Fichero eavesdropping.py: Contiene la interfaz y la lógica del ataque de eavesdropping.

import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
from scapy.all import sniff, Dot11, RadioTap
import os
import math
import numpy as np
import re

########### Variables y parámetros globales ########### 

mac_cliente = "e4:fa:c4:6f:6f:bf"
mac_servidor = "e4:fa:c4:6f:6f:6a"
last_timestamp = {}
RSSI_FILE = "rssi_eave.txt"
capturando = False
captura_thread = None


########### Funciones auxiliares  ########### 

# Calcula el valor mínimo y máximo de RSSI
def valorMinimoMaximoRssi(rssi_file):
  if os.path.exists(rssi_file):
    with open(rssi_file, "r") as f:
      rssi = []
      for line in f:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
        if match:
          rssi.append(int(match.group(2)))
    return min(rssi), max(rssi)
  else:
    print(f"[SERVER]: ERROR. No se encontró el archivo: {rssi_file}")
    return None, None


# Elimina el archivo de RSSI del sondeo anterior
def eliminar_archivo():
    if os.path.exists(RSSI_FILE):
        os.remove(RSSI_FILE)
        print(f"[SERVER]: Archivo {RSSI_FILE} eliminado.")
    else:
        print(f"[SERVER]: El archivo {RSSI_FILE} no existe.")


# Función que crea una lista de secuencias. Son 2^num_bits posibilidades
def gray(num_bits):
  codigos = []
  for i in range(2 ** num_bits):
    codigos.append(i ^ (i >> 1))
  return codigos


# Función variable
def e(k):
  return 1 if (k % 3 == 1 or k % 5 == 3) else 0
  

###### Esquema de cuantificación multibit adaptativo ######
def cuantificacion_cuatro(rssi, num_bits_secuencia = 16, y_min = -280, y_max = -180):
  y_min, y_max = valorMinimoMaximoRssi(RSSI_FILE)
  k = 4 * (2 ** num_bits_secuencia) 
  umbrales = np.linspace(y_min, y_max, k - 1) # K - 1 umbrales, y_min y y_max son los min y max esperados en un RSSI
  umbrales = [-np.inf] + list(umbrales) + [np.inf]
  nivel_rssi = 0
  while nivel_rssi < k and rssi > umbrales[nivel_rssi]:
    nivel_rssi += 1
  # Genero los códigos de Gray
  codigos = gray(num_bits_secuencia)
  nivel_rssi = (nivel_rssi * 7) % (2 ** num_bits_secuencia)
  # Calculo e(k) para saber si es 1 o 0
  e_k = e(nivel_rssi)
  if e_k == 1:
    nivel_rssi = min(nivel_rssi, len(codigos) - 1)
    resultado = codigos[nivel_rssi]
  else:
    # Gray desplazado
    resultado = codigos[(nivel_rssi + 1) % len(codigos)]  
  secuencia = format(resultado, f'0{num_bits_secuencia}b') 
  return secuencia


# Media adaptativa de RSSI
def media(rssi_file, diferencia = 10):
  if not os.path.exists(rssi_file):
    print(f"[SERVER]: ERROR. No se encontró el archivo: {rssi_file}")
    return None

  mediciones = []

  with open(rssi_file, "r") as f:
    for line in f:
      match = re.search(r", (-?\d+)\s+dBm", line)
      if match:
        mediciones.append(int(match.group(1)))

  if not mediciones:
    print(f"[SERVER]: ERROR. No se encontraron mediciones en {rssi_file}")
    return None

  media_sin_filtrar = sum(mediciones) / len(mediciones)
  mediciones_filtradas = []

  for i in range(len(mediciones)):
    if i == 0:
      mediciones_filtradas.append(mediciones[i])
    else:
      if abs(mediciones[i] - media_sin_filtrar) < diferencia:
        mediciones_filtradas.append(mediciones[i])
      else:
        mediciones_filtradas.append(media_sin_filtrar)
  

  valor_medio_rssi = sum(mediciones_filtradas) / len(mediciones_filtradas)
  return valor_medio_rssi



########### Funciones Eavesdropping ###########

# Función para iniciar la escucha
def escuchar():
  global boton_uno, capturando, captura_thread, boton_dos
  eliminar_archivo()
  boton_uno.destroy()  
  capturando = True
  boton_dos = tk.Button(cuerpo, text="Detener escucha", font=app.font,
                        bg="#c0392b", command=detener_escucha, fg="white",
                        width=30, height=2)
  boton_dos.pack(fill="x", pady=135, padx=350)

  captura_thread = threading.Thread(target=iniciar_captura)
  captura_thread.start()

# Función de captura de paquetes
def iniciar_captura():
  print("[*] Iniciando captura de paquetes...")
  sniff(prn=packet_handler, stop_filter=lambda x: not capturando, store=0, iface="wlp2s0")

# Función para manejar cada paquete capturado
def packet_handler(pkt):
  global last_timestamp

  if pkt.haslayer(Dot11):
    if pkt.type == 0 and pkt.subtype in [4, 5, 8]:  
      mac_origen = pkt.addr2
      mac_destino = pkt.addr1
      rssi = None
      try:
        if pkt.haslayer(RadioTap) and hasattr(pkt, "dBm_AntSignal"):
          rssi = pkt.dBm_AntSignal
      except Exception as e:
        print("Error al extraer RSSI:", e)

      if rssi is not None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if mac_origen not in last_timestamp or \
            time.mktime(time.strptime(timestamp, "%Y-%m-%d %H:%M:%S")) - \
            time.mktime(time.strptime(last_timestamp[mac_origen], "%Y-%m-%d %H:%M:%S")) >= 1:
          entry = f"{timestamp}, {mac_origen} -> {mac_destino}, {rssi} dBm"
          print(entry)
          last_timestamp[mac_origen] = timestamp
          if (mac_origen == mac_servidor and mac_destino == mac_cliente) or (mac_origen == mac_cliente and mac_destino == mac_servidor):
            with open(RSSI_FILE, "a") as f:
              f.write(entry + "\n")


# Función para detener la escucha
def detener_escucha():
    global capturando, boton_dos
    print("[*] Deteniendo captura...")
    capturando = False
    time.sleep(2)
    try:
      boton_dos.destroy()
      recuadro = tk.Frame(cuerpo, bg="white", padx=100, pady=100).pack(fill="both", expand=True)
      valor_medio = media(RSSI_FILE)
      secuencia = cuantificacion_cuatro(valor_medio)
      texto = f"Valor medio de RSSI: {valor_medio}\nSecuencia cuantificada: {secuencia}"
      resultado_label = tk.Label(cuerpo, text=texto, font=app.font, bg="white", fg="black", wraplength=600, justify="center")
      resultado_label.pack(pady=200)
    except Exception as e:
      print("[!] Error calculando resultados:", e)


####### Programa Principal #######
app = tk.Tk()
app.config(bg='white')
app.minsize(800, 600)
app.title("Ataque Eavesdropping")
app.geometry("1000x400")
app.font = ("Arial", 14)

####### Encabezado #######
encabezado = tk.Frame(app, bg='white', height=100)
encabezado.pack(fill="x", side="top", pady=10)
titulo_encabezado = tk.Label(encabezado, text="Ataque Eavesdropping", font=("Arial", 20), bg='white')
titulo_encabezado.pack(fill="x", padx=10, pady=10)
linea_encabezado = tk.Frame(app, bg="#5c068c", height=3)
linea_encabezado.pack(fill="x", side="top")

####### Cuerpo #######
cuerpo = tk.Frame(app, bg='white')
cuerpo.pack(fill="both", expand=True)

boton_uno = tk.Button(cuerpo, text="Comenzar a escuchar el canal", font=app.font,
                      bg="#5c068c", command=escuchar, fg="white", width=30, height=2)
boton_uno.pack(fill="x", pady=135, padx=350)

####### Footer #######
footer = tk.Frame(app, bg="#5c068c")
footer.pack(fill="x", side="bottom")
try:
    imagen = Image.open("images.png")
    imagen = imagen.resize((40, 40), Image.LANCZOS)
    logo = ImageTk.PhotoImage(imagen)
    label_logo = tk.Label(footer, image=logo, bg="#5c068c")
    label_logo.pack(pady=5)
except Exception as e:
    print("Error cargando el logo:", e)
texto_footer = tk.Label(footer,
                        text="Ithaisa Morales Arbelo. Universidad de La Laguna",
                        bg="#5c068c",
                        fg="white",
                        font=("Arial", 13))
texto_footer.pack(padx=5, pady=10)

app.mainloop()