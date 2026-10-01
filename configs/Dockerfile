# ============================================================
# KLARIXA KROADSCONTROL (KST)
# Dockerfile — Imagen base (CPU, sin modelos)
# WIPO / NNN / NDA — EinsRos Global Cortex Ultd
# ============================================================

FROM python:3.10-slim

LABEL maintainer="Freddy Adrián Sánchez Colmenares"
LABEL org="EinsRos Global Cortex Ultd — F1725 Development Technologies"
LABEL protocol="WIPO/NNN/NDA"

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (cache de capas)
COPY requirements.txt .

# Instalar dependencias Python (sin vLLM/torch, se instalan aparte en AMD)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY src/ ./src/
COPY configs/ ./configs/
COPY docs/ ./docs/
COPY .env.example ./.env

# Exponer puerto
EXPOSE 8000

# Comando
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]