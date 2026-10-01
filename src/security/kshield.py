# ============================================================
# KLARIXA KROADSCONTROL (KST)
# KSHIELD — Capa de seguridad del ecosistema
# WIPO / NNN / NDA — EinsRos Global Cortex Ultd
#
# Funciones:
#   - Verificación de token
#   - Geofencing (opcional)
#   - Ofuscación de coordenadas pre-match
# ============================================================

from __future__ import annotations

import hashlib
import hmac
import os
import time
from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, Request, status
from loguru import logger


# ------------------------------------------------------------
# Tipos
# ------------------------------------------------------------
@dataclass
class ContextoAutenticado:
    """Información del cliente autenticado."""
    token: str
    usuario_id: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


# ------------------------------------------------------------
# KSHIELD
# ------------------------------------------------------------
class KShield:
    """
    Capa de seguridad del ecosistema KLARIXA.
    Valida token, geofencing y ofusca coordenadas.
    """

    def __init__(self):
        self.token_maestro = os.getenv("KSHIELD_TOKEN", "dev-token")
        self.geofence_enabled = os.getenv("KSHIELD_GEOFENCE_ENABLED", "false").lower() == "true"
        self.geofence_lat = float(os.getenv("KSHIELD_GEOFENCE_CENTER_LAT", "7.8891"))
        self.geofence_lng = float(os.getenv("KSHIELD_GEOFENCE_CENTER_LNG", "-72.4967"))
        self.geofence_radio_km = float(os.getenv("KSHIELD_GEOFENCE_RADIUS_KM", "50"))

        logger.info(f"KSHIELD inicializado. Geofencing: {'ON' if self.geofence_enabled else 'OFF'}")

    # --------------------------------------------------------
    # Verificación de token
    # --------------------------------------------------------
    def verificar_token(self, token: str) -> bool:
        """Verificación por comparación en tiempo constante."""
        return hmac.compare_digest(token, self.token_maestro)

    def verificar_request(self, request: Request) -> ContextoAutenticado:
        """
        Extrae y valida el token del header X-Klarixa-Token.
        Lanza HTTPException si no es válido.
        """
        token = request.headers.get("X-Klarixa-Token", "")
        if not token or not self.verificar_token(token):
            logger.warning(f"Token inválido desde {request.client.host if request.client else 'unknown'}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token KSHIELD inválido",
            )
        return ContextoAutenticado(token=token)

    # --------------------------------------------------------
    # Geofencing
    # --------------------------------------------------------
    def dentro_de_geofence(self, lat: float, lng: float) -> bool:
        """Verifica si un punto está dentro del geofence."""
        if not self.geofence_enabled:
            return True

        import h3
        d = h3.great_circle_distance(
            (self.geofence_lat, self.geofence_lng),
            (lat, lng),
            unit="km",
        )
        return d <= self.geofence_radio_km

    # --------------------------------------------------------
    # Ofuscación de coordenadas
    # --------------------------------------------------------
    def ofuscar_coordenadas(
        self,
        lat: float,
        lng: float,
        precision: int = 3,
        salt: Optional[str] = None,
    ) -> tuple[float, float]:
        """
        Ofusca coordenadas antes de un match.
        Reduce precisión y agrega ruido determinista.
        """
        salt = salt or str(int(time.time() // 60))  # cambia cada minuto
        h = hashlib.sha256(f"{lat},{lng},{salt}".encode()).hexdigest()
        delta_lat = (int(h[:4], 16) / 65535 - 0.5) * 0.001
        delta_lng = (int(h[4:8], 16) / 65535 - 0.5) * 0.001

        return (
            round(lat, precision) + delta_lat,
            round(lng, precision) + delta_lng,
        )

    # --------------------------------------------------------
    # Hash de integridad
    # --------------------------------------------------------
    def hash_integridad(self, data: str) -> str:
        """Genera hash HMAC para verificar integridad."""
        return hmac.new(
            self.token_maestro.encode(),
            data.encode(),
            hashlib.sha256,
        ).hexdigest()


# ------------------------------------------------------------
# Singleton
# ------------------------------------------------------------
_kshield_instance: Optional[KShield] = None


def get_kshield() -> KShield:
    global _kshield_instance
    if _kshield_instance is None:
        _kshield_instance = KShield()
    return _kshield_instance