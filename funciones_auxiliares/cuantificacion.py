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
import numpy as np
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

def desviacionTipica(media, rssi_file):
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
          secuencia.append('1')
        elif rssi < rangoInferior:
          secuencia.append('0')
  print("media",media)
  print("desviacion", desviacion_tipica)
  secuencia = ''.join(secuencia)
  return secuencia

  ###### OPCIÓN 2 ######
def cuantificacion_dos(rssi_file):
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
def cuantificacion_tres(rssi_file):
  if os.path.exists(rssi_file):
    with open(rssi_file, "r") as f:
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
      n_niveles = max(n_niveles, 2)
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
      return secuencia_codificada;

  
# Función que crea una lista de secuencias. Son 2^num_bits posibilidades
def gray(num_bits):
  codigos = []
  for i in range(2 ** num_bits):
    codigos.append(i ^ (i >> 1))
  return codigos


# Función variable
def e(k):
  return 1 if k % 4 == 2 else 0
  
def cuantificacion_cuatro(rssi, num_bits_secuencia = 8, y_min = -280, y_max = -180):
  k = 4 * (2 ** num_bits_secuencia) 
  umbrales = np.linspace(y_min, y_max, k - 1) # K - 1 umbrales, y_min y y_max son los min y max esperados en un RSSI
  umbrales = [-np.inf] + list(umbrales) + [np.inf]
  nivel_rssi = 0
  while nivel_rssi < k and rssi > umbrales[nivel_rssi]:
    nivel_rssi += 1
  # Genero los códigos de Gray
  codigos = gray(num_bits_secuencia)
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
