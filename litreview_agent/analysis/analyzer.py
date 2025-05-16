"""
Paper analysis and organization functionality
"""

from typing import List

from litreview_agent.data.models import Paper
from litreview_agent.llm.engine import LLMEngine

class PaperAnalyzer:
    """Methods for analyzing and organizing papers"""
    
    def __init__(self, llm_engine: LLMEngine):
        """Initialize with an LLM engine for text analysis"""
        self.llm_engine = llm_engine
    
    def extract_paper_keywords(self, papers: List[Paper], num_keywords: int = 5) -> List[Paper]:
        """
        Extract keywords from each paper
        
        Args:
            papers: List of papers to analyze
            num_keywords: Number of keywords to extract per paper
            
        Returns:
            Updated list of papers with keywords
        """
        for paper in papers:
            if not paper.keywords:
                if paper.abstract:
                    paper.keywords = self.llm_engine.extract_keywords(paper.title, paper.abstract, num_keywords)
                else:
                    # Only title available
                    paper.keywords = self.llm_engine.extract_keywords(paper.title, "", num_keywords)
        return papers
    
    def detect_duplicates(self, papers: List[Paper], threshold: float = 0.8) -> List[Paper]:
        """
        Detect and mark duplicate papers
        
        Args:
            papers: List of papers to check for duplicates
            threshold: Similarity threshold for considering papers as duplicates
            
        Returns:
            Updated list of papers with duplicates marked
        """
        # First sort by citation count (if available) to keep the more cited papers as originals
        sorted_papers = sorted(papers, key=lambda p: p.citation_count or 0, reverse=True)
        
        # Check each paper against others
        for i, paper1 in enumerate(sorted_papers):
            if paper1.duplicate_of:
                continue  # Already marked as duplicate
                
            for j, paper2 in enumerate(sorted_papers[i+1:], i+1):
                if paper2.duplicate_of:
                    continue  # Already marked as duplicate
                    
                if paper1.is_likely_duplicate_of(paper2, threshold):
                    paper2.duplicate_of = paper1.id
                    print(f"Detected duplicate: '{paper2.title}' is duplicate of '{paper1.title}'")
        
        return papers
    
    def extract_findings(self, papers: List[Paper]) -> List[Paper]:
        """
        Extract key findings from each paper
        
        Args:
            papers: List of papers to analyze
            
        Returns:
            Updated list of papers with key findings
        """
        for paper in papers:
            if not paper.key_findings and paper.abstract:
                self.llm_engine.extract_paper_findings(paper)
        return papers 