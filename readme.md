Optimizador de currículums — un agente analiza la oferta de empleo, otro reescribe el CV para ajustarlo, un agente ATS evalúa la compatibilidad con filtros automáticos y un revisor final pule el resultado.

# Optimizador de Currículums — División de Tareas (3 Desarrolladores)

---

## 📋 Visión General del Proyecto

Sistema multi-agente que:
1. Analiza la oferta de empleo
2. Reescribe el CV para optimizarlo
3. Evalúa compatibilidad ATS
4. Pule y finaliza el resultado

---

## 👤 **PERSONA 1: Analista de Oferta + Arquitectura Base**

### Responsabilidades Principales
- ✅ Diseñar la arquitectura general del sistema
- ✅ Crear el **Agente 1: Analizador de Oferta** (Job Parser Agent)
- ✅ Gestionar la integración y orquestación de agentes
- ✅ Definir estructura de datos común (dataclasses/Pydantic)

### Puntos Clave Técnicos
```python
# Extraer de la oferta:
- job_title: str
- required_skills: List[str]
- years_experience: int
- soft_skills: List[str]
- keywords_ats: List[str]
- responsibilities: List[str]
- salary_range: Optional[str]
- benefits: List[str]

# Output estructura
class JobAnalysis(BaseModel):
    job_title: str
    required_skills: List[str]
    key_responsibilities: List[str]
    ats_keywords: List[str]
    seniority_level: str
    score_match_potential: float  # 0-1
```

### Herramientas a Usar
- **LLM Framework**: LangChain o LlamaIndex
- **Parsing**: spaCy, regex, o Claude API
- **Data Validation**: Pydantic
- **Orchestración**: simple queue/dict o tool_calling de LLM

### Entregables
- `agents/job_analyzer.py` — Agente analizador
- `models/schemas.py` — Estructuras de datos compartidas
- `main.py` o `orchestrator.py` — Coordinación central

### Interfaz con Otros Desarrolladores
```python
# ← Recibe: job_posting (str)
job_analysis = analyze_job(job_posting)
# → Envía: JobAnalysis object a Persona 2 y 3
```

---

## 👤 **PERSONA 2: Reescriptor de CV**

### Responsabilidades Principales
- ✅ Crear el **Agente 2: Optimizador de CV**
- ✅ Reescribir/ajustar contenido del CV
- ✅ Mantener coherencia y naturalidad
- ✅ Implementar varias estrategias de reescritura

### Puntos Clave Técnicos
```python
class CVOptimizer:
    """
    Tomar JobAnalysis + CV original
    → Producir CV optimizado
    """
    
    def optimize(self, job_analysis: JobAnalysis, cv_text: str) -> str:
        # 1. Identificar skills del CV
        # 2. Mapear skills → job_analysis.required_skills
        # 3. Reescribir bullets/logros relevantes
        # 4. Priorizar por frecuencia de keywords
        # 5. Mantener honestidad (no inventar)
        
        return optimized_cv
```

### Estrategias de Reescritura
1. **Keyword Matching** — Insertar keywords ATS naturalmente
2. **Achievement Reframing** — Destacar logros relevantes
3. **Skills Repositioning** — Poner skills relevantes al frente
4. **Responsibility Alignment** — Conectar experiencia con job requirements

### Herramientas a Usar
- **LLM Calls**: Usar prompts bien crafted para Claude/GPT
- **Text Processing**: NLTK, spaCy para análisis
- **Validation**: Verificar que no se inventan cosas
- **Versioning**: Guardar CV original + versiones

### Entregables
- `agents/cv_optimizer.py` — Agente reescriptor
- `utils/cv_parser.py` — Parser de CV (extrae secciones)
- `utils/prompt_templates.py` — Prompts para reescritura

### Interfaz con Otros Desarrolladores
```python
# ← Recibe: JobAnalysis (de Persona 1) + CV (archivo/string)
optimized_cv = optimize_cv(job_analysis, cv_text)
# → Envía: optimized_cv (str) a Persona 3 y 4
```

---

## 👤 **PERSONA 3: Evaluador ATS + Revisor Final**

