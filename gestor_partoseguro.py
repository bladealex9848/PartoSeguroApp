import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Conexión con la base de datos SQLite
conn = sqlite3.connect('partoseguro.db', check_same_thread=False)
c = conn.cursor()

# Funciones CRUD para la tabla 'pacientes'
def create_patient(id, nombre, edad, fum, patologia):
    c.execute("INSERT INTO pacientes (id, nombre, edad, fum, patologia) VALUES (?, ?, ?, ?, ?)", 
              (id, nombre, edad, fum, patologia))
    conn.commit()

def read_patients():
    return pd.read_sql("SELECT * FROM pacientes", conn)

def update_patient(id, nombre, edad, fum, patologia):
    c.execute("UPDATE pacientes SET nombre=?, edad=?, fum=?, patologia=? WHERE id=?", 
              (nombre, edad, fum, patologia, id))
    conn.commit()

def delete_patient(id):
    c.execute("DELETE FROM pacientes WHERE id=?", (id,))
    conn.commit()

# Funciones CRUD para 'mediciones'
def create_medicion(id_paciente, fecha, dilatacion, frecuencia_cardiaca, contracciones, presion_arterial):
    c.execute("INSERT INTO mediciones (id_paciente, fecha, dilatacion, frecuencia_cardiaca, contracciones, presion_arterial) VALUES (?, ?, ?, ?, ?, ?)", 
              (id_paciente, fecha, dilatacion, frecuencia_cardiaca, contracciones, presion_arterial))
    conn.commit()

def read_mediciones():
    return pd.read_sql("SELECT * FROM mediciones", conn)

# Funciones CRUD para 'patologias'
def create_patologia(nombre):
    c.execute("INSERT INTO patologias (nombre) VALUES (?)", (nombre,))
    conn.commit()

def read_patologias():
    return pd.read_sql("SELECT * FROM patologias", conn)

def delete_patologia(nombre):
    c.execute("DELETE FROM patologias WHERE nombre=?", (nombre,))
    conn.commit()

# UI de la aplicación Streamlit
st.title("Gestor de Base de Datos PartoSeguro")

# Selección de tablas
option = st.sidebar.selectbox("Elige una tabla para gestionar:", ('pacientes', 'mediciones', 'patologias'))

if option == 'pacientes':
    # Formulario para agregar un nuevo paciente
    with st.form(key='new_patient_form'):
        st.write("Agregar nuevo paciente")
        new_id = st.text_input("ID del Paciente")
        new_name = st.text_input("Nombre del Paciente")
        new_age = st.number_input("Edad del Paciente", min_value=0, max_value=100)
        new_fum = st.date_input("Fecha de Última Menstruación")
        new_patologia = st.text_input("Patología de Base")
        submit_button = st.form_submit_button(label='Agregar Paciente')
        if submit_button:
            create_patient(new_id, new_name, new_age, new_fum, new_patologia)

    # Mostrar los pacientes existentes
    st.write("Pacientes existentes:")
    st.write(read_patients())

    # Formulario para actualizar un paciente
    with st.form(key='update_patient_form'):
        st.write("Actualizar un paciente")
        update_id = st.text_input("ID del Paciente a actualizar")
        update_name = st.text_input("Nuevo Nombre")
        update_age = st.number_input("Nueva Edad", min_value=0, max_value=100)
        update_fum = st.date_input("Nueva Fecha de Última Menstruación")
        update_patologia = st.text_input("Nueva Patología")
        update_button = st.form_submit_button(label='Actualizar Paciente')
        if update_button:
            update_patient(update_id, update_name, update_age, update_fum, update_patologia)

    # Formulario para eliminar un paciente
    delete_id = st.text_input("ID del Paciente a eliminar")
    if st.button('Eliminar Paciente'):
        delete_patient(delete_id)

elif option == 'mediciones':
    # Funcionalidades para 'mediciones'
    with st.form(key='new_medicion_form'):
        st.write("Agregar nueva medición")
        new_id_paciente = st.selectbox("ID del Paciente", options=[p[0] for p in c.execute("SELECT id FROM pacientes").fetchall()])
        new_fecha = st.date_input("Fecha de la medición")
        new_dilatacion = st.number_input("Dilatación cervical (cm)", min_value=0, max_value=10)
        new_frecuencia_cardiaca = st.number_input("Frecuencia Cardíaca Fetal (latidos/min)", min_value=60, max_value=200)
        new_contracciones = st.number_input("Contracciones uterinas (en 10 min)", min_value=0, max_value=30)
        new_presion_arterial = st.text_input("Presión Arterial (mmHg)")
        submit_medicion_button = st.form_submit_button(label='Agregar Medición')
        if submit_medicion_button:
            create_medicion(new_id_paciente, new_fecha, new_dilatacion, new_frecuencia_cardiaca, new_contracciones, new_presion_arterial)

    st.write("Mediciones existentes:")
    st.write(read_mediciones())

elif option == 'patologias':
    # Funcionalidades para 'patologias'
    with st.form(key='new_patologia_form'):
        st.write("Agregar nueva patología")
        new_nombre_patologia = st.text_input("Nombre de la Patología")
        submit_patologia_button = st.form_submit_button(label='Agregar Patología')
        if submit_patologia_button:
            create_patologia(new_nombre_patologia)

    st.write("Patologías existentes:")
    st.write(read_patologias())

    delete_nombre_patologia = st.text_input("Nombre de la Patología a eliminar")
    if st.button('Eliminar Patología'):
        delete_patologia(delete_nombre_patologia)

# Cerrar la conexión a la base de datos
def close_connection():
    conn.close()
    st.sidebar.button("Cerrar la conexión a la base de datos", on_click=close_connection)