# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# Fecha: 13/02/2025
# Fichero reconciliacion.py: Contiene las funciones auxiliares relativas al proceso de
# reconciliacion de secuencias y sus métricas.


import hashlib
import sys
sys.path.append("/home/raspberrypiclient/Desktop/pqcIoT/pyascon")
from ascon import ascon_hash
import tkinter as tk


########### Funciones ###########

def calcular_hash(secuencia):
  secuencia = ''.join(secuencia).encode()
  return ascon_hash(secuencia, variant="Ascon-Hash256", hashlength=32).hex()
  #return hashlib.sha256(secuencia.encode()).hexdigest()
 

# Comprueba que los hashes sean iguales 
def checkHashes(hash_cliente, hash_servidor):
    if hash_cliente != hash_servidor:
        return True
    else:
        return False

# Función de reconciliación
def iniciarReconciliacion(sock, secuencia):
  secuencia = list(secuencia)
  hash_calculado = calcular_hash(''.join(secuencia))
  
  sock.sendall(hash_calculado.encode())
  while True:
    data = sock.recv(1024).decode().strip()
    
    if not data:
      print("Error. El servidor no ha respondido")
      break;
    if data == " Coinciden":
      return
    elif data == "Fin de transmisión":
      return secuencia
    secuencia = reconciliacion(sock, secuencia)
  secuencia_final = ''.join(secuencia)
  return secuencia_final
def reconciliacion(conn, mi_secuencia, mitad=16):
  
  while True:
    if len(mi_secuencia) == 1:
      return mi_secuencia
    
    mitad = mitad // 2
    primera_mitad = mi_secuencia[:mitad]
    segunda_mitad = mi_secuencia[mitad:]
    hash_primera = calcular_hash(''.join(primera_mitad))
    hash_segunda = calcular_hash(''.join(segunda_mitad))
    conn.sendall(f"{hash_primera},{hash_segunda}".encode())
    respuesta = conn.recv(1024).decode().strip()
    if respuesta == "Continuar primera":
      primera_mitad = reconciliacion(conn, primera_mitad, mitad)
      return primera_mitad + segunda_mitad
    elif respuesta == "Continuar segunda":
      segunda_mitad = reconciliacion(conn, segunda_mitad, mitad)
      return primera_mitad + segunda_mitad
    elif respuesta == "Continuar ambas":
      primera_mitad = reconciliacion(conn, primera_mitad, mitad)
      segunda_mitad = reconciliacion(conn, segunda_mitad, mitad)
      return primera_mitad + segunda_mitad
    elif respuesta == "Coinciden":
      return mi_secuencia
    else:
      return mi_secuencia
        

