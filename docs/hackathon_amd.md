# Estrategia para AMD Developer Hackathon: ACT III

**Fechas:** 12-17 de octubre de 2026
**Plataforma:** lablab.ai
**Track:** TBA (se anuncia el 12 de octubre)
**Premio:** $5,000+

---

## 1. Objetivo

Presentar el **Motor de Orquestación Nonacortex** como caso de uso de hardware AMD con ROCm.

**Mensaje central:**
> Un LLM monolítico no escala. El Nonacortex 5-3-1 distribuye la carga entre modelos especializados, cada uno optimizado para su tarea, sobre GPUs AMD MI300X.

---

## 2. Demo planificada

| Paso | Acción |
|------|--------|
| 1 | Simular N vehículos con datos GPS |
| 2 | Nonacortex procesa y toma decisiones |
| 3 | Mostrar throughput y latencia |
| 4 | Comparar con LLM monolítico |

---

## 3. Métricas objetivo

| Métrica | Objetivo |
|---------|----------|
| Reducción de latencia | ??? (a medir) |
| Throughput | ??? (a medir) |
| VRAM por modelo | ??? (a medir) |

**⚠️ Los números "40% de reducción" y similares son objetivos de diseño, NO resultados medidos. Deben validarse antes del submit.**

---

## 4. Entregables

- [ ] Código en GitHub
- [ ] README actualizado
- [ ] Video demo (2-3 min)
- [ ] Métricas reales medidas
- [ ] Submit en lablab.ai

---

## 5. Recursos

- Créditos: AMD Developer Cloud + DigitalOcean ($100, expiran 3 oct)
- Hardware: MI300X vía créditos
- Modelos: vLLM + ROCm

---

## 6. Riesgos

| Riesgo | Mitigación |
|--------|------------|
| Créditos expiran antes | Verificar uso antes del 3 oct |
| vLLM no corre en ROCm | Probar con modelo pequeño primero |
| Track no encaja con KST | Plan B: presentar Nonacortex genérico |
| Métricas bajas | Documentar honestamente, no inflar |