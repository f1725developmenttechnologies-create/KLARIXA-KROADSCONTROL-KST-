# KLARIXA KROADSCONTROL (KST)

**Plataforma de movilidad y logística P2P orquestada por IA distribuida, optimizada para hardware AMD.**

---

## ⚠️ PROTOCOLO DE CONFIDENCIALIDAD

**WIPO / NNN / NDA**

- Titular: EinsRos Global Cortex Ultd — F1725 Development Technologies
- WIPO Customer ID: user_CO_SANCHEZ-COLMENARES_FREDDY-ADRIAN_0876
- Autor: Freddy Adrián Sánchez Colmenares
- Contacto corporativo: f1725developmenttechnologies@gmail.com
- Contacto técnico: f1725.ai.dev@gmail.com

Toda reproducción, distribución o uso no autorizado queda prohibido bajo protocolo NNN/NDA/WIPO.

---

## DESCRIPCIÓN

KROADSCONTROL (KST) es un motor de orquestación de movilidad de alta concurrencia. A diferencia de las plataformas actuales basadas en LLM monolítico, KST utiliza una arquitectura de IA distribuida (Nonacortex) para procesar rutas, pagos, geolocalización y comunicación en tiempo real, delegando cada tarea al modelo más eficiente para cada carga.

**Objetivo del hackathon:** demostrar la orquestación de múltiples modelos sobre GPUs AMD con ROCm, mostrando reducción de latencia y aumento de throughput frente a un LLM monolítico.

---

## ARQUITECTURA NONACORTEX 5-3-1

Nueve "chips" lógicos (instancias de modelos) trabajando en paralelo:

| Rol | Cantidad | Función |
|-----|----------|---------|
| **Central (Router)** | 1 | Analiza intención y delega |
| **Periféricos alto rendimiento** | 3 | Lógica, NLP, Visión |
| **Borde (Edge)** | 5 | Detección de fraude, ETA, encriptación |

### Mapeo de modelos a hardware AMD

| Chip | Modelo | Justificación |
|------|--------|---------------|
| Central | Qwen 2.5 (32B) | Function Calling y razonamiento |
| Lógica | DeepSeek Coder / V3 | Lógica estructurada, geometría |
| NLP | Gemma 2 (9B/27B) | Chat en tiempo real |
| Visión | Qwen-VL | Procesamiento de imágenes |
| Edge (5) | Qwen 2.5 (1.5B) / Gemma 2B | Inferencia local de baja latencia |

---

## STACK TECNOLÓGICO

### Backend
- Python 3.10+
- FastAPI (asíncrono)
- PostgreSQL + Redis
- Uber H3 (geolocalización hexagonal)

### Frontend
- Next.js + React + Tailwind CSS
- Recharts / D3.js

### Hardware y despliegue
- AMD Instinct MI300X (AMD Developer Cloud)
- vLLM con soporte ROCm/HIP
- Docker + Docker Compose

---

## INSTALACIÓN (DESARROLLO)

```bash
# Clonar repositorio
git clone https://github.com/f1725developmenttechnologies-create/klarixa-kroadscontrol.git
cd klarixa-kroadscontrol

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con las claves correspondientes

# Ejecutar servidor de desarrollo
uvicorn src.main:app --reload