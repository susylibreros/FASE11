# ==============================================================================
# ETAPA 1: Construcción de dependencias
# ==============================================================================
FROM python:3.11-slim AS builder
WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==============================================================================
# ETAPA 2: Runtime final
# ==============================================================================
FROM python:3.11-slim AS runner
WORKDIR /app

# Crear usuario sin privilegios root
RUN groupadd -r appgroup && useradd -r -g appgroup -s /bin/false appuser
COPY --from=builder /root/.local /home/appuser/.local

# Copiar todo el contenido del repositorio al contenedor
COPY . /app/

# Crear carpetas auxiliares por si no existen
RUN mkdir -p /app/src /app/models /app/data

# Si app.py está en la raíz, moverlo o duplicarlo a /app/src/ para compatibilidad
RUN if [ -f /app/app.py ]; then cp /app/app.py /app/src/app.py; fi
RUN if [ -f /app/predictor.py ]; then cp /app/predictor.py /app/src/predictor.py; fi

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# Ejecutar app.py desde src si existe, o desde la raíz
CMD ["sh", "-c", "if [ -f /app/src/app.py ]; then streamlit run /app/src/app.py; else streamlit run /app/app.py; fi"]