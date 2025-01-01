
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import streamlit as sl
import altair as alt
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# wide-mode
sl.set_page_config(layout="wide")

# Sidebar
sl.title("Análisis de Curvas de Declinación")

# Subheader
sl.subheader("Carga de los datos", divider="gray")
file = sl.file_uploader("Seleccione la base de datos")
if file is not None:
    data = pd.read_csv(file, encoding="latin-1")
    data["fecha"] = pd.to_datetime(data["fecha"]).dt.date
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
    def plot_q(df, x, y, key):
        fig = px.line(df, x=x, y=y, markers=True, title= data["pozo"].values[0], labels={"q": "q - (Mb / MMPCD)"})
        fig.update_layout(title_x=0.4, title_y=0.85, plot_bgcolor="white")
        fig.update_traces(line_color="black", line_width=1.1, marker=dict(color="white", size=4.8, line=dict(width=1.2, color='black')))
        return sl.plotly_chart(fig, key = key)
    
    plot_q(data, data["fecha"], data["q"], 1)

    # Date range slider
    sl.subheader("Definición del período de interés", divider="gray")
    date_1 = data["fecha"].values[0]
    date_2 = data["fecha"].values[-1]
    start_date, end_date = sl.slider("Fechas:", min_value=date_1, max_value=date_2, value=(date_1, date_2), format="YYYY/MM/DD", 
                                    step=timedelta(days=1))

    start_date = start_date.replace(day=1)
    data = data[(data["fecha"] >= start_date) & (data["fecha"] <= end_date)]
    data.insert(0, "t", range(len(data)))
    
    # Computing D-constant
    time = data["t"]
    qi = data["q"].values[0]
    q = np.array([i if i != 0 else 1 for i in data["q"]])
    D1 = sum(time*np.log(qi/q))/(sum(time**2))

    # input constants
    col1, col2, col3, col4 = sl.columns([1, 1, 1, 1])
    with col1:
        qi = sl.number_input("Gasto inicial:", value=qi)
    with col2:
        d1 = sl.number_input("Constante D:", value=D1)
    with col3:
        b = sl.number_input("Constante b:", value=0.5)
    with col4:
        p_meses = sl.number_input("Proyección (meses):", value=12)
    
    sl.subheader("Resultados", divider="gray")

    # Fechas
    f1 = pd.to_datetime(data["fecha"].values[0])
    # f1 = datetime.date(f1)
    f2 = (pd.to_datetime(data["fecha"].values[-1]) + relativedelta(months=p_meses))
    # f2 = datetime.date(f2)
    fecha = pd.date_range(f1, f2, freq="MS")
    t = np.arange(len(fecha))
    
    # Declinación exponencial
    qo_exp = qi * np.exp(-D1 * t)
    Np_exp = 1/D1*(qi - qo_exp)
    
    # Declinación hiperbólica
    b = 0.65
    qo_hip = qi/(1 + D1*b*t)**(1/b)
    Np_hip = (qi**(b) * (qi**(1 - b) - qo_hip**(1 - b)))/(D1*(1 - b))
    
    # Declinación armónica
    qo_arm = qi/(1 + D1*t)
    Np_arm = (qi/D1)*np.log(1 + D1*t)
    
    # Creando el dataframe
    data_dec = {"t":t, "Fecha":fecha, "Qo_exp":qo_exp, "Np_exp":Np_exp, "Qo_hip":qo_hip, "Np_hip":Np_hip,
            "Qo_arm":qo_arm, "Np_arm":Np_arm}
    
    df_dec = pd.DataFrame(data_dec)
    df_dec["Fecha"] = pd.to_datetime(df_dec["Fecha"]).dt.date   

    fig = make_subplots(specs=[[{"secondary_y":True}]])

    # Real
    fig.add_trace(go.Scatter(x=data["fecha"], mode="lines + markers", y=data["q"], name="real"), 
              secondary_y=False)
    fig.update_traces(line_color="black", line_width=1.1, marker=dict(color="white", size=4.8, line=dict(width=1.2, color='black')))
    
    # Exponencial
    # fig.add_trace(go.Scatter(x=df_dec["Fecha"], y=df_dec["Qo_exp"], name="Exp"), secondary_y=False)
    # fig.add_trace(go.Scatter(x=df_dec["Fecha"], y=df_dec["Np_exp"], name="Np_Exp"), secondary_y=True)
    
    # Hiperbólica
    # fig.add_trace(go.Scatter(x=df_dec["Fecha"], y=df_dec["Qo_hip"], name="Hip"), secondary_y=False)
    # fig.add_trace(go.Scatter(x=df_dec["Fecha"], y=df_dec["Np_hip"], name="Np_Hip"), secondary_y=True)
    
    # Armónica
    # fig.add_trace(go.Scatter(x=df_dec["Fecha"], y=df_dec["Qo_arm"], name="Arm"), secondary_y=False)
    # fig.add_trace(go.Scatter(x=df_dec["Fecha"], y=df_dec["Np_arm"], name="Np_Arm"), secondary_y=True)

    # Plot-properties
    # fig.update_layout(yaxis2=dict(tickmode="sync"))
    fig.update_yaxes(secondary_y=True, showgrid=False)
    
    # fig.update_yaxes(rangemode='tozero')
    fig.update_yaxes(range=[min(data["q"]), max(data["q"]) + 5], secondary_y=False)
    fig.update_yaxes(range=[0, max(df_dec["Np_arm"]) + 300], secondary_y=True)
    fig.update_layout(width=1400, height=600)
    # fig.update_layout(title_x=0.4, title_y=0.85, plot_bgcolor="white")
    sl.plotly_chart(fig, key = 2)

    # Download button
    sl.write(df_dec)
    @sl.cache_data
    def convert_csv(df):
        return df.to_csv(index=False).encode("utf-8")
        
    csv = convert_csv(df_dec)
    sl.download_button(label="Download CSV", data=csv, file_name="Proyección_" + f"{select_pozo}_" + f"{p_meses}_meses" + ".csv", mime="text/csv")

elif file == None:
    sl.write("Aún no se ha cargado la Base de Datos")

