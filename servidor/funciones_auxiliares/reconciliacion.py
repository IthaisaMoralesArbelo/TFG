# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# Fecha: 13/02/2025
# Fichero reconciliacion.py: Contiene las funciones auxiliares relativas al proceso de
# reconciliación de secuencias y sus métricas.


import hashlib
import sys
sys.path.append("/home/raspberrypiserver/Desktop/pqcIoT/pyascon")
from asconv1 import ascon_hash
import tkinter as tk

import funciones_auxiliares.estadisticasPDF as archivo

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
        
        
# Calcula la métrica de Hamming
def metricaHamming(secuencia_server, secuencia_client):
  assert(len(secuencia_server) == len(secuencia_client))
  return sum(bit1 != bit2 for bit1,bit2 in zip(secuencia_server, secuencia_client))
  

# Genera las estadísticas relacionadas con las métricas de la reconciliación 
def generarInfoReconciliacion(frame, secuencia_reconciliada, secuencia_server, secuencia_client):
  recuadro = tk.Frame(frame, bg="white", bd=2, relief="solid", padx=10, pady=10)
  recuadro.pack(fill="both", expand=True, padx=20, pady=20)
  tk.Label(recuadro, text="Información de la reconciliación", font=("Arial",18,"bold")).pack(pady=10)
  tk.Label(recuadro, text="Secuencia de A", bg="white").pack(pady=5)
  tk.Label(recuadro, text=secuencia_server, bg="white").pack(pady=5)
  tk.Label(recuadro, text="Secuencia de B", bg="white").pack(pady=5)
  tk.Label(recuadro, text=secuencia_client, bg="white").pack(pady=5)
  tk.Label(recuadro, text="Secuencia de bits reconciliada", bg="white").pack(pady=5)
  tk.Label(recuadro, text=secuencia_reconciliada, bg="white").pack(pady=5)
  tk.Label(recuadro, text="Métrica de Hamming", bg="white").pack(pady=5)
  tk.Label(recuadro, text=metricaHamming(secuencia_server, secuencia_client), bg="white").pack(pady=5)
  
  archivo.informacion += f'''
  =============== RECONCILIACIÓN ===============
  Secuencia de bits de A: {secuencia_server}
  Secuencia de bits de B: {secuencia_client}
  Secuencia de bits reconciliada: {secuencia_reconciliada}
  Métrica de Hamming: {metricaHamming(secuencia_server, secuencia_client)}
  
  '''
  
# Proceso de reconciliación
def iniciarReconciliacion(conn, secuencia):
  secuencia_final = list("0000000000000000")
  secuencia = list(secuencia)
  hash_recibido= conn.recv(1024).decode()
  hash_calculado = calcular_hash(''.join(secuencia))
 
  if hash_calculado == hash_recibido:
    secuencia_final = secuencia
    conn.sendall("Coinciden".encode())
    return
  else:
    conn.sendall("Continuar".encode())
  secuencia_final=reconciliacion(conn, secuencia)
  
  conn.sendall("Fin de transmisión".encode())
  return secuencia_final
  
def reconciliacion(conn, mi_secuencia, mitad=16):
  while True:
    mitad = mitad // 2
    if mitad == 1:
      hash_cliente = conn.recv(1024).decode()
      primera_mitad = mi_secuencia[:mitad]
      segunda_mitad = mi_secuencia[mitad:]
      hash_primera = calcular_hash(''.join(primera_mitad))
      hash_segunda = calcular_hash(''.join(segunda_mitad))
      hashes = hash_cliente.split(",")
      continuar_primera = checkHashes(hashes[0], hash_primera)
      continuar_segunda = checkHashes(hashes[1], hash_segunda)
      
      if continuar_primera:
        if mi_secuencia[0] == "0":
           mi_secuencia[0] = "1"
        else:
          mi_secuencia[0] = "0"
      if continuar_segunda:
        if mi_secuencia[1] == "0":
          mi_secuencia[1] = "1"
        else:
          mi_secuencia[1] = "0"
      conn.sendall("Fin".encode())
      return ''.join(mi_secuencia)
        
    primera_mitad = mi_secuencia[:mitad]
    segunda_mitad = mi_secuencia[mitad:]
    hash_primera = calcular_hash(''.join(primera_mitad))
    hash_segunda = calcular_hash(''.join(segunda_mitad))
    respuesta = conn.recv(1024).decode()
    hashes = respuesta.split(",")
    continuar_primera = checkHashes(hashes[0], hash_primera)
    continuar_segunda = checkHashes(hashes[1], hash_segunda)
        
    if continuar_primera and continuar_segunda:
      conn.sendall(" Continuar ambas".encode())
      primera_mitad = reconciliacion(conn, primera_mitad, mitad)
      segunda_mitad = reconciliacion(conn, segunda_mitad, mitad)
    elif continuar_primera:
      conn.sendall(" Continuar primera".encode())
      primera_mitad = reconciliacion(conn, primera_mitad, mitad)
    elif continuar_segunda:
      conn.sendall(" Continuar segunda".encode())
      segunda_mitad = reconciliacion(conn, segunda_mitad, mitad)
    else:
      conn.sendall(" Coinciden".encode())
    primera_mitad=list(primera_mitad)
    segunda_mitad=list(segunda_mitad)
    return primera_mitad + segunda_mitad
