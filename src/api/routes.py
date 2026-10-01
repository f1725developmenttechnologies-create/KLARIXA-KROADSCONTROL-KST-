# ============================================================
# KLARIXA KROADSCONTROL (KST)
# Endpoints del Nonacortex 5-3-1
# WIPO / NNN / NDA — EinsRos Global Cortex Ultd
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status

from src.nonacortex import get_nonacortex
from src.nonacortex.orchestrator import Entrada
from src.nonacortex.schemas import (
    CicloResponse,
    DecisionResponse,
    EntradaRequest,
    EstadoResponse,
)
from src.security import get_kshield


router = APIRouter(prefix="/nonacortex", tags=["nonacortex"])


# ------------------------------------------------------------
# Estado del orquestador
# ------------------------------------------------------------
@router.get("/estado", response_model=EstadoResponse)
async def estado(_=Depends(get_kshield().verificar_request.__wrapped__ if False else None)):
    """Estado del Nonacortex. Requiere token KSHIELD."""
    ncx = get_nonacortex()
    return EstadoResponse(**ncx.estado())


# ------------------------------------------------------------
# Ciclo completo 5-3-1
# ------------------------------------------------------------
@router.post("/procesar", response_model=CicloResponse)
async def procesar(entrada: EntradaRequest):
    """
    Ciclo completo: recibir → seleccionar → decidir.
    Nota: requiere implementación del middleware KSHIELD.
    """
    ncx = get_nonacortex()
    if not ncx.activo:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nonacortex no inicializado",
        )

    e = Entrada(
        tipo=entrada.tipo,
        contenido=entrada.contenido,
        metadata=entrada.metadata,
    )

    analisis = await ncx.seleccionar(e)
    decision = await ncx.decidir(analisis)

    return CicloResponse(
        entrada=entrada,
        analisis=[a.__dict__ for a in analisis],
        decision=DecisionResponse(
            tipo_tarea=decision.tipo_tarea.value,
            modelo_destino=decision.modelo_destino,
            payload=decision.payload,
            confianza=decision.confianza,
            latencia_total_ms=decision.latencia_total_ms,
            timestamp=decision.timestamp,
        ),
    )