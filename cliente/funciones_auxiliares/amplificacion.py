# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# Fecha: 13/02/2025
# Fichero amplificacion.py: Contiene las funciones auxiliares relativas al proceso de
# amplificación de privacidad y sus métricas.

import sys
sys.path.append("/home/raspberrypiclient/Desktop/pqcIoT/pyascon")
from ascon import ascon_hash
import tkinter as tk

########### Funciones ########### 

# Usa la función hash de ASCON
def amplificacion(secuencia_bits):
  clave_compartida = ascon_hash(secuencia_bits, variant="Ascon-Hash256", hashlength=32)
  return clave_compartida
