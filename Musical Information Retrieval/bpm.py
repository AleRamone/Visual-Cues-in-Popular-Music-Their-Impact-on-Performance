# -*- coding: utf-8 -*-
"""esteban bpm.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Hj0eHj2nhLwGQ0rc4m3zfInbuCBUglwZ
"""

import matplotlib.pyplot as plt
import numpy as np
import librosa as li
import scipy.io
from scipy import signal
import csv

####################################################################################
#Este es el header del CSV
header = ['Pareja', 'Guitarrista', 'Condicion', 'Silencio', 'Trial', 'BPM']
data = []
#Se carga el array data de esta manera
#data = ['Pareja', 'Guitarrista', 'Condicion', 'Silencio', 'Trial', 'ONSET']

condicion = "S"
silencio = "SXL"

#Abrimos el archivo y corremos los procesos, a medida que vamos cargando la data
with open('BPM_RAMOS_'+condicion+'_'+silencio+'.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)

    #Escribimos el header
    writer.writerow(header)


    for p in range(1,17):
      for t in range(1,4):
        for g in range(1, 3):
          # carga del wav
          sr, data = scipy.io.wavfile.read('audios_nuevos2023/P'+str(p)+'_'+condicion+'_'+silencio+'_GTR'+str(g)+'_00'+str(t)+'.wav')

          # genero un filtro pasaaltos
          b, a = signal.butter(3, 1000, 'highpass', fs=sr)

          # cuantos samples se espera que dure cada negra
          bpm = 100 # bpm estimado aprox...
          bpm_samples = int(sr / (bpm/60))

          # busqueda cruda de picos en la señal, para eso hace falta primero darle contraste (filtro y **2)
          # luego ayuda darle una distancia esperada (tu bpm teorico) y tunear un threshold (depende de la señal)
          # si se complica, find peaks tiene mas parametros, pero conviene ayudarlo pre-procesando la señal para mejorar el contraste
          # le pido bpm_samples*0.9 porque conviene darle un poquito de margen a la distancia minima, que no esté tan justa
          peaks, _ = signal.find_peaks(signal.filtfilt(b,a, data)**2, distance = int(bpm_samples*0.9), threshold = 0.000001)

          #plt.subplots(figsize=(18, 3))
          #plt.plot(signal.filtfilt(b,a, data)**2)
          #plt.vlines(peaks, 0, 0.005, ls='dashed', color='red')

          # encuentro secciones, esto siempre hay que tunear los parametros del split y chequear que mas o menos funcione universalmente
          # aca tambien puede ayudar pre-procesar la señal, eliminar ruido de fondo, etc... darle mas contraste previo entre señal y silencio
          # para encontrar las secciones acá SI conviene tener los graves y menos definidos los ataques, que se vea mejor el "bloque" vs el silencio
          secciones = li.effects.split(data, top_db=30, frame_length=8192)  # top_db y frame_length son los parametros mas importantes
          #plt.subplots(figsize=(18, 3))
          #plt.plot(data)
          #plt.vlines(secciones, min(data), max(data), ls='dashed', color='red')

          # saco el bpm promedio de cada seccion
          bpm_medios = []
          for seccion in secciones:
            audio_seccion = signal.filtfilt(b,a, data[seccion[0]:seccion[1]])**2
            peaks, _ = signal.find_peaks(audio_seccion, distance = int(bpm_samples*0.9), threshold = 0.000001)
            bpm_medio = 60 * (sr / np.mean(np.diff(peaks)))   # media de las distancias entre picos, basicamente su frecuencia
            bpm_medios.append(bpm_medio)

            #plt.subplots(figsize=(12, 1))
            #plt.plot(audio_seccion)
            #plt.vlines(peaks, min(audio_seccion), max(audio_seccion), ls='dashed', color='red')
            #plt.title(f'BPM: {bpm_medio}')
            #plt.show()

          #print(bpm_medios)
          print(str(p)+'_'+str(t)+'_'+str(g)+' BPM MEDIO:',np.mean(bpm_medios))
          data = [p, 'GTR'+str(g), condicion, silencio, t, np.mean(bpm_medios)]
          writer.writerow(data)