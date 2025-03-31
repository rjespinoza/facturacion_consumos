import streamlit as st
import polars as pl
<<<<<<< HEAD
from openpyxl import Workbook
=======
import fastexcel
>>>>>>> 3fdfc4625e05feb13d4ca970f1ff4f99e3480f68
import bcrypt
import io
import os
import tempfile
import re

# Función para verificar el usuario y contraseña
def check_password():
    """Función para autenticar al usuario."""
    def password_entered():
        if bcrypt.checkpw(st.session_state["username"].encode("utf-8"), PASSWORD_CORRECTO):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # No almacenar la contraseña en la sesión
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", key="password", on_change=password_entered)
        return False
    
    elif not st.session_state["password_correct"]:
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", key="password", on_change=password_entered)
        st.error("Usuario/contraseña incorrectos")
        return False
    else:
        return True
    
# Datos de usuario (¡Importante! Cambia esto por un sistema de almacenamiento seguro)
USUARIO_CORRECTO = "admin"
PASSWORD_CORRECTO = bcrypt.hashpw("admin".encode("utf-8"), bcrypt.gensalt())

# Interfaz Principal
st.title("Extracción y filtrado de datos XLSB (Mes/Año)")

if check_password():
    # Instrucciones principales
    st.header("Cargar archivo XLSB")
    st.write(
        "Por favor, carga un archivo XLSB para extraer y filtrar los datos por mes y año."
        " Asegúrate de que el archivo contenga la hoja correcta con las columnas necesarias."
    )
    uploaded_file = st.file_uploader("Cargar archivo XLSB", type="xlsb")

    if uploaded_file is not None:
        try:
            # Configuración fija
            HOJA_FIJA = 'Libro Fac.Emitidas MM 2025'
            COLUMNAS_FIJAS = ['CUPS', 'Tipo factura', 'Fecha factura', 'Fecha inicial', 'Fecha final', 'Num. días', 'Tarifa', 'Total término variable (kWh)']

            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name

            # Leer el archivo y cargar los datos
            df = pl.read_excel(tmp_file_path, sheet_name=HOJA_FIJA).select(COLUMNAS_FIJAS)
            df = df.drop_nulls()

            # No filtramos por Año-Mes, acumulamos todos los datos
            df_filtered = df.filter(pl.col("Tipo factura") == "Normal")

            # Mostrar los datos filtrados
            st.header("Datos filtrados")
            st.dataframe(df_filtered.head())

            # Generar tablas pivoteadas acumulando por mes
            df_grouped = df_filtered.with_columns(
                pl.col('Fecha inicial').dt.strftime('%Y-%m').alias('Mes')
            ).group_by(['Tarifa', 'Mes']).agg([ 
                pl.col('Num. días').sum().alias('Suma de num. dias'),
                pl.col('CUPS').count().alias('Cuenta de CUPS'),
                pl.col('Total término variable (kWh)').sum().alias('Suma de kWh')
            ])

            df_pivot_num_dias = df_grouped.pivot(values='Suma de num. dias', index='Tarifa', on='Mes', sort_columns=True)
            df_pivot_cuenta_cups = df_grouped.pivot(values='Cuenta de CUPS', index='Tarifa', on='Mes', sort_columns=True)
            df_pivot_suma_kwh = df_grouped.pivot(values='Suma de kWh', index='Tarifa', on='Mes', sort_columns=True)

            # Ordenar las filas usando la función personalizada
            df_pivot_num_dias = df_pivot_num_dias.sort(by=pl.col("Tarifa"))
            df_pivot_cuenta_cups = df_pivot_cuenta_cups.sort(by=pl.col("Tarifa"))
            df_pivot_suma_kwh = df_pivot_suma_kwh.sort(by=pl.col("Tarifa"))

            # Mostrar los datos filtrados
            st.header("Tablas Generadas. Generando fichero Excel...")

<<<<<<< HEAD
            # Guardar los datos en Excel con openpyxl
            output = io.BytesIO()

            wb_out = Workbook()

            # Hoja 'raw_data' con los datos filtrados
            ws_raw_data = wb_out.active
            ws_raw_data.title = "raw_data"
            ws_raw_data.append(list(df_filtered.columns))
            for row in df_filtered.to_numpy():
                ws_raw_data.append(list(row))

            # Hoja 'consumos' con las tablas pivot
            ws_consumos = wb_out.create_sheet(title="consumos")

            def write_dataframe(ws, df, start_row):
                """Función auxiliar para escribir un DataFrame en la hoja de Excel."""
                ws.append(list(df.columns))  # Escribe los encabezados de las columnas
                for row in df.to_pandas().itertuples(index=False):
                    ws.append(row)
                return start_row + len(df) + 3  # Deja una fila vacía

            start_row = 1
            ws_consumos.append(["Tabla: Suma de num. dias"])
            start_row = write_dataframe(ws_consumos, df_pivot_num_dias, start_row)

            ws_consumos.append(["Tabla: Cuenta de CUPS"])
            start_row = write_dataframe(ws_consumos, df_pivot_cuenta_cups, start_row)

            ws_consumos.append(["Tabla: Suma de kWh"])
            start_row = write_dataframe(ws_consumos, df_pivot_suma_kwh, start_row)

            # Guardar el archivo
            wb_out.save(output)
=======
            # Guardar los datos en Excel con fastexcel
            output = io.BytesIO()

            # Usamos fastexcel para escribir el archivo Excel
            with fastexcel.open(output) as writer:
                # Hoja 'raw_data' con los datos filtrados
                worksheet_raw_data = writer.new_sheet('raw_data')
                worksheet_raw_data.append(list(df_filtered.columns))
                for row in df_filtered.to_numpy():
                    worksheet_raw_data.append(list(row))

                # Hoja 'consumos' con las tablas pivot
                worksheet_consumos = writer.new_sheet('consumos')
                
                # Función para escribir dataframes
                def write_dataframe(worksheet, df):
                    """Escribe un DataFrame en una hoja de Excel."""
                    worksheet.append(list(df.columns))
                    for row in df.to_pandas().itertuples(index=False):
                        worksheet.append(row)

                worksheet_consumos.append(['Tabla: Suma de num. dias'])
                write_dataframe(worksheet_consumos, df_pivot_num_dias)

                worksheet_consumos.append(['Tabla: Cuenta de CUPS'])
                write_dataframe(worksheet_consumos, df_pivot_cuenta_cups)

                worksheet_consumos.append(['Tabla: Suma de kWh'])
                write_dataframe(worksheet_consumos, df_pivot_suma_kwh)

>>>>>>> 3fdfc4625e05feb13d4ca970f1ff4f99e3480f68
            output.seek(0)

            # Botón para descargar el archivo
            st.download_button(
                label="Descargar datos filtrados",
                data=output,
                file_name="datos_filtrados.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            if 'tmp_file_path' in locals():
                os.remove(tmp_file_path)
