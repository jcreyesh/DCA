
import pandas as pd
import numpy as np
import plotly.express as px
import datetime
import streamlit as sl
import altair as alt
import plotly.io as pio

# wide-mode
sl.set_page_config(layout="wide")

# Sidebar
sl.title("Análisis de Curvas de Declinación")

# Subheader
sl.subheader("Carga de los datos", divider="gray")
file = sl.file_uploader("Seleccione la base de datos")
if file is not None:
    data = pd.read_csv(file, encoding="latin-1")
    data["fecha"] = pd.to_datetime(data["fecha"], format="YYYY/MM/DD")
    sl.write(data)

    # Subheader
    sl.subheader("Definición del pozo", divider="gray")
        
    col1, col2, col3, col4 = sl.columns([1, 1, 1, 1])
    with col1:
        lista_campo = list(data.campo.unique())
        select_campo = sl.selectbox("Campo", lista_campo)
        data = data[data["campo"] == select_campo]
    with col2:
        lista_yac = list(data.yacimiento.unique())
        select_yac = sl.selectbox("Yacimiento", lista_yac)
        data = data[data["yacimiento"] == select_yac]
    with col3:
        lista_pozo = list(data.pozo.unique())
        select_pozo = sl.selectbox("Pozo", lista_pozo)
        data = data[data["pozo"] == select_pozo]
    with col4:
        lista_fluido = list(data.unidad.unique())
        select_fluido = sl.selectbox("Fluido", lista_fluido)
        data = data[data["unidad"] == select_fluido]
    
    sl.subheader("Histórico de producción", divider="gray")
    
    # Function for plotting flow rate
    def plot_q(df, x, y):
        fig = px.line(df, x=x, y=y, markers=True, title= data["pozo"].values[0], labels={"q": "q - (Mb / MMPCD)"})
        fig.update_layout(title_x=0.4, title_y=0.85, plot_bgcolor="white")
        fig.update_traces(line_color="black", marker=dict(color="white", size=4.8, line=dict(width=1.2, color='black')))
        # fig.update_xaxes(mirror=True, ticks="outside", showline=True, linecolor="black", gridcolor="lightgrey")
        # fig.update_yaxes(mirror=True, ticks="outside", showline=True, linecolor="black", gridcolor="lightgrey")
        return sl.plotly_chart(fig)
    
    plot_q(data, data["fecha"], data["q"])
    
    sl.subheader("Definición del período de interés", divider="gray")

    date_1, date_2 = data["fecha"].values[0], data["fecha"].values[-1]
    start_date, end_date = sl.slider("Fechas:", min_value=date_1, max_value=date_2, value=(date_1, date_2), format="YYYY/MM/DD")
    sl.write(start_date, end_date)

elif file == None:
    sl.write("Aún no se ha cargado la Base de Datos.")




# df_pozo = data_pozos[data_pozos["Pozo"] == select_pozo]
# sl.write(df_pozo)
    


    

