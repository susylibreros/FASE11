import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from predictor import service_lunas

st.set_page_config(
    page_title="Las Tres Lunas Serenas | Gestión de Inventario",
    page_icon="🕯️",
    layout="wide"
)

st.title("🕯️ Las Tres Lunas Serenas — Taller de Velas y Sales Gourmet")
st.markdown(
    """
    **Sistema de Pronóstico de Demanda para Eventos y Recomendador de Colecciones**  
    *Algoritmo:* HistGradientBoosting | *Matriz de Costo:* 8:1 ($C_{FN}=8, C_{FP}=1$) | *Umbral de Decisión:* $t^* = 0.24$
    """
)

with st.sidebar:
    st.header("🌙 Taller Artesanal")
    st.info(f"**Umbral Operativo:** t* = {service_lunas.threshold}\n\nDiseñado para evitar quiebres de inventario en pedidos grandes.")
    st.markdown("---")
    st.metric("Sensibilidad (Recall)", "85.0%", "+75.0% vs umbral estándar")
    st.metric("Reducción de Costo de Error", "70.2%", "45 pts vs 151 pts")
    st.metric("Capacidad Discriminativa (AUC)", "0.721", "Modelo robusto")

tab1, tab2, tab3 = st.tabs(["🕯️ Cotizar Evento y Stock", "📦 Carga por Lote (Eventos del Mes)", "📊 Métricas y Curva ROC"])

with tab1:
    st.subheader("Planificación de Evento Especial")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        tipo_evento = st.selectbox("Tipo de Evento", ["boda", "corporativo", "retiro_bienestar", "cena_gourmet"])
        num_asistentes = st.slider("Número Estimado de Asistentes", 10, 300, 85)
    with c2:
        dias_anticipacion = st.slider("Días de Anticipación para Entrega", 2, 60, 12)
        stock_actual = st.slider("Unidades en Stock Actual", 0, 150, 25)
    with c3:
        incluye_sales = st.selectbox("¿Incluye Sales Gourmet / Baño?", ["yes", "no"])
        aroma = st.selectbox("Línea Aromática", ["lavanda", "bergamota", "salvia_palo_santo", "miel_silvestre"])

    if st.button("Evaluar Disponibilidad de Inventario y Recomendar", type="primary", use_container_width=True):
        datos = {
            "tipo_evento": tipo_evento,
            "num_asistentes": num_asistentes,
            "dias_anticipacion": dias_anticipacion,
            "stock_actual_unidades": stock_actual,
            "incluye_sales_gourmet": incluye_sales,
            "aroma_preferido": aroma
        }
        res = service_lunas.evaluar_pedido(datos)
        
        col_res1, col_res2 = st.columns([1.2, 0.8])
        with col_res1:
            if res["alerta"] == "warning":
                st.error(f"⚠️ **{res['diagnostico']}**")
            else:
                st.success(f"✅ **{res['diagnostico']}**")
            
            st.write(f"**Instrucción de Operación:** {res['accion_operativa']}")
            st.write(f"**Probabilidad Estimada de Quiebre:** `{res['probabilidad']*100:.1f}%` (Corte: `{res['umbral']*100:.0f}%`)")
            st.info(f"**Gestión de Materia Prima:** {res['recomendacion_inventario']}")
            st.markdown(f"🎁 **Recomendación para el Cliente:**\n> *{res['coleccion_sugerida']}*")
            
        with col_res2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=res["probabilidad"] * 100,
                title={'text': "Probabilidad vs. Alerta de Producción (24%)"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#334155"},
                    'steps': [
                        {'range': [0, 24], 'color': "#a7f3d0"},
                        {'range': [24, 100], 'color': "#fecaca"}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'value': 24}
                }
            ))
            fig.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Carga Masiva de Pedidos del Mes")
    archivo = st.file_uploader("Subir archivo CSV con eventos programados", type=["csv"])
    if archivo is not None:
        df = pd.read_csv(archivo)
        st.write(f"Se cargaron **{len(df)} solicitudes de eventos**.")
        if st.button("Calcular Necesidades de Fabricación"):
            df_out = service_lunas.procesar_lote_csv(df)
            st.dataframe(df_out, use_container_width=True)
            csv_data = df_out.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Plan de Producción (CSV)", csv_data, "plan_produccion_lunas.csv", "text/csv")

with tab3:
    st.subheader("Justificación de Rendimiento del Modelo")
    data_metrics = {
        "Configuración": ["Umbral Estándar (t = 0.50)", "Umbral Calibrado Las Tres Lunas (t* = 0.24)"],
        "Recall (Eventos Críticos Detectados)": ["10.0%", "85.0%"],
        "Eventos Sin Stock (Falsos Negativos)": [18, 3],
        "Falsas Alarmas de Producción (Falsos Positivos)": [7, 21],
        "Costo de Error Asimétrico (8*FN + 1*FP)": ["151 puntos", "45 puntos (Ahorro: 70.2%)"]
    }
    st.table(pd.DataFrame(data_metrics))