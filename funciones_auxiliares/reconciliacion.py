# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# Fecha: 13/02/2025

import tkinter as tk

# Función que calcula la paridad, devuelve cero si el número de 1 es par.
def calcularParidad(bits):
  return sum(bits) % 2 

# Paso 3: Reconciliación.
def reconciliacion(mi_secuencia, su_secuencia):
  secuencia = []
  for i in range(len(mi_secuencia)):
    if mi_secuencia[i] == su_secuencia[i]:
      secuencia.append(mi_secuencia[i])
    else:
      secuencia.append('0')
  paridadA = calcularParidad([int(bit) for bit in mi_secuencia])
  paridadB = calcularParidad([int(bit) for bit in su_secuencia])
  if paridadA != paridadB:
      print("[SERVER]: ERROR. Ha habido un error en la reconciliación.")
  return secuencia

def generarInfoReconciliacion(frame, secuencia_reconciliada):
  recuadro = tk.Frame(frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
  recuadro.pack(fill="both", expand=True, padx=20, pady=20)
  tk.Label(recuadro, text="Información de la reconciliación", font=("Arial",18,"bold")).pack(pady=10)
  tk.Label(recuadro, text="Secuencia de bits reconciliada", bg="white").pack(pady=5)
  tk.Label(recuadro, text=secuencia_reconciliada, bg="white").pack(pady=5)