### Responsabilidades Principales
- ✅ Crear el **Agente 3: Evaluador ATS**
- ✅ Crear el **Agente 4: Revisor/Pulidor Final**
- ✅ Implementar scoring de compatibilidad
- ✅ Proporcionar feedback accionable

### Puntos Clave Técnicos

#### Agente 3: ATS Evaluator
```python
class ATSEvaluator:
    """
    Simular filtros ATS comunes:
    - Keyword matching
    - Format parsing
    - Section detection
    - Readability
    """
    
    def evaluate(self, cv: str, job_analysis: JobAnalysis) -> ATSScore:
        scores = {
            'keyword_match': float,      # 0-100
            'format_score': float,        # 0-100
            'readability': float,         # 0-100
            'ats_compatibility': float,   # 0-100
            'overall_score': float        # 0-100
        }
        recommendations = List[str]
        return ATSScore(scores, recommendations)
```

#### Agente 4: Final Reviewer
```python
class FinalReviewer:
    """
    Pulir y optimizar resultado final:
    - Correcciones gramaticales
    - Coherencia visual
    - Mejoras de formato
    - Último check de calidad
    """
    
    def review_and_polish(self, cv: str, ats_feedback: ATSScore) -> FinalCV:
        # Aplicar feedback de ATS
        # Revisar ortografía/gramática
        # Optimizar formato
        # Sugerir mejoras finales
        return FinalCV(polished_cv, improvements)
```

### Herramientas a Usar
- **ATS Simulation**: Reglas + ML para keyword density
- **NLP**: spaCy, TextBlob para análisis
- **Spelling/Grammar**: PyEnchant, language_tool_python
- **Scoring Logic**: Custom scoring system o ML simple

### Criterios ATS a Evaluar
- ✓ Presencia de keywords por secciones
- ✓ Densidad de keywords (sin spam)
- ✓ Estructura clara (headers, bullets)
- ✓ Legibilidad (fuente, espaciado)
- ✓ Formatos comunes (PDF/TXT parseables)
- ✓ Ausencia de tablas/gráficos complejos

### Entregables
- `agents/ats_evaluator.py` — Evaluador ATS
- `agents/final_reviewer.py` — Revisor final
- `models/feedback.py` — Estructuras de feedback
- `utils/ats_rules.py` — Reglas y criteria ATS

### Interfaz con Otros Desarrolladores
```python
# ← Recibe: optimized_cv (de Persona 2) + JobAnalysis (de Persona 1)
ats_score = evaluate_ats(optimized_cv, job_analysis)
# → Usa feedback ATS
final_cv = review_and_polish(optimized_cv, ats_score)
# → Envía: FinalCV object + report
```

---

## 🔗 Flujo de Integración

```
┌─────────────────────────────────────────────────────────────┐
│  INPUT: Job Posting + Original CV                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  PERSONA 1: Job Analyzer                                    │
│  Extrae: skills, keywords, requirements, seniority          │
│  Output: JobAnalysis object                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  PERSONA 2: CV Optimizer                                    │
│  Reescribe CV basado en JobAnalysis                          │
│  Output: Optimized CV text                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
         ┌────────────────┴────────────────┐
         ↓                                  ↓
┌──────────────────────┐    ┌──────────────────────┐
│ PERSONA 3a:          │    │ PERSONA 3b:          │
│ ATS Evaluator        │    │ Final Reviewer       │
│ Scoring + Feedback   │    │ Polish + Grammar     │
└──────────────────────┘    └──────────────────────┘
         │                                  │
         └────────────────┬────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  OUTPUT: Final optimized CV + Report                        │
│  - Final CV text                                            │
│  - ATS Scores                                               │
│  - Recommendations                                          │
│  - Improvement suggestions                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Estructura de Carpetas Recomendada

```
cv-optimizer/
├── main.py                 # Punto de entrada (Persona 1)
├── requirements.txt
├── config.py               # API keys, modelos, configs
│
├── models/
│   ├── __init__.py
│   ├── schemas.py          # JobAnalysis, ATSScore, etc. (Persona 1)
│   └── feedback.py         # FinalCV, recommendations (Persona 3)
│
├── agents/
│   ├── __init__.py
│   ├── job_analyzer.py     # Persona 1
│   ├── cv_optimizer.py     # Persona 2
│   ├── ats_evaluator.py    # Persona 3
│   └── final_reviewer.py   # Persona 3
│
├── utils/
│   ├── __init__.py
│   ├── cv_parser.py        # Persona 2
│   ├── prompt_templates.py # Persona 2
│   ├── ats_rules.py        # Persona 3
│   └── validators.py       # Validaciones comunes
│
├── tests/
│   ├── test_job_analyzer.py
│   ├── test_cv_optimizer.py
│   ├── test_ats_evaluator.py
│   └── test_final_reviewer.py
│
└── data/
    ├── sample_cv.txt
    └── sample_job_posting.txt
