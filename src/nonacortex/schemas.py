# ============================================================
# KLARIXA KROADSCONTROL (KST)
# Schemas Pydantic v2 para el Nonacortex
# WIPO / NNN / NDA — EinsRos Global Cortex Ultd
# ============================================================

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, ConfigDict


# ------------------------------------------------------------
# Entrada
# ------------------------------------------------------------
class EntradaRequest(BaseModel):
    """Entrada cruda enviada al Nonacortex."""
    model_config = ConfigDict(extra="forbid")

    tipo: str = Field(..., description="texto | voz | imagen | gps | telemetria")
    contenido: Any = Field(..., description="Contenido de la entrada")
    metadata: dict[str, Any] = Field(default_factory=dict)


# ------------------------------------------------------------
# Análisis
# ------------------------------------------------------------
class AnalisisResponse(BaseModel):
    """Resultado de un selector."""
    model_config = ConfigDict(extra="forbid")

    selector: str
    resultado: Any
    confianza: float
    latencia_ms: float


# ------------------------------------------------------------
# Decisión
# ------------------------------------------------------------
class DecisionResponse(BaseModel):
    """Decisión final del Árbitro."""
    model_config = ConfigDict(extra="forbid")

    tipo_tarea: str
    modelo_destino: str
    payload: dict[str, Any]
    confianza: float
    latencia_total_ms: float
    timestamp: float


# ------------------------------------------------------------
# Ciclo completo
# ------------------------------------------------------------
class CicloResponse(BaseModel):
    """Respuesta del ciclo completo 5-3-1."""
    model_config = ConfigDict(extra="forbid")

    entrada: EntradaRequest
    analisis: list[AnalisisResponse]
    decision: DecisionResponse


# ------------------------------------------------------------
# Estado del Nonacortex
# ------------------------------------------------------------
class EstadoResponse(BaseModel):
    """Estado del orquestador."""
    model_config = ConfigDict(extra="forbid")

    activo: bool
    modo: str
    sensores: list[str]
    selectores: list[str]
    modelos_cargados: list[str]
    arquitectura: str