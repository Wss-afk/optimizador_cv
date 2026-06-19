"""
CV Optimizer Agent: Analiza CV del candidato y lo optimiza para la oferta.
Incluye: análisis del CV original + optimización + integración con RAG.
"""

import json
import logging
from typing import Optional

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

from optimizador.models.schemas import CVAnalysis, CVOptimizationResult, JobAnalysis
from optimizador.config import LLM_CONFIG, PROMPTS, AGENTS_CONFIG
from optimizador.rag.vector_store import get_knowledge_base

logger = logging.getLogger(__name__)


class CVOptimizerAgent:
    """Agente para analizar y optimizar currículums."""
    
    def __init__(self):
        """Inicializa el agente con el modelo LLM y la base de conocimiento."""
        self.config = AGENTS_CONFIG["cv_optimizer"]
        self.llm = ChatOllama(
            model=self.config["model"],
            temperature=self.config["temperature"],
            base_url=LLM_CONFIG["base_url"],
            request_timeout=LLM_CONFIG["request_timeout"],
        )
        self.prompt_template = PROMPTS["cv_optimizer"]
        
        # Inicializar base de conocimiento RAG
        try:
            self.knowledge_base = get_knowledge_base()
        except Exception as e:
            logger.warning(f"No se pudo inicializar RAG: {str(e)}. Continuando sin RAG.")
            self.knowledge_base = None
    
    def optimize(
        self,
        cv_text: str,
        job_analysis: JobAnalysis,
    ) -> CVOptimizationResult:
        """
        Analiza y optimiza un CV para una oferta de empleo.
        
        Args:
            cv_text: Texto del CV original
            job_analysis: Análisis de la oferta de empleo
            
        Returns:
            CVOptimizationResult con análisis, CV optimizado, y cambios
            
        Raises:
            ValueError: Si no se puede procesar el CV o la oferta
        """
        logger.info("Iniciando optimización de CV...")
        
        # Obtener contexto RAG
        rag_context = self._get_rag_context()
        
        # Preparar prompt
        job_analysis_str = json.dumps(job_analysis.model_dump(), ensure_ascii=False, indent=2)
        prompt = self.prompt_template.format(
            job_analysis=job_analysis_str,
            cv_text=cv_text,
            rag_context=rag_context,
        )
        
        try:
            # Llamar al LLM
            logger.debug(f"Enviando CV y oferta al LLM ({self.config['model']})...")
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            response_text = response.content
            
            logger.debug(f"Respuesta del LLM recibida ({len(response_text)} chars)")
            
            # Parsear respuesta
            result = self._parse_response(response_text)
            
            logger.info(
                f"CV optimizado: {result.match_score:.1f}% match, "
                f"{len(result.keywords_added)} keywords añadidas"
            )
            return result
            
        except Exception as e:
            logger.error(f"Error en optimización de CV: {str(e)}")
            raise
    
    def _get_rag_context(self) -> str:
        """
        Obtiene contexto de la base de conocimiento RAG.
        
        Returns:
            Contexto formateado como string
        """
        if self.knowledge_base is None:
            return "No hay contexto disponible de la base de conocimiento."
        
        try:
            query = "mejores prácticas para escribir un currículum profesional optimizado para ATS"
            context = self.knowledge_base.get_context_for_query(query, k=3)
            return context
        except Exception as e:
            logger.warning(f"Error obtiendo contexto RAG: {str(e)}")
            return "No se pudo obtener contexto de la base de conocimiento."
    
    def _parse_response(self, response_text: str) -> CVOptimizationResult:
        """
        Parsea la respuesta del LLM en un CVOptimizationResult.
        
        Args:
            response_text: Texto de respuesta del LLM
            
        Returns:
            CVOptimizationResult parseado
            
        Raises:
            ValueError: Si no se puede parsear el JSON
        """
        try:
            # Extraer JSON de la respuesta
            json_str = self._extract_json(response_text)
            data = json.loads(json_str)
            
            # Parsear componentes
            cv_analysis = CVAnalysis(
                candidate_name=data.get("cv_analysis", {}).get("candidate_name", "Unknown"),
                current_skills=data.get("cv_analysis", {}).get("current_skills", []),
                experience_years=int(data.get("cv_analysis", {}).get("experience_years", 0)),
                education=data.get("cv_analysis", {}).get("education", []),
                certifications=data.get("cv_analysis", {}).get("certifications", []),
                strengths=data.get("cv_analysis", {}).get("strengths", []),
                gaps=data.get("cv_analysis", {}).get("gaps", []),
            )
            
            # Crear resultado
            result = CVOptimizationResult(
                cv_analysis=cv_analysis,
                optimized_cv=data.get("optimized_cv", ""),
                changes_made=data.get("changes_made", []),
                keywords_added=data.get("keywords_added", []),
                match_score=float(data.get("match_score", 0.0)),
            )
            
            return result
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error parseando respuesta de CV Optimizer: {str(e)}")
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


def create_cv_optimizer() -> CVOptimizerAgent:
    """Factory para crear instancia del agente."""
    return CVOptimizerAgent()
