import matplotlib.pyplot as plt

# Definir variables iniciales
dilatacion = [0]
frecuencia_cardiaca = [140]
contracciones = [0]
tiempo = [0]

# Definir intervalo de actualización de los datos (en minutos)
intervalo = 1

# Configuración del gráfico
fig, ax = plt.subplots(nrows=4, ncols=1, figsize=(8, 10))
fig.suptitle('Partograma de seguimiento del trabajo de parto')

# Crear tabla para mostrar los datos
tabla_datos = ax[3].table(cellText=[[str(dilatacion[-1]), str(frecuencia_cardiaca[-1]), str(contracciones[-1]), 'Normal']],
                          colLabels=['Dilatación cervical (cm)', 'Frecuencia cardíaca fetal (lpm)', 'Contracciones uterinas (en 10 min)', 'Estado'],
                          loc='center', cellLoc='center')
tabla_datos.auto_set_font_size(False)
tabla_datos.set_fontsize(10)

# Función para actualizar los datos
def actualizar_datos():
    # Leer los nuevos datos de la interfaz de usuario
    nueva_dilatacion = float(input('\nIngrese la dilatación cervical actual (en cm): '))
    nueva_frecuencia = int(input('Ingrese la frecuencia cardíaca fetal actual (en lpm): '))
    nuevas_contracciones = int(input('Ingrese el número de contracciones uterinas en los últimos 10 min: '))

    # Agregar los nuevos datos a las listas correspondientes
    dilatacion.append(nueva_dilatacion)
    frecuencia_cardiaca.append(nueva_frecuencia)
    contracciones.append(nuevas_contracciones)

    # Actualizar el tiempo transcurrido
    tiempo_transcurrido = tiempo[-1] + intervalo / 60
    tiempo.append(tiempo_transcurrido)

    # Actualizar los gráficos
    ax[0].plot(tiempo, dilatacion, 'bo-')
    ax[1].plot(tiempo, frecuencia_cardiaca, 'go-')
    ax[2].plot(tiempo, contracciones, 'ro-')

    # Actualizar la tabla de datos
    tabla_datos._cells[(0, 0)]._text.set_text(str(nueva_dilatacion))
    tabla_datos._cells[(0, 1)]._text.set_text(str(nueva_frecuencia))
    tabla_datos._cells[(0, 2)]._text.set_text(str(nuevas_contracciones))

    # Actualizar el estado del trabajo de parto
    estado = 'Normal'
    if nueva_dilatacion < 4:
        estado = 'Dilatación cervical lenta'
    elif nueva_frecuencia < 110:
        estado = 'Bradicardia fetal'
    elif nueva_frecuencia > 160:
        estado = 'Taquicardia fetal'
    elif nuevas_contracciones < 3:
        estado = 'Contracciones uterinas insuficientes'
    elif nuevas_contracciones > 5:
        estado = 'Contracciones uterinas frecuentes'

    tabla_datos._cells[(0, 3)]._text.set_text(str(estado))

    # Mostrar el gráfico actualizado y la tabla de datos
    plt.show()
    print('\nResumen del estado del trabajo de parto:')
    print(f'- Dilatación cervical: {nueva_dilatacion} cm')
    print(f'- Frecuencia cardíaca fetal: {nueva_frecuencia} lpm')
    print(f'- Contracciones uterinas en los últimos 10 min: {nuevas_contracciones}')
    print(f'- Estado del trabajo de parto: {estado}')

    # Guardar la figura en un archivo diferenciando cada partograma
    fig.savefig('partograma.png')
    fig.savefig('partograma.pdf')
    fig.savefig(f'partograma_{tiempo_transcurrido}.png')




# Actualizar los datos cada cierto intervalo de tiempo
while True:
    try:
        actualizar_datos()
        plt.pause(intervalo * 60)
    except KeyboardInterrupt:
        break

# Configuración adicional del gráfico
ax[0].set(xlabel='Tiempo (horas)', ylabel='Dilatación cervical (cm)')
ax[0].set_title("Gráfico de dilatación cervical")
ax[0].annotate("Interpretación: muestra el progreso de la dilatación cervical durante el trabajo de parto", xy=(0.05, 0.95), xycoords='axes fraction', fontsize=10, ha='left', va='top')
ax[0].grid()

# Marcar línea de alerta
alerta_dilatacion = 4 # cm de dilatación
ax[0].axhline(y=alerta_dilatacion, color='r', linestyle='--')
ax[0].annotate('Línea de alerta', xy=(0.1, alerta_dilatacion+0.5), color='r')

ax[1].set(xlabel='Tiempo (horas)', ylabel='Frecuencia cardíaca fetal (lpm)')
ax[1].set_title("Gráfico de frecuencia cardíaca fetal")
ax[1].annotate("Interpretación: muestra la frecuencia cardíaca fetal durante el trabajo de parto", xy=(0.05, 0.95), xycoords='axes fraction', fontsize=10, ha='left', va='top')
ax[1].grid()

# Marcar límites normales
limite_superior = 160 # lpm
limite_inferior = 110 # lpm
ax[1].axhline(y=limite_superior, color='r', linestyle='--')
ax[1].axhline(y=limite_inferior, color='r', linestyle='--')
ax[1].annotate('Límite superior', xy=(0.1, limite_superior+2), color='r')
ax[1].annotate('Límite inferior', xy=(0.1, limite_inferior-8), color='r')

ax[2].set(xlabel='Tiempo (horas)', ylabel='Contracciones uterinas (en 10 min)')
ax[2].set_title("Gráfico de contracciones uterinas")
ax[2].annotate("Interpretación: muestra la frecuencia de las contracciones uterinas durante el trabajo de parto", xy=(0.05, 0.95), xycoords='axes fraction', fontsize=10, ha='left', va='top')
ax[2].grid()

# Marcar límites normales
limite_contracciones = 5 # en 10 minutos
ax[2].axhline(y=limite_contracciones, color='r', linestyle='--')
ax[2].annotate('Límite normal', xy=(0.1, limite_contracciones+0.5), color='r')

# Configurar la tabla de datos
tabla_datos.scale(1, 2)
ax[3].axis('off')
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
