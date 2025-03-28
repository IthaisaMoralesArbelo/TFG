# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es


import os
import re
import hashlib
import numpy as np
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from collections import Counter
import math
from collections import defaultdict


########### Variables y parámetros globales ########### 
RSSI_FILE_A = "rssi_log.txt"
RSSI_FILE_B = "rssi_log_B.txt"
RSSI_FILE_CANAL_A = "rssi_canal_a.txt"  
RSSI_FILE_CANAL_B = "rssi_canal_b.txt"  

media_rssi_a = 0
media_rssi_b = 0

rssi_a_total = []
rssi_b_total = []
timestamps = []
rssi_values_a = []
rssi_values_b = []
rssi_a = {}
rssi_b = {}
rssi_canal_a = {}
rssi_canal_b = {}





def limpiarContenedor(contenedor):
  for widget in contenedor.winfo_children():
    widget.destroy()


def obtenerRssiArchivo(archivo):
  rssi_data = defaultdict(list)
  if os.path.exists(archivo):
    with open(archivo, "r") as f:
      for line in f:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
        if match:
          timestamp, rssi = match.groups()
          rssi_data[timestamp].append(int(rssi))
  return rssi_data


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



def media_no_adaptativa(file):
  valores = []
  if os.path.exists(file):
    with open(file, "r") as f:
      for line in f:
        match = re.search(r"(-\d+)\s+dBm", line)
        if match:
          valores.append(int(match.group(1)))
  return sum(valores) / len(valores) if valores else 0


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



def entropia(rssi_file):
  if os.path.exists(rssi_file):
    with open(rssi_file, "r") as f:
      rssi = []
      for line in f:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
        if match:
          rssi.append(int(match.group(2)))
        
    # Contamos la frecuencia de cada valor de RSSI
    total_medidas = len(rssi)
    frecuencia = Counter(rssi)
    probabilidades = {valor: count / total_medidas for valor, count in frecuencia.items()}
        
    # Calcular la entropía del canal
    entropia = -sum(prob * math.log2(prob) for prob in probabilidades.values())
    return entropia
  else:    
    print(f"[SERVER]: ERROR. No se encontró el archivo: {rssi_file}")
    return None

def iniciarGrafica(frame_contenedor):
    global figure, ax, canvas, toolbar, anim
    global timestamps, rssi_values_a, rssi_values_b

    # Limpiar contenedor
    for widget in frame_contenedor.winfo_children():
        widget.destroy()

    timestamps.clear()
    rssi_values_a.clear()
    rssi_values_b.clear()

    figure, ax = plt.subplots(figsize=(6, 4))
    ax.set_title("Sondeo del canal")
    ax.set_xlabel("Tiempo")
    ax.set_ylabel("RSSI (dBm)")
    ax.set_ylim(-40, 0)

    canvas = FigureCanvasTkAgg(figure, master=frame_contenedor)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    toolbar = NavigationToolbar2Tk(canvas, frame_contenedor)
    toolbar.update()
    toolbar.pack(side="top", fill="x")

    anim = FuncAnimation(figure, actualizarGrafica, interval=1000, save_count=100)


def actualizarGrafica(frame):
    global ax, canvas, timestamps
    global media_rssi_a, media_rssi_b
    if os.path.exists(RSSI_FILE_A):
        with open(RSSI_FILE_A, "r") as f:
            for line in f:
                match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
                if match:
                    timestamp = match.group(1)
                    rssi = int(match.group(2))
                    if timestamp not in rssi_a:
                        rssi_a[timestamp] = []
                    rssi_a[timestamp].append(rssi)

# Leer el archivo de B
    if os.path.exists(RSSI_FILE_B):
        with open(RSSI_FILE_B, "r") as f:
            for line in f:
                match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
                if match:
                    timestamp = match.group(1)
                    rssi = int(match.group(2))
                    if timestamp not in rssi_b:
                        rssi_b[timestamp] = []
                    rssi_b[timestamp].append(rssi)

