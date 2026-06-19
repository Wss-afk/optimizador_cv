"""
ATS Reviewer Agent: Evalúa compatibilidad ATS y realiza revisión final del CV.
Incluye: análisis ATS + revisión final de calidad.
"""

import json
import logging
from typing import List

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

from optimizador.models.schemas import ATSScore, ATSReviewResult, JobAnalysis
from optimizador.config import LLM_CONFIG, PROMPTS, AGENTS_CONFIG
from optimizador.rag.vector_store import get_knowledge_base

logger = logging.getLogger(__name__)


class ATSReviewerAgent:
    """Agente para evaluar compatibilidad ATS y realizar revisión final."""
    
    def __init__(self):
        """Inicializa el agente con el modelo LLM y la base de conocimiento."""
        self.config = AGENTS_CONFIG["ats_reviewer"]
        self.llm = ChatOllama(
            model=self.config["model"],
            temperature=self.config["temperature"],
            base_url=LLM_CONFIG["base_url"],
            request_timeout=LLM_CONFIG["request_timeout"],
        )
        self.prompt_template = PROMPTS["ats_reviewer"]
        
        # Inicializar base de conocimiento RAG
        try:
            self.knowledge_base = get_knowledge_base()
        except Exception as e:
            logger.warning(f"No se pudo inicializar RAG: {str(e)}. Continuando sin RAG.")
            self.knowledge_base = None
    
    def review(
        self,
        optimized_cv: str,
        job_analysis: JobAnalysis,
    ) -> ATSReviewResult:
        """
        Evalúa la compatibilidad ATS del CV y realiza revisión final.
        
        Args:
            optimized_cv: CV optimizado del paso anterior
            job_analysis: Análisis de la oferta de empleo
            
        Returns:
            ATSReviewResult con puntuaciones, CV final, y recomendaciones
            
        Raises:
            ValueError: Si no se puede procesar el CV
        """
        logger.info("Iniciando revisión ATS...")
        
        # Obtener contexto RAG sobre reglas ATS
        rag_context = self._get_rag_context()
        
        # Preparar prompt
        keywords_ats_str = ", ".join(job_analysis.keywords_ats)
        prompt = self.prompt_template.format(
            optimized_cv=optimized_cv,
            keywords_ats=keywords_ats_str,
            rag_context=rag_context,
        )
        
        try:
            # Llamar al LLM
            logger.debug(f"Enviando CV para revisión ATS al LLM ({self.config['model']})...")
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            response_text = response.content
            
            logger.debug(f"Respuesta del LLM recibida ({len(response_text)} chars)")
            
            # Parsear respuesta
            result = self._parse_response(response_text)
            
            logger.info(
                f"Revisión ATS completada: {result.ats_score.overall_score:.1f}% puntuación global"
            )
            return result
            
        except Exception as e:
            logger.error(f"Error en revisión ATS: {str(e)}")
            raise
    
    def _get_rag_context(self) -> str:
        """
        Obtiene contexto de la base de conocimiento RAG sobre reglas ATS.
        
        Returns:
            Contexto formateado como string
        """
        if self.knowledge_base is None:
            return "No hay contexto disponible de la base de conocimiento."
        
        try:
            query = "reglas de sistemas ATS y formatos compatibles para currículums"
            context = self.knowledge_base.get_context_for_query(query, k=3)
            return context
        except Exception as e:
            logger.warning(f"Error obtiendo contexto RAG: {str(e)}")
            return "No se pudo obtener contexto de la base de conocimiento."
    
    def _parse_response(self, response_text: str) -> ATSReviewResult:
        """
        Parsea la respuesta del LLM en un ATSReviewResult.
        
        Args:
            response_text: Texto de respuesta del LLM
            
        Returns:
            ATSReviewResult parseado
            
        Raises:
            ValueError: Si no se puede parsear el JSON
        """
        try:
            # Extraer JSON de la respuesta
            json_str = self._extract_json(response_text)
            data = json.loads(json_str)
            
            # Parsear puntuaciones ATS
            ats_score_data = data.get("ats_score", {})
            ats_score = ATSScore(
                keyword_match=float(ats_score_data.get("keyword_match", 0.0)),
                format_score=float(ats_score_data.get("format_score", 0.0)),
                completeness=float(ats_score_data.get("completeness", 0.0)),
                overall_score=float(ats_score_data.get("overall_score", 0.0)),
            )
            
            # Crear resultado
            result = ATSReviewResult(
                ats_score=ats_score,
                final_cv=data.get("final_cv", ""),
                missing_keywords=data.get("missing_keywords", []),
                found_keywords=data.get("found_keywords", []),
                recommendations=data.get("recommendations", []),
                improvements_applied=data.get("improvements_applied", []),
            )
            
            return result
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error parseando respuesta de ATS Reviewer: {str(e)}")
            logger.debug(f"Respuesta: {response_text[:500]}")
            raise ValueError(f"No se pudo parsear la respuesta del LLM: {str(e)}")
    
    def _extract_json(self, text: str) -> str:
        """
        Extrae JSON de un texto que puede contener explicación.
        
        Args:
            text: Texto que contiene JSON
            
        Returns:
            String JSON válido
            
        Raises:
            ValueError: Si no encuentra JSON válido
        """
        # Intenta encontrar el JSON entre llaves
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No se encontró JSON en la respuesta")
        
        json_str = text[start_idx:end_idx]
        return json_str


def create_ats_reviewer() -> ATSReviewerAgent:
    """Factory para crear instancia del agente."""
    return ATSReviewerAgent()
