import joblib
import numpy as np
import pandas as pd
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "modelo_velas_calibrado.joblib"
UMBRAL_CALIBRADO = 0.24  # Corte óptimo para prevenir quiebres de inventario

class CandleInventoryPredictor:
    def __init__(self):
        self.threshold = UMBRAL_CALIBRADO
        self.model = self._cargar_modelo()

    def _cargar_modelo(self):
        if MODEL_PATH.exists():
            try:
                return joblib.load(MODEL_PATH)
            except Exception:
                return None
        return None

    def predecir_probabilidad(self, df: pd.DataFrame) -> np.ndarray:
        if self.model is not None:
            return self.model.predict_proba(df)[:, 1]

        # Heurística empírica de Las Tres Lunas Serenas (eventos y producción)
        probs = []
        for _, row in df.iterrows():
            inv_actual = row.get("stock_actual_unidades", 50)
            inv_factor = max(0.1, (100 - inv_actual) / 100.0)
            
            score = (
                (row.get("num_asistentes", 50) * 0.018) +
                (row.get("dias_anticipacion", 15) * -0.04) +  # Menos días = mayor urgencia
                (0.35 if str(row.get("tipo_evento", "boda")).lower() in ["boda", "corporativo"] else 0.0) +
                (0.25 if str(row.get("incluye_sales_gourmet", "no")).lower() == "yes" else 0.0) +
                (inv_factor * 0.8)
            )
            prob = 1 / (1 + np.exp(-score))
            probs.append(float(np.clip(prob, 0.02, 0.98)))
        return np.array(probs)

    def recomendar_coleccion(self, tipo_evento: str, aroma_preferido: str) -> str:
        recomendaciones = {
            "boda": "Colección 'Noche Serena': Velas de Cera de Soya con Jazmín Blanco y Sales Gourmet de Lavanda Francesa.",
            "corporativo": "Colección 'Luna Creciente': Velas Cítricas de Bergamota con Cedro y Sales Exfoliantes de Eucalipto.",
            "retiro_bienestar": "Colección 'Plenilunio': Velas de Salvia Blanca con Palo Santo y Sales de Baño del Himalaya.",
            "cena_gourmet": "Colección 'Tres Lunas': Velas Neutras de Miel Silvestre con Sales Negras Gourmet para Mesa."
        }
        return recomendaciones.get(tipo_evento, "Colección Artesanal Clásica de Las Tres Lunas Serenas.")

    def evaluar_pedido(self, datos_evento: dict) -> dict:
        df_single = pd.DataFrame([datos_evento])
        prob = float(self.predecir_probabilidad(df_single)[0])
        es_critico = int(prob >= self.threshold)

        if es_critico == 1:
            diagnostico = "Riesgo de Quiebre de Stock (Prioridad Alta)"
            accion = "Activar Lote de Producción Urgente (Taller)"
            recomendacion = "Iniciar curado de cera de soya de inmediato y reservar 20 kg de sales base."
            alerta = "warning"
        else:
            diagnostico = "Stock Suficiente (Flujo Normal)"
            accion = "Surtir desde Almacén Regular"
            recomendacion = "El inventario actual cubre el evento sin alterar el calendario de producción."
            alerta = "success"

        coleccion_sugerida = self.recomendar_coleccion(
            datos_evento.get("tipo_evento", "boda"),
            datos_evento.get("aroma_preferido", "lavanda")
        )

        return {
            "probabilidad": round(prob, 4),
            "umbral": self.threshold,
            "prediccion": es_critico,
            "diagnostico": diagnostico,
            "accion_operativa": accion,
            "recomendacion_inventario": recomendacion,
            "coleccion_sugerida": coleccion_sugerida,
            "alerta": alerta
        }

    def procesar_lote_csv(self, df_lote: pd.DataFrame) -> pd.DataFrame:
        df_out = df_lote.copy()
        probs = self.predecir_probabilidad(df_out)
        df_out["Probabilidad_Riesgo_Stock"] = np.round(probs, 4)
        df_out["Accion_Taller"] = np.where(probs >= self.threshold, "Producción Urgente", "Stock Regular")
        return df_out

service_lunas = CandleInventoryPredictor()
