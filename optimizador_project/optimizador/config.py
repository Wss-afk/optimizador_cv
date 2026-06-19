"""
Configuración global del optimizador de CVs.
Define modelos, parámetros de RAG, y configuración del LLM.
"""

import os
from pathlib import Path

# ==================== RUTAS ====================

PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT.parent / "docs"
CHROMA_DB_DIR = PROJECT_ROOT.parent / "chroma_db"
DATA_DIR = PROJECT_ROOT.parent / "data"

# Crear directorios si no existen
CHROMA_DB_DIR.mkdir(exist_ok=True)
DOCS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)


# ==================== LLM CONFIGURATION ====================

LLM_CONFIG = {
    "model": "qwen3:8b",
    "temperature_extraction": 0.1,      # Extracción precisa (Job Analyzer)
    "temperature_optimization": 0.4,    # Creatividad controlada (CV Optimizer)
    "temperature_review": 0.2,          # Revisión precisa (ATS Reviewer)
    "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    "request_timeout": 300,              # 5 minutos timeout
}


# ==================== RAG CONFIGURATION ====================

RAG_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 50,
    "embedding_model": "nomic-embed-text",
    "collection_name": "cv_knowledge_base",
    "persist_directory": str(CHROMA_DB_DIR),
    "top_k": 3,                         # Documentos a recuperar
}


# ==================== PROMPT TEMPLATES ====================

PROMPTS = {
    "job_analyzer": """Eres un experto en análisis de ofertas de empleo.
Analiza la siguiente oferta y extrae la información en formato JSON estructurado.
Identifica: título del puesto, habilidades técnicas y blandas, años de experiencia,
nivel de seniority, palabras clave relevantes para ATS, responsabilidades principales
y tecnologías mencionadas.

Oferta de empleo:
{job_posting_text}

Devuelve un JSON válido con la siguiente estructura:
{{
    "job_title": "...",
    "required_skills": [...],
    "soft_skills": [...],
    "years_experience": 0,
    "seniority_level": "...",
    "keywords_ats": [...],
    "responsibilities": [...],
    "technologies": [...],
    "salary_range": "..."
}}""",

    "cv_optimizer": """Eres un experto en optimización de currículums para ATS y reclutadores.

## Análisis de la oferta de empleo:
{job_analysis}

## CV original del candidato:
{cv_text}

## Mejores prácticas (de la base de conocimiento):
{rag_context}

## Instrucciones:
1. Analiza el CV y extrae: nombre, habilidades, experiencia, formación, certificaciones
2. Compara con los requisitos de la oferta
3. Reescribe el CV optimizándolo para esta oferta específica:
   - Añade palabras clave ATS de forma natural
   - Destaca logros cuantificables
   - Reordena secciones por relevancia
   - NO inventes experiencia
4. Devuelve un JSON con: análisis del CV, CV optimizado, cambios realizados, keywords añadidas, match_score (0-100)

Devuelve un JSON válido con esta estructura:
{{
    "cv_analysis": {{
        "candidate_name": "...",
        "current_skills": [...],
        "experience_years": 0,
        "education": [...],
        "certifications": [...],
        "strengths": [...],
        "gaps": [...]
    }},
    "optimized_cv": "...",
    "changes_made": [...],
    "keywords_added": [...],
    "match_score": 0.0
}}""",

    "ats_reviewer": """Eres un sistema ATS (Applicant Tracking System) y revisor final de CVs.

## CV optimizado a evaluar:
{optimized_cv}

## Requisitos del puesto (keywords ATS):
{keywords_ats}

## Reglas ATS (de la base de conocimiento):
{rag_context}

## Tareas:
1. Evalúa la compatibilidad ATS:
   - ¿Qué keywords están presentes?
   - ¿Qué keywords faltan?
   - Calcula puntuaciones: keyword_match (0-100), format_score (0-100), completeness (0-100), overall_score (0-100)
2. Realiza revisión final:
   - Corrige errores gramaticales
   - Elimina redundancias
   - Mejora la redacción
   - Uniformiza el formato
3. Devuelve un JSON con el CV final + puntuaciones + recomendaciones

Devuelve un JSON válido con esta estructura:
{{
    "ats_score": {{
        "keyword_match": 0.0,
        "format_score": 0.0,
        "completeness": 0.0,
        "overall_score": 0.0
    }},
    "final_cv": "...",
    "missing_keywords": [...],
    "found_keywords": [...],
    "recommendations": [...],
    "improvements_applied": [...]
}}""",
}


# ==================== AGENT CONFIGURATION ====================

AGENTS_CONFIG = {
    "job_analyzer": {
        "name": "Job Analyzer",
        "description": "Analiza ofertas de empleo y extrae requisitos",
        "temperature": LLM_CONFIG["temperature_extraction"],
        "model": LLM_CONFIG["model"],
    },
    "cv_optimizer": {
        "name": "CV Optimizer",
        "description": "Analiza y optimiza CVs para la oferta",
        "temperature": LLM_CONFIG["temperature_optimization"],
        "model": LLM_CONFIG["model"],
    },
    "ats_reviewer": {
        "name": "ATS Reviewer",
        "description": "Evalúa compatibilidad ATS y revisa finalmente el CV",
        "temperature": LLM_CONFIG["temperature_review"],
        "model": LLM_CONFIG["model"],
    },
}
