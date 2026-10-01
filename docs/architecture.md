# Arquitectura KROADSCONTROL (KST)

**Protocolo:** WIPO / NNN / NDA
**Titular:** EinsRos Global Cortex Ultd — F1725 Development Technologies
**WIPO Customer ID:** user_CO_SANCHEZ-COLMENARES_FREDDY-ADRIAN_0876

---

## 1. Visión general

KST es un motor de orquestación de movilidad de alta concurrencia.
La arquitectura se basa en el modelo **Nonacortex 5-3-1**.

---

## 2. Nonacortex 5-3-1

---

## 3. Componentes del repositorio

| Módulo | Función |
|--------|---------|
| `src/main.py` | Aplicación FastAPI |
| `src/nonacortex/` | Orquestador 5-3-1 |
| `src/models/` | Cliente de modelos vía vLLM |
| `src/routing/` | H3 (geolocalización hexagonal) |
| `src/payments/` | Cliente Bre-B |
| `src/security/` | KSHIELD (token, geofence, ofuscación) |

---

## 4. Stack

- Python 3.10+
- FastAPI + Uvicorn
- PostgreSQL + Redis
- Uber H3
- vLLM + ROCm (AMD)
- Docker

---

## 5. Modelos y roles

| Rol | Modelo | Justificación |
|-----|--------|---------------|
| Router Central | Qwen 2.5 32B | Function calling, razonamiento |
| Lógica | DeepSeek Coder | Geometría, rutas |
| NLP | Gemma 2 27B | Chat en tiempo real |
| Visión | Qwen2-VL 7B | Procesamiento de imágenes |
| Edge | Qwen 2.5 1.5B | Inferencia local |

---

## 6. Estado

| Aspecto | Estado |
|---------|--------|
| Código base | ✅ Redactado |
| Tests | ⚠️ Básicos |
| Despliegue AMD | ❌ Pendiente |
| Métricas | ❌ No medidas |
