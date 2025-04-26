# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT 
# a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# Fecha: 13/02/2025
# Fichero sondeo.py: Contiene las funciones auxiliares relativas al muestreo de
# RSSI y la generación de gráficas. 

from collections import Counter
from collections import defaultdict
import hashlib
import math
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import os
import re
import tkinter as tk


########### Variables y parámetros globales ########### 
RSSI_FILE_A = "rssi_log.txt"
RSSI_FILE_B = "rssi_log_B.txt"
RSSI_FILE_CANAL_A = "rssi_canal_a.txt"  
RSSI_FILE_CANAL_B = "rssi_canal_b.txt"  

########### Promedios globales ########### 
media_rssi_a = 0
media_rssi_b = 0

########### Listas de datos globales ########### 
rssi_a_total = []
rssi_b_total = []
timestamps = []
rssi_values_a = []
rssi_values_b = []

########### Diccionarios ########### 
rssi_a = {}
rssi_b = {}
rssi_canal_a = {}
rssi_canal_b = {}


########### Funciones ########### 

# Agrupa los valores RSSI por timestamp y devuelve un diccionario
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


# Promediado no adaptativo, para mejorar la entropía del canal
# se descartan los valores que se desvían más de 10 dBm de la media
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


# Media simple
def media_no_adaptativa(file):
  valores = []
  if os.path.exists(file):
    with open(file, "r") as f:
      for line in f:
        match = re.search(r"(-\d+)\s+dBm", line)
        if match:
          valores.append(int(match.group(1)))
  if valores:
    return sum(valores) / len(valores)
  else:
    return 0


# Función para calcular el valor mínimo y máximo de RSSI
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


# Calcula la aleatoriedad del canal
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
        
    # Calcula la entropía del canal
    entropia = -sum(prob * math.log2(prob) for prob in probabilidades.values())
    return entropia
  else:    
    print(f"[SERVER]: ERROR. No se encontró el archivo: {rssi_file}")
    return None
