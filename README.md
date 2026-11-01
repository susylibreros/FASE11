# 🕯️ Las Tres Lunas Serenas — Sistema MLOps de Inventario y Recomendación

Sistema inteligente de pronóstico de demanda y asignación preventiva de lotes de producción para pedidos de gran escala (velas de soya botánicas y sales gourmet) desarrollado para el taller artesanal **Las Tres Lunas Serenas**.

## 🚀 Características del Sistema
- **Algoritmo:** Clasificación con árboles de gradiente (HistGradientBoosting).
- **Enfoque Sensible al Costo:** Penalización asimétrica $8:1$ ($C_{FN}=8$ por quiebre de stock no previsto vs. $C_{FP}=1$ por adelantar producción).
- **Umbral Operativo:** $t^* = 0.24$, alcanzando un **Recall del 85.0%** y reduciendo el costo de error en un **70.2%**.
- **Interfaz Interactiva:** Panel en Streamlit con cotizador individual y carga masiva por CSV.
- **Contenerización y CI/CD:** Docker multi-stage optimizado con pruebas en GitHub Actions.

## 🛠️ Ejecución Local con Python
```bash
python -m venv venv
# Activar entorno (Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
pytest tests/ -v
streamlit run src/app.py
