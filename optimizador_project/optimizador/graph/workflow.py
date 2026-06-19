"""
LangGraph Workflow: Orquestador de agentes usando StateGraph.
Coordina el flujo: Job Analyzer → CV Optimizer → ATS Reviewer
"""

import logging
from typing import cast

from langgraph.graph import StateGraph, START, END
from langgraph.types import StateSnapshot

from optimizador.models.schemas import (
    WorkflowState,
    JobAnalysis,
    CVOptimizationResult,
    ATSReviewResult,
)
from optimizador.agents.job_analyzer import create_job_analyzer
from optimizador.agents.cv_optimizer import create_cv_optimizer
from optimizador.agents.ats_reviewer import create_ats_reviewer

logger = logging.getLogger(__name__)


class CVOptimizationWorkflow:
    """Orquestador de workflow usando LangGraph StateGraph."""
    
    def __init__(self):
        """Inicializa los agentes y construye el grafo."""
        self.job_analyzer = create_job_analyzer()
        self.cv_optimizer = create_cv_optimizer()
        self.ats_reviewer = create_ats_reviewer()
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Construye el StateGraph del workflow.
        
        Flujo:
        START → analyze_job → optimize_cv → review_ats → END
        
        Returns:
            StateGraph configurado
        """
        # Crear grafo
        graph_builder = StateGraph(WorkflowState)
        
        # Añadir nodos
        graph_builder.add_node("analyze_job", self._analyze_job_node)
        graph_builder.add_node("optimize_cv", self._optimize_cv_node)
        graph_builder.add_node("review_ats", self._review_ats_node)
        
        # Conectar nodos
        graph_builder.add_edge(START, "analyze_job")
        graph_builder.add_edge("analyze_job", "optimize_cv")
        graph_builder.add_edge("optimize_cv", "review_ats")
        graph_builder.add_edge("review_ats", END)
        
        # Compilar grafo
        return graph_builder.compile()
    
    def _analyze_job_node(self, state: WorkflowState) -> dict:
        """
        Nodo 1: Analiza la oferta de empleo.
        
        Args:
            state: Estado actual del workflow
            
        Returns:
            Estado actualizado con análisis de oferta
        """
        logger.info("[NODO 1] Ejecutando Job Analyzer...")
        
        try:
            state.current_step = "job_analysis"
            
            # Ejecutar Job Analyzer
            job_analysis = self.job_analyzer.analyze(state.job_posting_text)
            
            # Actualizar estado
            return {
                "job_analysis": job_analysis,
                "current_step": "cv_optimization",
            }
            
        except Exception as e:
            logger.error(f"Error en Job Analyzer: {str(e)}")
            error_msg = f"Error analizando oferta de empleo: {str(e)}"
            return {
                "current_step": "error",
                "errors": [error_msg],
            }
    
    def _optimize_cv_node(self, state: WorkflowState) -> dict:
        """
        Nodo 2: Analiza y optimiza el CV.
        
        Args:
            state: Estado actual del workflow
            
        Returns:
            Estado actualizado con CV optimizado
        """
        logger.info("[NODO 2] Ejecutando CV Optimizer...")
        
        try:
            # Verificar que tenemos análisis de oferta
            if state.job_analysis is None:
                raise ValueError("No se tiene análisis de oferta de empleo")
            
            state.current_step = "cv_optimization"
            
            # Ejecutar CV Optimizer
            optimization_result: CVOptimizationResult = self.cv_optimizer.optimize(
                cv_text=state.cv_text,
                job_analysis=state.job_analysis,
            )
            
            # Actualizar estado
            return {
                "cv_analysis": optimization_result.cv_analysis,
                "optimized_cv": optimization_result.optimized_cv,
                "changes_made": optimization_result.changes_made,
                "keywords_added": optimization_result.keywords_added,
                "match_score": optimization_result.match_score,
                "current_step": "ats_review",
            }
            
        except Exception as e:
            logger.error(f"Error en CV Optimizer: {str(e)}")
            error_msg = f"Error optimizando CV: {str(e)}"
            return {
                "current_step": "error",
                "errors": state.errors + [error_msg],
            }
    
    def _review_ats_node(self, state: WorkflowState) -> dict:
        """
        Nodo 3: Evalúa compatibilidad ATS y realiza revisión final.
        
        Args:
            state: Estado actual del workflow
            
        Returns:
            Estado actualizado con CV final y puntuaciones ATS
        """
        logger.info("[NODO 3] Ejecutando ATS Reviewer...")
        
        try:
            # Verificar que tenemos CV optimizado
            if state.optimized_cv is None:
                raise ValueError("No se tiene CV optimizado del paso anterior")
            
            if state.job_analysis is None:
                raise ValueError("No se tiene análisis de oferta de empleo")
            
            state.current_step = "ats_review"
            
            # Ejecutar ATS Reviewer
            ats_result: ATSReviewResult = self.ats_reviewer.review(
                optimized_cv=state.optimized_cv,
                job_analysis=state.job_analysis,
            )
            
            # Actualizar estado
            return {
                "ats_score": ats_result.ats_score,
                "final_cv": ats_result.final_cv,
                "missing_keywords": ats_result.missing_keywords,
                "found_keywords": ats_result.found_keywords,
                "ats_recommendations": ats_result.recommendations,
                "improvements_applied": ats_result.improvements_applied,
                "current_step": "complete",
            }
            
        except Exception as e:
            logger.error(f"Error en ATS Reviewer: {str(e)}")
            error_msg = f"Error en revisión ATS: {str(e)}"
            return {
                "current_step": "error",
                "errors": state.errors + [error_msg],
            }
    
    def invoke(self, job_posting_text: str, cv_text: str) -> WorkflowState:
        """
        Ejecuta el workflow completo.
        
        Args:
            job_posting_text: Texto de la oferta de empleo
            cv_text: Texto del CV
            
        Returns:
            Estado final del workflow con todos los resultados
        """
        logger.info("=" * 60)
        logger.info("INICIANDO WORKFLOW DE OPTIMIZACIÓN DE CV")
        logger.info("=" * 60)
        
        # Estado inicial
        initial_state = WorkflowState(
            job_posting_text=job_posting_text,
            cv_text=cv_text,
            current_step="start",
        )
        
        # Ejecutar grafo
        try:
            final_state = self.graph.invoke(initial_state)
            logger.info("=" * 60)
            logger.info("WORKFLOW COMPLETADO EXITOSAMENTE")
            logger.info("=" * 60)
            return final_state
        
        except Exception as e:
            logger.error(f"Error ejecutando workflow: {str(e)}")
            initial_state.current_step = "error"
            initial_state.errors = [str(e)]
            return initial_state


def create_workflow() -> CVOptimizationWorkflow:
    """Factory para crear instancia del workflow."""
    return CVOptimizationWorkflow()
