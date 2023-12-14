import streamlit as st
from PIL import Image
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# Configuración inicial de la página de Streamlit.
st.set_page_config(
    page_title="PartoSeguro Monitor",
    page_icon="🤰",
    initial_sidebar_state='expanded',
    menu_items={
        'Get Help': 'https://www.isabellaea.com',
        'Report a bug': None,
        'About': "PartoSeguro Monitor es una aplicación para el seguimiento del trabajo de parto."
    }
)

# Carga y muestra el logo de la aplicación.
logo = Image.open('img/logo.png')
st.image(logo, width=250)

# Título principal y descripción de la aplicación.
st.title('PartoSeguro Monitor')
st.write("""
Esta aplicación permite el seguimiento continuo y detallado del trabajo de parto, 
registrando y visualizando datos clave como la dilatación cervical, frecuencia cardíaca fetal y contracciones.
""")

# Conexión con la base de datos SQLite.
conn = sqlite3.connect('partoseguro.db')
c = conn.cursor()

# Creación de las tablas en la base de datos si no existen.
# Tabla de pacientes.
c.execute('''
CREATE TABLE IF NOT EXISTS pacientes (
    id TEXT PRIMARY KEY,
    nombre TEXT,
    edad INTEGER,
    fum DATE,
    patologia TEXT,
    FOREIGN KEY(patologia) REFERENCES patologias(nombre)
)
''')

# Tabla de mediciones.
c.execute('''
CREATE TABLE IF NOT EXISTS mediciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_paciente TEXT,
    fecha TIMESTAMP,
    dilatacion INTEGER,
    frecuencia_cardiaca INTEGER,
    contracciones INTEGER,
    presion_arterial TEXT,
    FOREIGN KEY(id_paciente) REFERENCES pacientes(id)
)
''')

# Tabla de patologías.
c.execute('''
CREATE TABLE IF NOT EXISTS patologias (
    nombre TEXT PRIMARY KEY
)
''')

# Inserción de patologías comunes en la base de datos.
patologias_comunes = ["Hipertensión", "Diabetes Gestacional", "Anemia", "Tiroides", "Preeclampsia", "Sin patologías"]
c.execute("SELECT * FROM patologias")
if len(c.fetchall()) == 0:
    for patologia in patologias_comunes:
        c.execute("INSERT INTO patologias (nombre) VALUES (?)", (patologia,))
    conn.commit()

# Función para agregar pacientes a la base de datos.
def agregar_paciente(id, nombre, edad, fum, patologia):
    c.execute("INSERT INTO pacientes (id, nombre, edad, fum, patologia) VALUES (?, ?, ?, ?, ?)", (id, nombre, edad, fum, patologia))
    conn.commit()

# Función para agregar mediciones a la base de datos.
def agregar_medicion(id_paciente, fecha_hora, dilatacion, frecuencia_cardiaca, contracciones, presion_arterial):
    c.execute("INSERT INTO mediciones (id_paciente, fecha, dilatacion, frecuencia_cardiaca, contracciones, presion_arterial) VALUES (?, ?, ?, ?, ?, ?)", (id_paciente, fecha_hora, dilatacion, frecuencia_cardiaca, contracciones, presion_arterial))
    conn.commit()

# Función para generar diagnósticos y recomendaciones basados en las mediciones.
def generar_diagnostico(dilatacion, frecuencia_cardiaca, contracciones, presion_arterial):
    estado = 'Normal'
    recomendacion = "Continuar con el monitoreo rutinario y mantener las prácticas estándar de cuidado prenatal."
    
    # Evaluar la dilatación cervical
    if dilatacion < 4:
        estado = 'Dilatación cervical lenta'
        recomendacion = "Monitorear progreso más de cerca."
    elif dilatacion >= 10:
        estado = 'Dilatación completa, preparar para el parto'
        recomendacion = "Preparar para el parto inminente y notificar al equipo médico."
    
    # Evaluar la frecuencia cardíaca fetal
    if frecuencia_cardiaca < 110:
        estado = 'Bradicardia fetal'
        recomendacion = "Requiere atención inmediata y evaluación médica."
    elif frecuencia_cardiaca > 160:
        estado = 'Taquicardia fetal'
        recomendacion = "Evaluar causas y tomar acciones según protocolo médico."
    
    # Evaluar las contracciones uterinas
    if contracciones < 3:
        estado = 'Contracciones uterinas insuficientes'
        recomendacion = "Considerar estimulación si es indicado y está dentro del plan de parto."
    elif contracciones > 5:
        estado = 'Contracciones uterinas frecuentes'
        recomendacion = "Evaluar para descartar parto prematuro o hiperestimulación."
    
    # Evaluar la presión arterial
    try:
        sistolica, diastolica = map(int, presion_arterial.split('/'))
        if sistolica < 90 or diastolica < 60:
            estado = 'Hipotensión'
            recomendacion = "Aumentar la monitorización, asegurar hidratación adecuada y considerar evaluación médica."
        elif sistolica > 140 or diastolica > 90:
            estado = 'Hipertensión'
            recomendacion = "Requerir evaluación médica adicional y considerar manejo para hipertensión."
    except ValueError:
        estado = 'Error en la medición de la presión arterial'
        recomendacion = "Verificar la entrada de la presión arterial y volver a medir."

    return estado, recomendacion

