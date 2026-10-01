# ============================================================
# KLARIXA KROADSCONTROL (KST)
# H3 Router — Geolocalización y ruteo hexagonal
# WIPO / NNN / NDA — EinsRos Global Cortex Ultd
# ============================================================

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import h3
from loguru import logger


# ------------------------------------------------------------
# Tipos
# ------------------------------------------------------------
@dataclass
class Punto:
    """Punto geográfico."""
    lat: float
    lng: float
    h3_index: Optional[str] = None


# ------------------------------------------------------------
# H3 Router
# ------------------------------------------------------------
class H3Router:
    """
    Router basado en H3 (Uber).
    Provee indexación hexagonal y consultas de proximidad.
    """

    def __init__(self, resolucion: Optional[int] = None):
        self.resolucion = resolucion or int(os.getenv("H3_RESOLUTION", "9"))
        logger.info(f"H3Router inicializado. Resolución: {self.resolucion}")

    # --------------------------------------------------------
    # Conversiones básicas
    # --------------------------------------------------------
    def latlng_a_h3(self, lat: float, lng: float) -> str:
        """Convierte coordenadas a índice H3."""
        return h3.latlng_to_cell(lat, lng, self.resolucion)

    def h3_a_latlng(self, h3_index: str) -> tuple[float, float]:
        """Convierte índice H3 a coordenadas del centro."""
        return h3.cell_to_latlng(h3_index)

    def punto(self, lat: float, lng: float) -> Punto:
        """Crea un Punto con índice H3."""
        return Punto(
            lat=lat,
            lng=lng,
            h3_index=self.latlng_a_h3(lat, lng),
        )

    # --------------------------------------------------------
    # Vecinos y anillos
    # --------------------------------------------------------
    def vecinos(self, h3_index: str) -> list[str]:
        """Retorna los 6 vecinos inmediatos."""
        return list(h3.grid_disk(h3_index, 1))[1:]  # excluir el propio

    def disco(self, h3_index: str, k: int) -> list[str]:
        """Retorna todos los hexágonos dentro de k anillos."""
        return list(h3.grid_disk(h3_index, k))

    def anillo(self, h3_index: str, k: int) -> list[str]:
        """Retorna los hexágonos del anillo k."""
        return list(h3.grid_ring(h3_index, k))

    # --------------------------------------------------------
    # Distancias
    # --------------------------------------------------------
    def distancia_km(self, h3_a: str, h3_b: str) -> float:
        """Distancia aproximada entre dos celdas H3 en km."""
        lat1, lng1 = h3.cell_to_latlng(h3_a)
        lat2, lng2 = h3.cell_to_latlng(h3_b)
        return h3.great_circle_distance((lat1, lng1), (lat2, lng2), unit="km")

    # --------------------------------------------------------
    # Búsqueda de proximidad
    # --------------------------------------------------------
    def conductores_cerca(
        self,
        lat: float,
        lng: float,
        conductores: list[dict],
        radio_km: float = 5.0,
        max_resultados: int = 10,
    ) -> list[dict]:
        """
        Encuentra conductores cercanos a un punto.

        Args:
            lat, lng: coordenadas del usuario
            conductores: lista de dicts con 'lat', 'lng', 'id', etc.
            radio_km: radio de búsqueda
            max_resultados: máximo de resultados

        Returns:
            lista de conductores ordenados por distancia
        """
        h3_origen = self.latlng_a_h3(lat, lng)

        # Determinar cuántos anillos cubren el radio
        # Aproximación: 1 anillo ≈ 200m a resolución 9
        k_anillos = max(1, int(radio_km * 1000 / 200))

        celdas_validas = set(self.disco(h3_origen, k_anillos))

        resultados = []
        for c in conductores:
            h3_c = self.latlng_a_h3(c["lat"], c["lng"])
            if h3_c in celdas_validas:
                dist = self.distancia_km(h3_origen, h3_c)
                if dist <= radio_km:
                    resultados.append({**c, "distancia_km": round(dist, 3)})

        resultados.sort(key=lambda x: x["distancia_km"])
        return resultados[:max_resultados]


# ------------------------------------------------------------
# Singleton
# ------------------------------------------------------------
_h3_instance: Optional[H3Router] = None


def get_h3_router() -> H3Router:
    global _h3_instance
    if _h3_instance is None:
        _h3_instance = H3Router()
    return _h3_instance