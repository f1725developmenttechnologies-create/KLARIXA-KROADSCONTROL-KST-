# ============================================================
# KLARIXA KROADSCONTROL (KST)
# Cliente unificado para modelos IA (vLLM / ROCm)
# WIPO / NNN / NDA — EinsRos Global Cortex Ultd
#
# Los modelos se sirven vía vLLM con backend ROCm/HIP.
# Cada modelo tiene su propio endpoint OpenAI-compatible.
# ============================================================

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Optional

import httpx
from loguru import logger


# ------------------------------------------------------------
# Configuración de modelos (endpoints vLLM)
# ------------------------------------------------------------
@dataclass
class ModelEndpoint:
    """Definición de un endpoint de modelo."""
    nombre: str
    url: str
    modelo: str
    rol: str
    max_tokens: int = 512
    temperatura: float = 0.7


def _cargar_endpoints() -> dict[str, ModelEndpoint]:
    """Carga los endpoints desde variables de entorno."""
    return {
        "qwen_central": ModelEndpoint(
            nombre="qwen_central",
            url=os.getenv("QWEN_CENTRAL_URL", "http://localhost:8001/v1"),
            modelo="Qwen/Qwen2.5-32B-Instruct",
            rol="Router / Árbitro",
        ),
        "deepseek_logic": ModelEndpoint(
            nombre="deepseek_logic",
            url=os.getenv("DEEPSEEK_LOGIC_URL", "http://localhost:8002/v1"),
            modelo="deepseek-ai/deepseek-coder-33b-instruct",
            rol="Lógica / Rutas",
        ),
        "gemma_nlp": ModelEndpoint(
            nombre="gemma_nlp",
            url=os.getenv("GEMMA_NLP_URL", "http://localhost:8003/v1"),
            modelo="google/gemma-2-27b-it",
            rol="NLP / Chat",
        ),
        "qwen_vl": ModelEndpoint(
            nombre="qwen_vl",
            url=os.getenv("QWEN_VL_URL", "http://localhost:8004/v1"),
            modelo="Qwen/Qwen2-VL-7B-Instruct",
            rol="Visión",
        ),
        "edge_model": ModelEndpoint(
            nombre="edge_model",
            url=os.getenv("EDGE_MODEL_URL", "http://localhost:8005/v1"),
            modelo="Qwen/Qwen2.5-1.5B-Instruct",
            rol="Edge / Fraude / ETA",
        ),
    }


# ------------------------------------------------------------
# Cliente
# ------------------------------------------------------------
class ModelClient:
    """
    Cliente unificado para todos los modelos del Nonacortex.
    Usa el protocolo OpenAI-compatible de vLLM.
    """

    def __init__(self, timeout: float = 60.0):
        self.endpoints = _cargar_endpoints()
        self.timeout = timeout
        self._http: Optional[httpx.AsyncClient] = None

    async def inicializar(self) -> None:
        self._http = httpx.AsyncClient(timeout=self.timeout)
        logger.info(f"ModelClient inicializado. Endpoints: {list(self.endpoints.keys())}")

    async def cerrar(self) -> None:
        if self._http:
            await self._http.aclose()
            self._http = None
        logger.info("ModelClient cerrado")

    async def llamar(
        self,
        endpoint: str,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperatura: Optional[float] = None,
        system: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Llama a un modelo específico vía su endpoint vLLM.
        Retorna un dict con: respuesta, latencia_ms, modelo, tokens.
        """
        if self._http is None:
            raise RuntimeError("ModelClient no inicializado. Llamar a inicializar() primero.")

        if endpoint not in self.endpoints:
            raise ValueError(f"Endpoint desconocido: {endpoint}")

        ep = self.endpoints[endpoint]
        t0 = time.time()

        mensajes = []
        if system:
            mensajes.append({"role": "system", "content": system})
        mensajes.append({"role": "user", "content": prompt})

        payload = {
            "model": ep.modelo,
            "messages": mensajes,
            "max_tokens": max_tokens or ep.max_tokens,
            "temperature": temperatura if temperatura is not None else ep.temperatura,
        }

        try:
            r = await self._http.post(
                f"{ep.url}/chat/completions",
                json=payload,
            )
            r.raise_for_status()
            data = r.json()
            respuesta = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("total_tokens", 0)
        except httpx.HTTPError as e:
            logger.error(f"Error en {endpoint}: {e}")
            respuesta = f"[ERROR: {type(e).__name__}]"
            tokens = 0

        latencia_ms = (time.time() - t0) * 1000
        logger.info(f"{endpoint}: {latencia_ms:.0f}ms, {tokens} tokens")

        return {
            "endpoint": endpoint,
            "modelo": ep.modelo,
            "rol": ep.rol,
            "respuesta": respuesta,
            "tokens": tokens,
            "latencia_ms": latencia_ms,
        }

    async def salud(self) -> dict[str, str]:
        """Verifica el estado de cada endpoint."""
        if self._http is None:
            raise RuntimeError("ModelClient no inicializado")

        resultados = {}
        for nombre, ep in self.endpoints.items():
            try:
                r = await self._http.get(f"{ep.url}/models", timeout=5.0)
                resultados[nombre] = "ok" if r.status_code == 200 else f"http_{r.status_code}"
            except Exception:
                resultados[nombre] = "unreachable"
        return resultados


# ------------------------------------------------------------
# Singleton
# ------------------------------------------------------------
_model_client_instance: Optional[ModelClient] = None


def get_model_client() -> ModelClient:
    global _model_client_instance
    if _model_client_instance is None:
        _model_client_instance = ModelClient()
    return _model_client_instance