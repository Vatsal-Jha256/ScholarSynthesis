"""
LitReviewAgent: An agentic AI system for automated literature reviews

This system takes a paper title and abstract, searches for relevant literature,
organizes the findings, and generates a review section with citations in LaTeX format.
"""

__version__ = "0.2.0"

from litreview_agent.core.agent import LitReviewAgent
from litreview_agent.data.models import Paper, ResearchPlan, KeyInsight 