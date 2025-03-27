# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# Fecha: 13/02/2025

import tkinter as tk
import os
import re
import math
from collections import Counter


def generarInfoCuantificacion(frame,secuencia_server, secuencia_client):
  recuadro = tk.Frame(frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
  recuadro.pack(fill="both", expand=True, padx=20, pady=20)
  tk.Label(recuadro, text="Información de la cuantificación", font=("Arial",18,"bold")).pack(pady=10)
  tk.Label(recuadro, text="Secuencia de bits de A", bg="white").pack(pady=5)
  tk.Label(recuadro, text=secuencia_server, bg="white").pack(pady=5)
  tk.Label(recuadro, text="Secuencia de bits de B", bg="white").pack(pady=5)
  tk.Label(recuadro, text=secuencia_client, bg="white").pack(pady=5)


###### OPCIÓN 1 ######
def media(rssi_file):
  if os.path.exists(rssi_file):
    with open(rssi_file, "r") as f:
      rssi = []
      for line in f:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
        if match:
          rssi.append(int(match.group(2)))
    return sum(rssi) / len(rssi)
  return 0

def desviacion_tipica(media, rssi_file):
  if os.path.exists(rssi_file):
    with open(rssi_file, "r") as f:
      rssi = []
      for line in f:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
        if match:
          rssi.append((int(match.group(2)) - media) ** 2)
    return (sum(rssi) / len(rssi)) ** 0.5
  return 0

def cuantificacion(media, desviacion_tipica, valor, rssi_file):
  secuencia = []
  rangoSuperior = media + valor * desviacion_tipica
  rangoInferior = media - valor * desviacion_tipica
  if os.path.exists(rssi_file):
    with open(rssi_file, "r") as f:
      for line in f:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
        if match:
          timestamp = match.group(1)
          rssi = int(match.group(2))
        if rssi > rangoSuperior:
          secuencia.append(1)
        elif rssi < rangoInferior:
          secuencia.append(0)
  return secuencia

  ###### OPCIÓN 2 ######
def cuantificacion(rssi_file):
  if os.path.exists(rssi_file):
    with open(rssi_file, "r") as f:
      rssi = []
      for line in f:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
        if match:
          rssi.append(int(match.group(2)))
    secuencia = []
    for i in range(1, len(rssi)):
      if rssi[i] < rssi[i-1]:
        secuencia.append(0)
      else:
        secuencia.append(1)
    return secuencia
  return 0


  ###### OPCIÓN 3 ######
def cuantificacion():
  if os.path.exists(RSSI_FILE):
    with open(RSSI_FILE, "r") as f:
      rssi = []
      for line in f:
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), .*?, (-\d+)\s+dBm", line)
        if match:
          rssi.append(int(match.group(2)))
        
      # Contar la frecuencia de cada valor de RSSI
      total_medidas = len(rssi)
      frecuencia = Counter(rssi)
      probabilidades = {valor: count / total_medidas for valor, count in frecuencia.items()}
        
      # Calcular la entropía del canal
      entropia = -sum(prob * math.log2(prob) for prob in probabilidades.values())
      entropia_entera = int(entropia)
        
      # Calcular el número de niveles
      n_niveles = 2 ** entropia_entera
      bits_por_nivel = math.log2(n_niveles)
        
      # Determinar los niveles de cuantificación
      rssi_min, rssi_max = min(rssi), max(rssi)
      niveles = [rssi_min + i * (rssi_max - rssi_min) / (n_niveles - 1) for i in range(n_niveles)]
        
      # Asignar códigos binarios a los niveles
      codigos = {niveles[i]: format(i, f'0{int(bits_por_nivel)}b') for i in range(n_niveles)}
        
      # Generar la secuencia final codificada
      secuencia_codificada = "".join(codigos[min(niveles, key=lambda x: abs(x - valor))] for valor in rssi)
        
      print("Probabilidades:", probabilidades)
      print("Entropía del canal:", entropia)
      print("Número de niveles:", n_niveles)
      print("Bits por nivel:", bits_por_nivel)
      print("Niveles de cuantificación:", niveles)
      print("Códigos asignados:", codigos)
      print("Secuencia codificada:", secuencia_codificada)