# Función para parsear fechas de diferentes formatos.
def parse_fecha(fecha_str):
    # Asegúrate de que la entrada es una cadena, ya que strptime espera una cadena
    if isinstance(fecha_str, str):
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                return datetime.strptime(fecha_str, fmt)
            except ValueError:
                continue
    return None  # Devuelve None si no se reconoce el formato o no es una cadena

# Función para calcular la diferencia de tiempo y mostrar una cuenta regresiva
def mostrar_cuenta_regresiva(fecha_ultima_medicion, intervalo_minutos=30):
    ahora = datetime.now()
    tiempo_transcurrido = ahora - fecha_ultima_medicion
    tiempo_restante = timedelta(minutes=intervalo_minutos) - tiempo_transcurrido
    if tiempo_restante.total_seconds() > 0:
        # Calcular horas y minutos para la cuenta regresiva
        horas, rem = divmod(tiempo_restante.seconds, 3600)
        minutos, segundos = divmod(rem, 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    else:
        return "00:00:00"

# Sección de la interfaz de usuario para agregar pacientes.
st.sidebar.title("Agregar Paciente")
id_paciente = st.sidebar.text_input("ID del Paciente", placeholder="Ejemplo: 12345678")
nombre_paciente = st.sidebar.text_input("Nombre del Paciente", placeholder="Ejemplo: Maria Perez")
edad_paciente = st.sidebar.number_input("Edad del Paciente", min_value=0, max_value=100, step=1, value=30)
fum_paciente = st.sidebar.date_input("Fecha de Última Menstruación")
c.execute("SELECT nombre FROM patologias")
patologias_opciones = [p[0] for p in c.fetchall()]
patologia_paciente = st.sidebar.selectbox("Patología de Base", patologias_opciones)
if st.sidebar.button("Agregar Paciente"):
    agregar_paciente(id_paciente, nombre_paciente, edad_paciente, fum_paciente, patologia_paciente)
    st.sidebar.success("Paciente agregado con éxito.")

# Sección de la interfaz de usuario para agregar mediciones.
st.sidebar.title("Agregar Mediciones")
c.execute("SELECT id FROM pacientes")
lista_pacientes = [id[0] for id in c.fetchall()]
id_paciente_medicion = st.sidebar.selectbox("Seleccionar Paciente", lista_pacientes, key="paciente_seleccionado")
fecha_medicion = st.sidebar.date_input("Fecha de Medición", key="fecha_medicion")
hora_medicion = st.sidebar.time_input("Hora de Medición", key="hora_medicion")
fecha_hora_medicion = datetime.combine(fecha_medicion, hora_medicion)
dilatacion = st.sidebar.number_input("Dilatación cervical (cm)", min_value=0, max_value=10, step=1, key="dilatacion", value=3)
frecuencia_cardiaca = st.sidebar.number_input("Frecuencia Cardíaca Fetal (latidos/min)", min_value=60, max_value=200, step=1, key="frecuencia_cardiaca", value=120)
contracciones = st.sidebar.number_input("Contracciones uterinas (en 10 min)", min_value=0, max_value=30, step=1, key="contracciones", value=5)
presion_arterial = st.sidebar.text_input("Presión Arterial (mmHg)", key="presion_arterial", placeholder="Ejemplo: 120/80")
if st.sidebar.button("Registrar Medicion", key="boton_registrar_medicion"):
    # Validación de la presión arterial
    try:
        sistolica, diastolica = map(int, presion_arterial.split('/'))
        if sistolica < 50 or diastolica < 30:
            st.sidebar.error("La presión arterial sistólica y diastólica parece muy baja.")
        elif sistolica > 250 or diastolica > 150:
            st.sidebar.error("La presión arterial sistólica y diastólica parece muy alta.")
        else:
            agregar_medicion(id_paciente_medicion, fecha_hora_medicion, dilatacion, frecuencia_cardiaca, contracciones, presion_arterial)
            st.sidebar.success("Medición registrada con éxito.")
    except ValueError:
        st.sidebar.error("Por favor ingresa la presión arterial en el formato correcto (sistólica/diastólica).")

# Sección de la interfaz de usuario para alertas y cuenta regresiva
st.sidebar.title("Próximas Mediciones")
for paciente in c.execute("SELECT id, nombre FROM pacientes").fetchall():
    ultima_medicion = c.execute("SELECT MAX(fecha) FROM mediciones WHERE id_paciente = ?", (paciente[0],)).fetchone()[0]
    if ultima_medicion:
        try:
            ultima_medicion_date = parse_fecha(ultima_medicion)
            if ultima_medicion_date and datetime.now() >= ultima_medicion_date + timedelta(minutes=30):
                cuenta_regresiva = mostrar_cuenta_regresiva(ultima_medicion_date)
                st.sidebar.warning(f"Realizar nueva medición para {paciente[1]} (ID: {paciente[0]}). Siguiente en: {cuenta_regresiva}")
            else:
                cuenta_regresiva = mostrar_cuenta_regresiva(ultima_medicion_date)
                st.sidebar.info(f"Próxima medición para {paciente[1]} (ID: {paciente[0]}) en: {cuenta_regresiva}")
        except ValueError as e:
            st.sidebar.error(f"Error en el formato de fecha para {paciente[1]} (ID: {paciente[0]}): {e}")

# Visualización de Datos y Generación de Diagnósticos
for paciente in c.execute("SELECT * FROM pacientes").fetchall():
    st.subheader(f"Paciente: {paciente[1]} (ID: {paciente[0]}) - Edad: {paciente[2]} - FUM: {paciente[3]} - Patología: {paciente[4]}")
    
    # Obtener las mediciones del paciente de la base de datos
    mediciones_df = pd.read_sql_query(
        "SELECT id, fecha, dilatacion, frecuencia_cardiaca, contracciones, presion_arterial FROM mediciones WHERE id_paciente = ? ORDER BY fecha",
        conn,
        params=(paciente[0],)
    )

    # Verificar si hay mediciones disponibles para el paciente
    if not mediciones_df.empty:
        # Conversión y limpieza de la columna de fecha
        mediciones_df['Fecha'] = pd.to_datetime(mediciones_df['fecha']).dt.tz_localize(None)
        mediciones_df.drop(columns=['fecha'], inplace=True) # Eliminar la columna original para evitar duplicados

        # Mostrar la tabla de mediciones con la opción de descarga
        st.dataframe(mediciones_df)
        st.download_button(label="Descargar mediciones como CSV", data=mediciones_df.to_csv(index=False), file_name='mediciones.csv', mime='text/csv')

        # Graficar cada métrica en una gráfica separada
        fig, axes = plt.subplots(3, 1, figsize=(10, 15))
        mediciones_df.plot(x='Fecha', y='dilatacion', ax=axes[0], legend=False)
        axes[0].set_title('Evolución de la Dilatación')
        axes[0].set_ylabel('Dilatación (cm)')

        mediciones_df.plot(x='Fecha', y='frecuencia_cardiaca', ax=axes[1], legend=False, color='r')
        axes[1].set_title('Evolución de la Frecuencia Cardíaca Fetal')
        axes[1].set_ylabel('Frecuencia Cardíaca (latidos/min)')

        mediciones_df.plot(x='Fecha', y='contracciones', ax=axes[2], legend=False, color='g')
        axes[2].set_title('Evolución de las Contracciones')
        axes[2].set_ylabel('Contracciones (en 10 min)')

        # Ajustar el formato de fecha en el eje x
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            ax.xaxis.set_tick_params(rotation=45)

        st.pyplot(fig)

        # Diagnóstico y Recomendación
        ultima_medicion = mediciones_df.iloc[-1]
        diagnostico, recomendacion = generar_diagnostico(
            ultima_medicion["dilatacion"],
            ultima_medicion["frecuencia_cardiaca"],
            ultima_medicion["contracciones"],
            ultima_medicion["presion_arterial"]
        )
        st.subheader("Diagnóstico y Recomendación")
        st.write(f"Diagnóstico: {diagnostico}")
        st.write(f"Recomendación: {recomendacion}")

# Cerrar conexión con la base de datos
conn.close()

# Sección de footer.
st.sidebar.markdown('---')
st.sidebar.subheader('Creado por:')
st.sidebar.markdown('Alexander Oviedo Fadul')
st.sidebar.markdown("[GitHub](https://github.com/bladealex9848) | [Website](https://alexander.oviedo.isabellaea.com/) | [Instagram](https://www.instagram.com/alexander.oviedo.fadul) | [Twitter](https://twitter.com/alexanderofadul) | [Facebook](https://www.facebook.com/alexanderof/) | [WhatsApp](https://api.whatsapp.com/send?phone=573015930519&text=Hola%20!Quiero%20conversar%20contigo!%20)")