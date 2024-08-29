from essentia.standard import *
from tempfile import TemporaryDirectory
import csv

#Funcion que hace todo para medir el onset
def medirOnsets(audio1, audio2,pareja, condicion, silencio, trial):
    # 1. Compute the onset detection function (ODF).
    # The OnsetDetection algorithm provides various ODFs.
    od_hfc1 = OnsetDetection(method='hfc')
    od_complex1 = OnsetDetection(method='complex')

    od_hfc2 = OnsetDetection(method='hfc')
    od_complex2 = OnsetDetection(method='complex')

    # We need the auxilary algorithms to compute magnitude and phase.
    w1 = Windowing(type='square')
    fft1 = FFT() # Outputs a complex FFT vector.
    c2p1 = CartesianToPolar() # Converts it into a pair of magnitude and phase vectors.

    w2 = Windowing(type='square')
    fft2 = FFT() # Outputs a complex FFT vector.
    c2p2 = CartesianToPolar() # Converts it into a pair of magnitude and phase vectors.

    # Compute both ODF frame by frame. Store results to a Pool.
    pool1 = essentia.Pool()
    for frame1 in FrameGenerator(audio1, frameSize=1024, hopSize=512):
        magnitude, phase = c2p1(fft1(w1(frame1)))
        pool1.add('odf1.hfc', od_hfc1(magnitude, phase))
        pool1.add('odf1.complex', od_complex1(magnitude, phase))

    pool2 = essentia.Pool()
    for frame2 in FrameGenerator(audio2, frameSize=1024, hopSize=512):
        magnitude, phase = c2p2(fft2(w2(frame2)))
        pool2.add('odf2.hfc', od_hfc2(magnitude, phase))
        pool2.add('odf2.complex', od_complex2(magnitude, phase))

    # 2. Detect onset locations.
    onsets1 = Onsets()
    onsets2 = Onsets()

    onsets_hfc1 = onsets1(# This algorithm expects a matrix, not a vector.
                        essentia.array([pool1['odf1.hfc']]),
                        # You need to specify weights, but if we use only one ODF
                        # it doesn't actually matter which weight to give it
                        [1])

    onsets_complex1 = onsets1(essentia.array([pool1['odf1.complex']]), [1])



    onsets_hfc2 = onsets2(# This algorithm expects a matrix, not a vector.
                        essentia.array([pool2['odf2.hfc']]),
                        # You need to specify weights, but if we use only one ODF
                        # it doesn't actually matter which weight to give it
                        [1])

    onsets_complex2 = onsets2(essentia.array([pool2['odf2.complex']]), [1])

    #print(onsets_hfc2)

    # Add onset markers to the audio and save it to a file.
    # We use beeps instead of white noise and stereo signal as it's more distinctive.

    # We want to keep beeps in a separate audio channel.
    # Add them to a silent audio and use the original audio as another channel. Mux both into a stereo signal.
    silence1 = [0.] * len(audio1)

    beeps_hfc1 = AudioOnsetsMarker(onsets=onsets_hfc1, type='beep')(silence1)
    beeps_complex1 = AudioOnsetsMarker(onsets=onsets_complex1, type='beep')(silence1)

    audio_hfc1 = StereoMuxer()(audio1, beeps_hfc1)
    audio_complex1 = StereoMuxer()(audio1, beeps_complex1)



    silence2 = [0.] * len(audio2)

    beeps_hfc2 = AudioOnsetsMarker(onsets=onsets_hfc2, type='beep')(silence2)
    beeps_complex2 = AudioOnsetsMarker(onsets=onsets_complex2, type='beep')(silence2)

    audio_hfc2 = StereoMuxer()(audio2, beeps_hfc2)
    audio_complex2 = StereoMuxer()(audio2, beeps_complex2)


    # Write audio to files in a temporary directory.
    temp_dir = TemporaryDirectory()
    AudioWriter(filename=temp_dir.name + '/hfc_stereo1.wav', format='wav')(audio_hfc1)
    AudioWriter(filename=temp_dir.name + '/complex_stereo1.wav', format='wav')(audio_complex1)


    AudioWriter(filename=temp_dir.name + '/hfc_stereo2.wav', format='wav')(audio_hfc2)
    AudioWriter(filename=temp_dir.name + '/complex_stereo2.wav', format='wav')(audio_complex2)

    import IPython
    import matplotlib.pyplot as plt
    import numpy

    n_frames1 = len(pool1['odf1.hfc'])
    frames_position_samples = numpy.array(range(n_frames1)) * 512

    fig, ((ax1,ax2)) = plt.subplots(2, 1, sharex=True, sharey=False, figsize=(5, 6))

    #Obtengo el largo de los audios
    time1 = numpy.linspace(
            0, # start
            len(audio1) / 44100,
            num = len(audio1)
        )

    ax1.set_title('Pareja'+str(pareja)+' '+ str(condicion) + ' ' + "Silencio:" + str(silencio) + ' ' + 'Trial'+str(trial)+' '+'Guitarra 1 / Guitarra 2')
    ax1.plot(time1, audio1)

    #Contador y Old para la primera guitarra
    contador1 = 0
    old1 = 0

    #Aca voy guardando los onsets de la guitarra 1
    onset_gtr1 = []

    #Imprimo que pareja y que trial estoy corriendo
    print("Pareja: "+str(pareja))
    print("Trial: "+str(trial))
    print("Condicion: "+str(condicion))
    print("Silencio: "+str(silencio))
    

    #Este loop con if me ayuda a filtrar los onsets de la guitarra 1
    for onset1 in onsets_hfc1:
        if(contador1==0):
            ax1.axvline(x=onset1, color='magenta')
            #print(onset1)
            onset_gtr1.append(onset1)
        if(contador1>0):
            if((onset1 - old1) > 1):
                ax1.axvline(x=onset1, color='magenta')  
                #print(onset1)
                onset_gtr1.append(onset1) 
        old1 = onset1
        contador1 += 1

    #Seteo los nombres de los ejes por si quiero plotear
    ax1.set_xlabel("Tiempo en Seg.")
    ax1.set_ylabel("Amplitud")
    ax2.plot(time1, audio2)

    #Contador y old para la guitarra 2
    #Arranca en 1 para no mostrar el primer onset que no se por que esta corrido
    contador2 = 1
    old2 = 0
    #Aca voy guardando los onsets de la guitarra 2
    onset_gtr2 = []

    #Este loop con if me ayuda a filtrar los onsets de la guitarra 2
    for onset2 in onsets_hfc2:
        if(contador2==0):
            ax2.axvline(x=onset2, color='magenta')
            #print(onset2)
            #Aca se guardan los onsets
            onset_gtr2.append(onset2)
        if(contador2>0):
            
            if((onset2 - old2) > 1):
                ax2.axvline(x=onset2, color='magenta') 
                #print(onset2)
                #Aca se guardan los onsets
                onset_gtr2.append(onset2)  
        old2 = onset2
        contador2 += 1


