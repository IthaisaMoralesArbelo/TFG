# Universidad de La Laguna
# Escuela Superior de Ingeniería y Tecnología
# Grado en Ingeniería Informática
# Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT 
# a partir de la Capa Física
# Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es
# Fecha: 13/02/2025
# Fichero estadísticasPDF.py: Contiene las funciones auxiliares y la estructura de datos
# necesaria para generar el PDF con las métricas del proceso de generación de claves. 

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import datetime
import tkinter as tk


# Estructura de datos para almacenar la información del PDF
class InfoPDF:
  def sondeo(self, num_paquetes, tiempo, media_simple_A, media_simple_B,
  media_adaptativa_A, media_adaptativa_B, entropia_a, entropia_b,
  valor_min_A, valor_min_B, valor_max_A, valor_max_B,
  valor_min_A_general, valor_min_B_general,
  valor_max_A_general, valor_max_B_general):
    self.numero_paquetes = num_paquetes
    self.tiempo = tiempo
    self.media_simple_A = media_simple_A
    self.media_simple_B = media_simple_B
    self.media_adaptativa_A = media_adaptativa_A
    self.media_adaptativa_B = media_adaptativa_B
    self.entropia_a = entropia_a
    self.entropia_b = entropia_b
    self.valor_min_A = valor_min_A
    self.valor_min_B = valor_min_B
    self.valor_max_A = valor_max_A
    self.valor_max_B = valor_max_B
    self.valor_min_A_general = valor_min_A_general
    self.valor_min_B_general = valor_min_B_general
    self.valor_max_A_general = valor_max_A_general
    self.valor_max_B_general = valor_max_B_general

  def cuantificacion(self, secuencia_A, secuencia_B, BDR, autocorrelacion_a,
  autocorrelacion_b, entriopia_a, entropia_b):
    self.secuencia_A = secuencia_A
    self.secuencia_B = secuencia_B
    self.BDR = BDR
    self.autocorrelacion_a = autocorrelacion_a
    self.autocorrelacion_b = autocorrelacion_b
    self.entropia_a = entropia_a
    self.entropia_b = entropia_b
   
  def reconciliacion(self, secuencia_server, secuencia_client,
  secuencia_reconciliada, metrica_hamming):
    self.secuencia_server = secuencia_server
    self.secuencia_client = secuencia_client
    self.secuencia_reconciliada = secuencia_reconciliada
    self.metrica_hamming = metrica_hamming

  def amplificacion(self, clave_compartida):
    self.clave_compartida = clave_compartida

  def generar_pdf(self):
  try:
    nombre_pdf = f"PLKG_IoT_Proceso_de_Generación_de_Claves_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = canvas.Canvas(nombre_pdf, pagesize=A4)
    ancho, alto = A4
    margen = 40
    y_actual = alto - margen

    # === Recuadro general del informe ===
    alto_total = alto - 2 * margen
    c.setStrokeColorRGB(0, 0, 0)
    c.rect(margen - 10, margen - 10, ancho - 2 * (margen - 10), alto_total + 10)

    # === Cabecera ===
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margen, y_actual, "Universidad de La Laguna")
    y_actual -= 20
    c.drawString(margen, y_actual, "Escuela Superior de Ingeniería y Tecnología")
    y_actual -= 20
    c.drawString(margen, y_actual, "Grado en Ingeniería Informática")
    y_actual -= 20
    c.drawString(margen, y_actual, "Trabajo de Fin de Grado:")
    y_actual -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margen, y_actual, "Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física")
    y_actual -= 30
    c.setFont("Helvetica", 11)
    c.drawString(margen, y_actual, "Autora: Ithaisa Morales Arbelo. alu0101482194@ull.edu.es")
    y_actual -= 20
    c.drawString(margen, y_actual, f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    y_actual -= 30

    # === Sección: Sondeo ===
    altura_bloque = 120
    c.rect(margen, y_actual - altura_bloque, ancho - 2 * margen, altura_bloque)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margen + 5, y_actual - 15, "1. Sondeo")
    c.setFont("Helvetica", 10)
    y = y_actual - 30
    c.drawString(margen + 10, y, f"Nº paquetes: {self.numero_paquetes}   Tiempo: {self.tiempo}")
    y -= 15
    c.drawString(margen + 10, y, f"Media simple A: {self.media_simple_A}   Media simple B: {self.media_simple_B}")
    y -= 15
    c.drawString(margen + 10, y, f"Media adaptativa A: {self.media_adaptativa_A}   Media adaptativa B: {self.media_adaptativa_B}")
    y -= 15
    c.drawString(margen + 10, y, f"Entropía A: {self.entropia_a}   Entropía B: {self.entropia_b}")
    y -= 15
    c.drawString(margen + 10, y, f"Valor mínimo A: {self.valor_min_A}   Valor mínimo B: {self.valor_min_B}")
    y -= 15
    c.drawString(margen + 10, y, f"Valor máximo A: {self.valor_max_A}   Valor máximo B: {self.valor_max_B}")
    y -= 15
    c.drawString(margen + 10, y, f"Valor mínimo A (global): {self.valor_min_A_general}   Valor mínimo B (global): {self.valor_min_B_general}")
    y -= 15
    c.drawString(margen + 10, y, f"Valor máximo A (global): {self.valor_max_A_general}   Valor máximo B (global): {self.valor_max_B_general}")
    y_actual = y - 30

    # === Sección: Cuantificación ===
    c.rect(margen, y_actual - altura_bloque, ancho - 2 * margen, altura_bloque)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margen + 5, y_actual - 15, "2. Cuantificación")
    c.setFont("Helvetica", 10)
    y = y_actual - 30
    c.drawString(margen + 10, y, f"Secuencia A: {self.secuencia_A}")
    y -= 15
    c.drawString(margen + 10, y, f"Secuencia B: {self.secuencia_B}")
    y -= 15
    c.drawString(margen + 10, y, f"BDR: {self.BDR}")
    y -= 15
    c.drawString(margen + 10, y, f"Autocorrelación A: {self.autocorrelacion_a}")
    y -= 15
    c.drawString(margen + 10, y, f"Autocorrelación B: {self.autocorrelacion_b}")
    y -= 15
    c.drawString(margen + 10, y, f"Entropía A: {self.entropia_a}")
    y -= 15
    c.drawString(margen + 10, y, f"Entropía B: {self.entropia_b}")
    y_actual = y - 30

    # === Sección: Reconciliación ===
    c.rect(margen, y_actual - altura_bloque, ancho - 2 * margen, altura_bloque)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margen + 5, y_actual - 15, "3. Reconciliación")
    c.setFont("Helvetica", 10)
    y = y_actual - 30
    c.drawString(margen + 10, y, f"Secuencia Server: {self.secuencia_server}")
    y -= 15
    c.drawString(margen + 10, y, f"Secuencia Client: {self.secuencia_client}")
    y -= 15
    c.drawString(margen + 10, y, f"Secuencia reconciliada: {self.secuencia_reconciliada}")
    y -= 15
    c.drawString(margen + 10, y, f"Métrica de Hamming: {self.metrica_hamming}")
    y_actual = y - 30
    
    # === Sección: Amplificación ===
    c.rect(margen, y_actual - altura_bloque, ancho - 2 * margen, altura_bloque)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margen + 5, y_actual - 15, "4. Amplificación")
    c.setFont("Helvetica", 10)
    y = y_actual - 30
    c.drawString(margen + 10, y, f"Clave compartida: {self.clave_compartida}")
    y -= 15
    # === Pie de página ===
    c.setFont("Helvetica", 8)
    y_actual -= 20
    c.drawString(margen, y_actual, "Trabajo de Fin de Grado: Generación de Claves Compartidas en Dispositivos IoT a partir de la Capa Física")
    y_actual -= 20
    c.drawString(margen, y_actual, "Universidad de La Laguna")
    y_actual -= 20
    
    c.save()
    print(f"[PDF]: Informe generado correctamente: {nombre_pdf}")
  except Exception as e:
    print(f"[PDF]: Error al generar PDF: {e}")
