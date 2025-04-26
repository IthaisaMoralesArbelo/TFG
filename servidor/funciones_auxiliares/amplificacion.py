# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# Fecha: 13/02/2025
# Fichero amplificacion.py: Contiene las funciones auxiliares relativas al proceso de
# amplificación de privacidad y sus métricas.

import sys
sys.path.append("/home/raspberrypiserver/Desktop/pqcIoT/pyascon")
from asconv1 import ascon_hash
import tkinter as tk

########### Funciones ########### 

# Genera el recuadro de estadísticas sobre la amplificación de privacidad
def generarInfoAmplificacion(frame, clave_compartida):
  recuadro = tk.Frame(frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
  recuadro.pack(fill="both", expand=True, padx=20, pady=20)
  tk.Label(recuadro, text="Información de la amplificación", font=("Arial",18,"bold")).pack(pady=10)
  tk.Label(recuadro, text="Clave compartida generada", bg="white").pack(pady=5)
  tk.Label(recuadro, text=clave_compartida, bg="white").pack(pady=5)

# Usa la función hash de ASCON
def amplificacion(secuencia_bits):
  clave_compartida = ascon_hash(secuencia_bits, variant="Ascon-Hash256", hashlength=32)
  return clave_compartida
