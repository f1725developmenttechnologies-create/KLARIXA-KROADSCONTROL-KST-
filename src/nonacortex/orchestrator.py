# ============================================================
# KLARIXA KROADSCONTROL (KST)
# Nonacortex 5-3-1 — Orquestador de IA distribuida
# WIPO / NNN / NDA — EinsRos Global Cortex Ultd
#
# Arquitectura:
#   5 Sensores  → entradas (telemetría, texto, voz, visión, GPS)
#   3 Selectores → análisis (lógica, NLP, visión)
#   1 Árbitro   → decisión y delegación
# ============================================================

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from loguru import logger


# ------------------------------------------------------------
# Tipos y enums
# ------------------------------------------------------------
class ModoOperacion(str, Enum):
    """Modos de operación del Nonacortex."""
    ENERGIA = "E"
    COMUNICACION = "C"
    DEFENSA = "D"
    FABRICACION = "F"
    PREVIEW = "PREVIEW"


class TipoTarea(str, Enum):
    """Tipos de tarea que el Árbitro puede delegar."""
    LOGICA = "logica"          # Rutas, H3, geometría
    NLP = "nlp"                # Chat, traducción, texto
    VISION = "vision"          # Imágenes, validación
    FRAUDE = "fraude"          # Detección de anomalías
    ETA = "eta"                # Estimación de tiempo
    CIFRADO = "cifrado"        # KSHIELD


@dataclass
class Entrada:
    """Entrada cruda recibida por un sensor."""
    tipo: str
    contenido: Any
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class Analisis:
    """Resultado del análisis de un selector."""
    selector: str
    resultado: Any
    confianza: float
    latencia_ms: float


@dataclass
class Decision:
    """Decisión final del Árbitro."""
    tipo_tarea: TipoTarea
    modelo_destino: str
    payload: dict
    confianza: float
    latencia_total_ms: float
    timestamp: float = field(default_factory=time.time)


