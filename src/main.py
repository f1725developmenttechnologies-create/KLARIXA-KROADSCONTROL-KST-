# ============================================================
# KLARIXA KROADSCONTROL (KST)
# Aplicación principal FastAPI
# WIPO / NNN / NDA — EinsRos Global Cortex Ultd
# ============================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger
import sys


# ------------------------------------------------------------
# Configuración
# ------------------------------------------------------------
class Settings(BaseSettings):
    app_name: str = "KROADSCONTROL"
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_secret_key: str = "change-me"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()


# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------
logger.remove()
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)


# ------------------------------------------------------------
# Lifespan (startup / shutdown)
# ------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Iniciando {settings.app_name} v1.0")
    logger.info(f"Entorno: {settings.app_env}")
    logger.info("Estado: Sistema en modo pre-construcción")
    logger.info("Repositorio: klarixa-kroadscontrol")
    logger.info("Protocolo: WIPO / NNN / NDA — EinsRos Global Cortex Ultd")

    # TODO: Inicializar conexión a PostgreSQL
    # TODO: Inicializar conexión a Redis
    # TODO: Inicializar cliente Nonacortex (Qwen, DeepSeek, Gemma)

    yield

    logger.info(f"Cerrando {settings.app_name}")


# ------------------------------------------------------------
# App FastAPI
# ------------------------------------------------------------
app = FastAPI(
    title="KLARIXA KROADSCONTROL (KST)",
    description=(
        "Plataforma de movilidad y logística P2P orquestada por IA distribuida. "
        "Optimizada para hardware AMD con ROCm."
    ),
    version="0.1.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    docs_url="/docs" if settings.app_debug else None,
    redoc_url="/redoc" if settings.app_debug else None,
)


# ------------------------------------------------------------
# CORS
# ------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app_debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# Endpoints base
# ------------------------------------------------------------
@app.get("/", tags=["root"])
async def root():
    """Endpoint raíz. Verificación de que el sistema está en línea."""
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "status": "online",
        "protocol": "WIPO/NNN/NDA",
        "titular": "EinsRos Global Cortex Ultd",
    }


@app.get("/health", tags=["health"])
async def health(request: Request):
    """Estado de salud del sistema. Verifica componentes clave."""
    return {
        "status": "healthy",
        "environment": settings.app_env,
        "components": {
            "api": "ok",
            "database": "not_connected",      # TODO
            "redis": "not_connected",          # TODO
            "nonacortex": "not_initialized",   # TODO
            "models": "not_loaded",            # TODO
        },
        "client_ip": request.client.host if request.client else None,
    }


@app.get("/version", tags=["root"])
async def version():
    """Información de versión y titularidad."""
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "build": "pre-construcción",
        "titular": "EinsRos Global Cortex Ultd",
        "wipo_id": "user_CO_SANCHEZ-COLMENARES_FREDDY-ADRIAN_0876",
        "hackathon": "AMD Developer Hackathon: ACT III",
    }


# ------------------------------------------------------------
# Ejecución directa
# ------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
        log_level="info",
    )