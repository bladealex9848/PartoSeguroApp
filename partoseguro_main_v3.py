import streamlit as st
from PIL import Image
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

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

# Esto recargará la página cada 30 segundos, lo que actualizará la cuenta regresiva
st_autorefresh(interval=30 * 1000, key="autorefresh")

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
        ultima_medicion_date = parse_fecha(ultima_medicion)
        if ultima_medicion_date:
            cuenta_regresiva = mostrar_cuenta_regresiva(ultima_medicion_date)
            if cuenta_regresiva == "00:00:00":
                st.sidebar.error(f"¡Hora de realizar nueva medición para {paciente[1]} (ID: {paciente[0]})!")
            else:
                st.sidebar.info(f"Próxima medición para {paciente[1]} (ID: {paciente[0]}) en: {cuenta_regresiva}")
        else:
            st.sidebar.error("No se pudo interpretar la última fecha de medición.")
    else:
        st.sidebar.warning(f"No hay mediciones registradas para {paciente[1]} (ID: {paciente[0]}).")

# Al inicio de tu script, añade estas líneas para el estilo CSS
st.markdown(
    """
    <style>
    .paciente-container {
        border-radius: 10px;
        box-shadow: 5px 5px 20px rgba(0,0,0,0.1);
        padding: 20px;
        margin-bottom: 20px;
        transition: box-shadow 0.3s ease-in-out;
        background-color: #f8f9fa;
    }
    .paciente-container:hover {
        box-shadow: 5px 5px 30px rgba(0,0,0,0.2);
    }
    .paciente-header {
        color: #4f8bf9;
        margin-bottom: 20px;
        font-weight: 500;
    }
    .grafica {
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .grafica-title {
        text-align: center;
        margin-top: 10px;
        font-weight: bold;
        color: #333;
    }
    .diagnostico-recomendacion {
        margin-top: 20px;
        padding: 10px;
        background-color: #e9ecef;
        border-left: 5px solid #4f8bf9;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Visualización de Datos y Generación de Diagnósticos
for paciente in c.execute("SELECT * FROM pacientes").fetchall():
    # Contenedor personalizado para cada paciente
    with st.container():
        # Contenedor personalizado para cada paciente
        st.markdown(f"<div class='paciente-container'>", unsafe_allow_html=True)
        
        # Subtítulo con estilo personalizado
        st.markdown(f"<h2 class='paciente-header'>Paciente: {paciente[1]} (ID: {paciente[0]}) - Edad: {paciente[2]} - FUM: {paciente[3]} - Patología: {paciente[4]}</h2>", unsafe_allow_html=True)
        
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
            
            # Añadir una clave única para cada botón de descarga
            #unique_key = f"download_{paciente[0]}"  # Usando el ID del paciente
            #st.download_button(
            #    label="Descargar mediciones como CSV",
            #    data=mediciones_df.to_csv(index=False),
            #    file_name=f'mediciones_{paciente[0]}.csv',
            #    mime='text/csv',
            #    key=unique_key
            #)

            # Graficar cada métrica en una gráfica separada
            fig, axes = plt.subplots(3, 1, figsize=(10, 15))
            
            # Añadir gráficas al contenedor de figuras
            for i, (ax, column, color, title) in enumerate(zip(
                    axes,
                    ['dilatacion', 'frecuencia_cardiaca', 'contracciones'],
                    ['blue', 'red', 'green'],
                    ['Evolución de la Dilatación', 'Evolución de la Frecuencia Cardíaca Fetal', 'Evolución de las Contracciones']
                )):
                ax.plot(mediciones_df['Fecha'], mediciones_df[column], color=color)
                ax.set_title(title)
                ax.set_xlabel('Fecha')
                ax.set_ylabel(column)
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
                ax.xaxis.set_tick_params(rotation=45)

                # Añadir estilo a la gráfica
                ax.grid(True)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
            
            # Mostrar las figuras
            plt.tight_layout()
            st.pyplot(fig)
        
            # Diagnóstico y Recomendación
            ultima_medicion = mediciones_df.iloc[-1]
            diagnostico, recomendacion = generar_diagnostico(
                ultima_medicion["dilatacion"],
                ultima_medicion["frecuencia_cardiaca"],
                ultima_medicion["contracciones"],
                ultima_medicion["presion_arterial"]
            )
            
            # Mostrar diagnóstico y recomendación con estilo personalizado
            st.markdown(f"<div class='diagnostico-recomendacion'><strong>Diagnóstico:</strong> {diagnostico}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='diagnostico-recomendacion'><strong>Recomendación:</strong> {recomendacion}</div>", unsafe_allow_html=True)
        
        else:
            st.write("No hay mediciones disponibles para este paciente.")
            
        # Cierra el contenedor personalizado
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("---")  # Separador visual para la siguiente sección    
     
# Cerrar conexión con la base de datos
conn.close()

# Sección de footer.
st.sidebar.markdown('---')
st.sidebar.subheader('Creado por:')
st.sidebar.markdown('Alexander Oviedo Fadul')
st.sidebar.markdown("[GitHub](https://github.com/bladealex9848) | [Website](https://alexander.oviedo.isabellaea.com/) | [Instagram](https://www.instagram.com/alexander.oviedo.fadul) | [Twitter](https://twitter.com/alexanderofadul) | [Facebook](https://www.facebook.com/alexanderof/) | [WhatsApp](https://api.whatsapp.com/send?phone=573015930519&text=Hola%20!Quiero%20conversar%20contigo!%20)")