# Calcular la media de RSSI por segundo
    timestamps = sorted(set(rssi_a.keys()) & set(rssi_b.keys()))  # Solo timestamps en ambos archivos
    valores_a = [sum(rssi_a[t]) / len(rssi_a[t]) for t in timestamps]
    valores_b = [sum(rssi_b[t]) / len(rssi_b[t]) for t in timestamps]
    media_rssi_a = media(RSSI_FILE_A)
    media_rssi_b = media(RSSI_FILE_B)
    ax.clear()
    ax.set_title("Sondeo del canal")
    ax.set_xlabel("Tiempo")
    ax.set_ylabel("RSSI (dBm)")
    ax.set_ylim(-40, 0)

    ax.plot(timestamps, valores_a, 'o-', color='purple', label="RSSI A")
    ax.plot(timestamps, valores_b, 's-', color='orange', label="RSSI B")
    ax.axhline(media_rssi_a, color='purple', linestyle='dashed', label="RSSI A (media)")
    ax.axhline(media_rssi_b, color='orange', linestyle='dashed', label="RSSI B (media)")
    ax.legend()

    canvas.draw()




def generarEstadisticas(frame, numero_paquetes, tiempo_entre_paquetes):
  global media_rssi_a, media_rssi_b
  recuadro = tk.Frame(frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
  recuadro.pack(fill="both", expand=True, padx=20, pady=20)
  label = tk.Label(recuadro, text="Estadísticas de la comunicación", font=("Arial",18,"bold"))
  label.pack(pady=10)
  tk.Label(recuadro, text=f"Número de paquetes enviados: {numero_paquetes}", bg="white").pack(pady=5)
  tk.Label(recuadro, text=f"Tiempo entre paquetes: {tiempo_entre_paquetes} ms",bg="white").pack(pady=5)
  tk.Label(recuadro, text="Medias simples de RSSI", bg="white").pack(pady=10)
  tk.Label(recuadro, text=f"RSSI A: Media={media_no_adaptativa(RSSI_FILE_A):.2f}", bg="white").pack(pady=5)
  tk.Label(recuadro, text=f"RSSI B: Media={media_no_adaptativa(RSSI_FILE_B):.2f}", bg="white").pack(pady=5)
  tk.Label(recuadro, text="Valores RSSI medios tras hacer un filtrado de ruido", bg="white").pack(pady=10)
  tk.Label(recuadro, text=f"RSSI A: Media={media_rssi_a:.2f}", bg="white").pack(pady=5)
  tk.Label(recuadro, text=f"RSSI B: Media={media_rssi_b:.2f}", bg="white").pack(pady=5)
  tk.Label(recuadro, text="Entropía del canal", bg="white").pack(pady=10)
  tk.Label(recuadro, text=f"Entropía medida por A: {entropia(RSSI_FILE_A):.2f}", bg="white").pack(pady=5)
  tk.Label(recuadro, text=f"Entropía medida por B: {entropia(RSSI_FILE_B):.2f}", bg="white").pack(pady=5)
  tk.Label(recuadro, text="Valores mínimo y máximo de RSSI del canal entre A y B", bg="white").pack(pady=10)
  min_a, max_a = valorMinimoMaximoRssi(RSSI_FILE_A)
  min_b, max_b = valorMinimoMaximoRssi(RSSI_FILE_B)
  tk.Label(recuadro, text=f"RSSI A: Valor máximo={min_a}, mínimo={max_a}", bg="white").pack(pady=5)
  tk.Label(recuadro, text=f"RSSI B: Valor máximo={min_b}, mínimo={max_b}", bg="white").pack(pady=5)
  tk.Label(recuadro, text="Valores mínimo y máximo de RSSI en el canal de entre todos los dispositivos", bg="white").pack(pady=10)
  min_canal_a, max_canal_a = valorMinimoMaximoRssi(RSSI_FILE_CANAL_A)
  min_canal_b, max_canal_b = valorMinimoMaximoRssi(RSSI_FILE_CANAL_B)
  tk.Label(recuadro, text=f"RSSI A: Valor máximo={min_canal_a}, mínimo={max_canal_a}", bg="white").pack(pady=5)
  tk.Label(recuadro, text=f"RSSI B: Valor máximo={min_canal_b}, mínimo={max_canal_b}", bg="white").pack(pady=5)



       
def iniciarSegundaGrafica(frame_contenedor):
    global figure, ax, canvas, toolbar, anim, rssi_a, rssi_b, timestamps
    rssi_a.clear()
    rssi_b.clear()
    rssi_canal_a.clear()
    rssi_canal_b.clear()

    # Limpiar contenedor
    for widget in frame_contenedor.winfo_children():
        widget.destroy()
    
    figure, ax = plt.subplots(figsize=(6, 4))
    ax.set_title("Sondeo del canal")
    ax.set_xlabel("Tiempo")
    ax.set_ylabel("RSSI (dBm)")
    ax.set_ylim(-120, 0)

    canvas = FigureCanvasTkAgg(figure, master=frame_contenedor)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    toolbar = NavigationToolbar2Tk(canvas, frame_contenedor)
    toolbar.update()
    toolbar.pack(side="top", fill="x")

    anim = FuncAnimation(figure, actualizarSegundaGrafica, interval=1000, save_count=100)

def actualizarSegundaGrafica(frame):
    global figure, ax, canvas, toolbar, anim, rssi_a, rssi_b, timestamps

    # Limpiar diccionarios de datos
    rssi_a.clear()
    rssi_b.clear()
    rssi_canal_a.clear()
    rssi_canal_b.clear()

    def leer_archivo(filename, diccionario):
        """ Función para leer un archivo de RSSI y almacenar datos en un diccionario """
        if os.path.exists(filename):
            with open(filename, "r") as f:
                for line in f:
                    match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
                    if match:
                        timestamp = match.group(1)
                        rssi = int(match.group(2))
                        if timestamp not in diccionario:
                            diccionario[timestamp] = []
                        diccionario[timestamp].append(rssi)

    # Leer datos de los cuatro archivos
    leer_archivo(RSSI_FILE_A, rssi_a)
    leer_archivo(RSSI_FILE_B, rssi_b)
    leer_archivo(RSSI_FILE_CANAL_A, rssi_canal_a)
    leer_archivo(RSSI_FILE_CANAL_B, rssi_canal_b)

    # Obtener timestamps comunes
    timestamps = sorted(set(rssi_a.keys()) | set(rssi_b.keys()) | set(rssi_canal_a.keys()) | set(rssi_canal_b.keys()))

    # Calcular valores medios
    valores_a = [sum(rssi_a[t]) / len(rssi_a[t]) if t in rssi_a else None for t in timestamps]
    valores_b = [sum(rssi_b[t]) / len(rssi_b[t]) if t in rssi_b else None for t in timestamps]
    valores_canal_a = [sum(rssi_canal_a[t]) / len(rssi_canal_a[t]) if t in rssi_canal_a else None for t in timestamps]
    valores_canal_b = [sum(rssi_canal_b[t]) / len(rssi_canal_b[t]) if t in rssi_canal_b else None for t in timestamps]


    media_rssi_a = media_no_adaptativa(RSSI_FILE_A)
    media_rssi_b = media_no_adaptativa(RSSI_FILE_B)
    media_rssi_canal_a = media_no_adaptativa(RSSI_FILE_CANAL_A)
    media_rssi_canal_b = media_no_adaptativa(RSSI_FILE_CANAL_B)
    # Limpiar gráfico
    ax.clear()
    ax.set_title("Sondeo del canal")
    ax.set_xlabel("Tiempo")
    ax.set_ylabel("RSSI (dBm)")
    ax.set_ylim(-120, 0)

    # Graficar dispositivos A y B con colores distintivos
    ax.plot(timestamps, valores_a, 'o-', color='purple', label="RSSI A")
    ax.plot(timestamps, valores_b, 's-', color='orange', label="RSSI B")

    # Graficar todos los dispositivos en gris
    ax.plot(timestamps, valores_canal_a, 'x-', color='gray', alpha=0.3, label="Todos desde A")
    ax.plot(timestamps, valores_canal_b, 'd-', color='darkgray', alpha=0.3, label="Todos desde B")

    # Líneas de media
    ax.axhline(media_rssi_a, color='purple', linestyle='dashed', label="RSSI A (media)")
    ax.axhline(media_rssi_b, color='orange', linestyle='dashed', label="RSSI B (media)")
    ax.axhline(media_rssi_canal_a, color='gray', linestyle='dashed', label="Todos desde A (media)")
    ax.axhline(media_rssi_canal_b, color='darkgray', linestyle='dashed', label="Todos desde B (media)")

    ax.legend()
    canvas.draw()
