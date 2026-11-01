import pytest
import pandas as pd
from src.predictor import CandleInventoryPredictor, UMBRAL_CALIBRADO

@pytest.fixture
def predictor():
    return CandleInventoryPredictor()

def test_umbral_fijado(predictor):
    """Verifica que el umbral esté estrictamente en 0.24."""
    assert predictor.threshold == 0.24

def test_evento_alto_riesgo_desabasto(predictor):
    """Boda grande con pocos días de anticipación y bajo stock debe detonar alerta."""
    evento_critico = {
        "tipo_evento": "boda",
        "num_asistentes": 150,
        "dias_anticipacion": 4,
        "stock_actual_unidades": 10,
        "incluye_sales_gourmet": "yes",
        "aroma_preferido": "lavanda"
    }
    res = predictor.evaluar_pedido(evento_critico)
    assert res["probabilidad"] >= UMBRAL_CALIBRADO
    assert res["prediccion"] == 1
    assert res["alerta"] == "warning"

def test_evento_bajo_riesgo(predictor):
    """Cena pequeña con suficiente anticipación y buen stock no debe saturar el taller."""
    evento_regular = {
        "tipo_evento": "cena_gourmet",
        "num_asistentes": 15,
        "dias_anticipacion": 30,
        "stock_actual_unidades": 80,
        "incluye_sales_gourmet": "no",
        "aroma_preferido": "miel_silvestre"
    }
    res = predictor.evaluar_pedido(evento_regular)
    assert res["probabilidad"] < UMBRAL_CALIBRADO
    assert res["prediccion"] == 0
    assert res["alerta"] == "success"

def test_procesamiento_lote(predictor):
    """Valida la consistencia de columnas en la predicción por lote CSV."""
    df_muestra = pd.DataFrame([
        {"tipo_evento": "boda", "num_asistentes": 120, "dias_anticipacion": 5, "stock_actual_unidades": 10, "incluye_sales_gourmet": "yes"},
        {"tipo_evento": "cena_gourmet", "num_asistentes": 10, "dias_anticipacion": 25, "stock_actual_unidades": 90, "incluye_sales_gourmet": "no"}
    ])
    df_res = predictor.procesar_lote_csv(df_muestra)
    assert "Probabilidad_Riesgo_Stock" in df_res.columns
    assert "Accion_Taller" in df_res.columns
    assert len(df_res) == 2