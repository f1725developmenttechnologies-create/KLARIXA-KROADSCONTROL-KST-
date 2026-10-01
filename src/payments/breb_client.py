# ============================================================
# KLARIXA KROADSCONTROL (KST)
# Cliente Bre-B (pagos Colombia)
# WIPO / NNN / NDA — EinsRos Global Cortex Ultd
#
# Bre-B es la plataforma de pagos instantáneos interoperables
# del Banco de la República (Colombia).
# ============================================================

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import httpx
from loguru import logger


# ------------------------------------------------------------
# Tipos
# ------------------------------------------------------------
class EstadoTransaccion(str, Enum):
    PENDIENTE = "pendiente"
    COMPLETADA = "completada"
    FALLIDA = "fallida"
    REVERTIDA = "revertida"


@dataclass
class Transaccion:
    """Representa una transacción en KST."""
    id: str
    origen: str
    destino: str
    monto: float
    moneda: str = "COP"
    estado: EstadoTransaccion = EstadoTransaccion.PENDIENTE
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


# ------------------------------------------------------------
# Cliente
# ------------------------------------------------------------
class BreBClient:
    """
    Cliente para la API Bre-B.
    En modo desarrollo retorna transacciones simuladas.
    En producción requiere BREB_API_KEY y BREB_API_URL.
    """

    def __init__(self):
        self.api_url = os.getenv("BREB_API_URL", "")
        self.api_key = os.getenv("BREB_API_KEY", "")
        self.merchant_id = os.getenv("BREB_MERCHANT_ID", "")
        self.simulado = not (self.api_url and self.api_key)
        self._http: Optional[httpx.AsyncClient] = None

        if self.simulado:
            logger.warning("Bre-B en modo SIMULADO (sin credenciales reales)")
        else:
            logger.info("Bre-B configurado con credenciales reales")

    async def inicializar(self) -> None:
        self._http = httpx.AsyncClient(timeout=30.0)

    async def cerrar(self) -> None:
        if self._http:
            await self._http.aclose()
            self._http = None

    # --------------------------------------------------------
    # Operaciones
    # --------------------------------------------------------
    async def crear_transaccion(
        self,
        origen: str,
        destino: str,
        monto: float,
        metadata: Optional[dict] = None,
    ) -> Transaccion:
        """
        Crea una transacción Bre-B.
        En modo simulado, retorna una transacción ficticia completada.
        """
        tx = Transaccion(
            id=str(uuid.uuid4()),
            origen=origen,
            destino=destino,
            monto=monto,
            metadata=metadata or {},
        )

        if self.simulado:
            tx.estado = EstadoTransaccion.COMPLETADA
            logger.info(f"[SIMULADO] Transacción {tx.id} completada: {monto} COP")
            return tx

        try:
            r = await self._http.post(
                f"{self.api_url}/transactions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "merchant_id": self.merchant_id,
                    "origen": origen,
                    "destino": destino,
                    "monto": monto,
                    "moneda": "COP",
                    "metadata": metadata or {},
                },
            )
            r.raise_for_status()
            data = r.json()
            tx.id = data.get("id", tx.id)
            tx.estado = EstadoTransaccion(data.get("estado", "pendiente"))
        except httpx.HTTPError as e:
            logger.error(f"Error en Bre-B: {e}")
            tx.estado = EstadoTransaccion.FALLIDA

        return tx

    async def consultar_transaccion(self, tx_id: str) -> dict[str, Any]:
        """Consulta el estado de una transacción."""
        if self.simulado:
            return {"id": tx_id, "estado": "completada", "simulado": True}

        try:
            r = await self._http.get(
                f"{self.api_url}/transactions/{tx_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            r.raise_for_status()
            return r.json()
        except httpx.HTTPError as e:
            logger.error(f"Error consultando {tx_id}: {e}")
            return {"id": tx_id, "estado": "error"}

    async def reembolsar(self, tx_id: str, monto: Optional[float] = None) -> bool:
        """Revierte o reembolsa una transacción."""
        if self.simulado:
            logger.info(f"[SIMULADO] Reembolso de {tx_id}: OK")
            return True

        try:
            r = await self._http.post(
                f"{self.api_url}/transactions/{tx_id}/refund",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"monto": monto} if monto else {},
            )
            r.raise_for_status()
            return True
        except httpx.HTTPError as e:
            logger.error(f"Error en reembolso: {e}")
            return False


# ------------------------------------------------------------
# Singleton
# ------------------------------------------------------------
_breb_instance: Optional[BreBClient] = None


def get_breb_client() -> BreBClient:
    global _breb_instance
    if _breb_instance is None:
        _breb_instance = BreBClient()
    return _breb_instance