```

---

## 🤝 Puntos de Coordinación Críticos

### 1. **Definición de Interfaces (DÍA 1)**
- Reunión rápida para acordar:
  - Estructura de `JobAnalysis` (Persona 1)
  - Formato de entrada/salida de cada agente
  - Tipo de datos compartidos

### 2. **Versionamiento de Modelos**
- Usar Pydantic con `model_validate()` para compatibilidad
- Documentar cambios en schemas

### 3. **Testing de Integración**
```python
# test_integration.py
def test_full_pipeline():
    job = "Senior Python Developer..."
    cv = "John Doe, Software Engineer..."
    
    # Persona 1
    job_analysis = analyze_job(job)
    
    # Persona 2
    optimized_cv = optimize_cv(job_analysis, cv)
    
    # Persona 3
    ats_score = evaluate_ats(optimized_cv, job_analysis)
    final_cv = review_and_polish(optimized_cv, ats_score)
    
    assert final_cv.overall_score > 70
    assert len(final_cv.recommendations) > 0
```

### 4. **Comunicación de Cambios**
- Branch por persona o feature branches
- PRs con descripción clara
- Documentar cambios en schemas

---

## 📊 Criterios de Éxito

| Persona | Métrica | Meta |
|---------|---------|------|
| **1** | Job Analysis accuracy | 95% keywords correctly identified |
| **2** | CV relevance improvement | +40% keyword alignment |
| **3a** | ATS score correlation | Matches real ATS (75%+ correlation) |
| **3b** | Final CV quality | 0 grammar errors, 100% readable |

---

## 🚀 Plan de Trabajo Sugerido

### Fase 1: Setup (Día 1-2)
- [ ] Crear repo compartido
- [ ] Definir schemas en `models/schemas.py`
- [ ] Cada persona crea estructura básica de su agente

### Fase 2: Development (Día 3-7)
- [ ] Persona 1: Completa Job Analyzer
- [ ] Persona 2: Completa CV Optimizer
- [ ] Persona 3: Completa ATS Evaluator + Final Reviewer

### Fase 3: Integration (Día 8-9)
- [ ] Conectar agentes en `main.py`
- [ ] Testing de pipeline completo
- [ ] Ajustes de compatibilidad

### Fase 4: Polish (Día 10)
- [ ] Documentación
- [ ] Ejemplos de uso
- [ ] Manual de mantenimiento

---

## 💡 Tips Prácticos

1. **Usa Pydantic** para validación automática de datos
2. **Documenta prompts** — guardar versiones de prompts usados
3. **Logging detallado** — cada agente debe loguear decisiones
4. **Mock data** — crear CV y job postings de prueba
5. **Versionado de CV** — guardar todas las versiones (original, optimizado, final)
6. **Reportes** — generar HTML o PDF con resultados

---

## 📝 Template para Inicio de Sesión

Cada persona puede usar este template para actualizar al equipo:

```markdown
## [PERSONA X] - Status de Hoy

**Logros:**
- [ ] Tarea 1
- [ ] Tarea 2

**Bloqueadores:**
- Esperando decision sobre X

**Plan para mañana:**
- Implementar Y
- Revisar código

**Interfaces necesarias:**
- Feedback sobre schema Z
```

---

**Creado**: 2025
**Proyecto**: Optimizador de Currículums
**Duración estimada**: 2 semanas