##########################################################
    #Aca calculo e imprimo todo lo neceario
    
    #data = ['Pareja', 'Guitarrista', 'Condicion', 'Silencio', 'Trial', 'ONSET']

    #Imprimo tanto Guitarra 1 como Guitarra 2 por que lombera lo quiere asi
    #Se imprime las diferencias en valor absoluto para las tres repeticiones y se agregan 
    #al CSV
    data = [pareja, "GTR1", condicion, silencio, trial, abs(onset_gtr1[1]-onset_gtr2[1])]
    writer.writerow(data)
    data = [pareja, "GTR2", condicion, silencio, trial, abs(onset_gtr1[1]-onset_gtr2[1])]
    writer.writerow(data)

    data = [pareja, "GTR1", condicion, silencio, trial, abs(onset_gtr1[2]-onset_gtr2[2])]
    writer.writerow(data)
    data = [pareja, "GTR2", condicion, silencio, trial, abs(onset_gtr1[2]-onset_gtr2[2])]
    writer.writerow(data)

    data = [pareja, "GTR1", condicion, silencio, trial, abs(onset_gtr1[3]-onset_gtr2[3])]
    writer.writerow(data)
    data = [pareja, "GTR2", condicion, silencio, trial, abs(onset_gtr1[3]-onset_gtr2[3])]
    writer.writerow(data)
    
##########################################################
    #También seteo los ejes de la grafica de la guitarra 2
    ax2.set_xlabel("Tiempo en Seg.")
    ax2.set_ylabel("Amplitud")
    
    #Comento y descomento el ploteo
    #plt.show()

    #Deleteo la variable de plot para que no consuma memoria
    #del(plt)



###########################################################################
def analisis(condicion, silencio):
    for p in range(1,17):
        #Este loop es para iterar trials o repeticiones
        for t in range(1,4):
            # Cargo los archivos de audio dependiendo de la pareja (p) y el trial (c)
            audio1 = MonoLoader(filename='audios_nuevos2023/P'+str(p)+'_'+condicion+'_'+silencio+'_GTR1_00'+str(t)+'.wav')()
            audio2 = MonoLoader(filename='audios_nuevos2023/P'+str(p)+'_'+condicion+'_'+silencio+'_GTR2_00'+str(t)+'.wav')()

            print("###############################################################")
            print('audios_nuevos2023/P'+str(p)+'_'+condicion+'_'+silencio+'_GTR1_00'+str(t)+'.wav')
            print('audios_nuevos2023/P'+str(p)+'_'+condicion+'_'+silencio+'_GTR2_00'+str(t)+'.wav')
            #Esta funcion recibe:
            #   los audios de la guitarra
            #   el numero de parejas p
            #   si estan juntos o separados
            #   silencio (1:SS, 2:SC, 3:SL, 4SXL. No se usa sin silencio acá)

            if condicion == 'J':
                ver_sin_ver = 'VER'
            
            if condicion == 'S':
                ver_sin_ver = 'SIN VER'

            if silencio == 'SC':
                sil = 2

            if silencio == 'SL':
                sil = 3

            if silencio == 'SXL':
                sil = 4

            medirOnsets(audio1, audio2, p, ver_sin_ver, sil, t)
            print("###############################################################")
            #Cuando termino cada vuelta deleteo la variable para que no se llene la memoria
            del audio1
            del audio2
###########################################################################

#Este es el header del CSV
header = ['Pareja', 'Guitarrista', 'Condicion', 'Silencio', 'Trial', 'ONSET']
data = []
#Se carga el array data de esta manera
#data = ['Pareja', 'Guitarrista', 'Condicion', 'Silencio', 'Trial', 'ONSET']

#Abrimos el archivo y corremos los procesos, a medida que vamos cargando la data
with open('onsets_S_SXL.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)

    #Escribimos el header
    writer.writerow(header)

    #analisis('J', 'SC')
    #analisis('S', 'SC')
    #analisis('J', 'SL')
    #analisis('S', 'SL')
    #analisis('J', 'SXL')
    analisis('S', 'SXL')