# ------------------------------------------------------------
# Nonacortex 5-3-1
# ------------------------------------------------------------
class Nonacortex:
    """
    Orquestador de IA distribuida basado en la arquitectura 5-3-1.

    - 5 Sensores: entradas paralelas (texto, voz, imagen, GPS, telemetría)
    - 3 Selectores: análisis especializados (lógica, NLP, visión)
    - 1 Árbitro: decisión y delegación al modelo más eficiente
    """

    def __init__(self):
        self.modo: ModoOperacion = ModoOperacion.COMUNICACION
        self.activo: bool = False
        self._modelos: dict[str, Any] = {}
        self._sensores: list[str] = ["texto", "voz", "imagen", "gps", "telemetria"]
        self._selectores: list[str] = ["logica", "nlp", "vision"]

        logger.info("Nonacortex 5-3-1 instanciado")
        logger.info(f"  Sensores:  {self._sensores}")
        logger.info(f"  Selectores: {self._selectores}")
        logger.info(f"  Árbitro:   1 (Router Central)")

    # --------------------------------------------------------
    # Ciclo de vida
    # --------------------------------------------------------
    async def inicializar(self, modelos: Optional[dict[str, Any]] = None) -> None:
        """Inicializa el orquestador y carga los modelos."""
        self._modelos = modelos or {}
        self.activo = True
        logger.info(f"Nonacortex activado. Modo: {self.modo.value}")
        logger.info(f"Modelos cargados: {list(self._modelos.keys())}")

    async def detener(self) -> None:
        """Detiene el orquestador."""
        self.activo = False
        self._modelos.clear()
        logger.info("Nonacortex detenido")

    # --------------------------------------------------------
    # Sensores
    # --------------------------------------------------------
    async def recibir_entrada(self, entrada: Entrada) -> Entrada:
        """Procesa una entrada de un sensor."""
        if not self.activo:
            raise RuntimeError("Nonacortex no está activo")
        logger.debug(f"Entrada recibida: tipo={entrada.tipo}")
        return entrada

    # --------------------------------------------------------
    # Selectores
    # --------------------------------------------------------
    async def _selector_logica(self, entrada: Entrada) -> Analisis:
        """Analiza lógica, geometría, rutas."""
        t0 = time.time()
        await asyncio.sleep(0)  # placeholder
        return Analisis(
            selector="logica",
            resultado={"tipo": "placeholder"},
            confianza=0.0,
            latencia_ms=(time.time() - t0) * 1000,
        )

    async def _selector_nlp(self, entrada: Entrada) -> Analisis:
        """Analiza texto, intención, idioma."""
        t0 = time.time()
        await asyncio.sleep(0)
        return Analisis(
            selector="nlp",
            resultado={"intencion": "placeholder"},
            confianza=0.0,
            latencia_ms=(time.time() - t0) * 1000,
        )

    async def _selector_vision(self, entrada: Entrada) -> Analisis:
        """Analiza imágenes."""
        t0 = time.time()
        await asyncio.sleep(0)
        return Analisis(
            selector="vision",
            resultado={"clase": "placeholder"},
            confianza=0.0,
            latencia_ms=(time.time() - t0) * 1000,
        )

    async def seleccionar(self, entrada: Entrada) -> list[Analisis]:
        """Ejecuta los 3 selectores en paralelo."""
        resultados = await asyncio.gather(
            self._selector_logica(entrada),
            self._selector_nlp(entrada),
            self._selector_vision(entrada),
            return_exceptions=True,
        )
        return [r for r in resultados if isinstance(r, Analisis)]

    # --------------------------------------------------------
    # Árbitro
    # --------------------------------------------------------
    async def decidir(self, analisis: list[Analisis]) -> Decision:
        """
        Árbitro: decide qué tarea ejecutar y qué modelo usar.

        Reglas de mapeo (diseño):
          - lógica   → DeepSeek Coder
          - nlp      → Gemma 2
          - vision   → Qwen-VL
          - fraude   → Edge (Qwen 1.5B)
          - eta      → Edge (Qwen 1.5B)
          - cifrado  → KSHIELD (local)
        """
        t0 = time.time()

        # Seleccionar el análisis con mayor confianza
        if not analisis:
            tipo = TipoTarea.NLP
            modelo = "gemma_nlp"
            confianza = 0.0
        else:
            mejor = max(analisis, key=lambda a: a.confianza)
            tipo = self._mapear_tipo(mejor.selector)
            modelo = self._mapear_modelo(tipo)
            confianza = mejor.confianza

        decision = Decision(
            tipo_tarea=tipo,
            modelo_destino=modelo,
            payload={"analisis": [a.selector for a in analisis]},
            confianza=confianza,
            latencia_total_ms=(time.time() - t0) * 1000,
        )
        logger.info(f"Decisión: {tipo.value} → {modelo} (confianza={confianza:.2f})")
        return decision

    def _mapear_tipo(self, selector: str) -> TipoTarea:
        return {
            "logica": TipoTarea.LOGICA,
            "nlp": TipoTarea.NLP,
            "vision": TipoTarea.VISION,
        }.get(selector, TipoTarea.NLP)

    def _mapear_modelo(self, tipo: TipoTarea) -> str:
        return {
            TipoTarea.LOGICA: "deepseek_logic",
            TipoTarea.NLP: "gemma_nlp",
            TipoTarea.VISION: "qwen_vl",
            TipoTarea.FRAUDE: "edge_model",
            TipoTarea.ETA: "edge_model",
            TipoTarea.CIFRADO: "kshield_local",
        }.get(tipo, "gemma_nlp")

    # --------------------------------------------------------
    # Ciclo completo
    # --------------------------------------------------------
    async def procesar(self, entrada: Entrada) -> Decision:
        """Ciclo completo 5-3-1: recibir → seleccionar → decidir."""
        entrada = await self.recibir_entrada(entrada)
        analisis = await self.seleccionar(entrada)
        decision = await self.decidir(analisis)
        return decision

    # --------------------------------------------------------
    # Estado
    # --------------------------------------------------------
    def estado(self) -> dict:
        """Estado actual del Nonacortex."""
        return {
            "activo": self.activo,
            "modo": self.modo.value,
            "sensores": self._sensores,
            "selectores": self._selectores,
            "modelos_cargados": list(self._modelos.keys()),
            "arquitectura": "5-3-1",
        }


# ------------------------------------------------------------
# Singleton
# ------------------------------------------------------------
_nonacortex_instance: Optional[Nonacortex] = None


def get_nonacortex() -> Nonacortex:
    """Retorna la instancia global del Nonacortex."""
    global _nonacortex_instance
    if _nonacortex_instance is None:
        _nonacortex_instance = Nonacortex()
    return _nonacortex_instance