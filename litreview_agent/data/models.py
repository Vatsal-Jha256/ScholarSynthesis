"""
Data structures for LitReviewAgent
"""

import re
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ResearchPlan:
    """Research plan for organizing the literature review process"""
    title: str
    abstract: str
    keywords: List[str] = field(default_factory=list)
    research_questions: List[str] = field(default_factory=list)
    search_strategies: List[Dict[str, Any]] = field(default_factory=list)
    focus_areas: List[str] = field(default_factory=list)
    methodology_interest: float = 0.5
    recency_preference: float = 0.5  # 0.0 = prefer older seminal works, 1.0 = prefer newest papers
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "created"  # created, in_progress, completed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "title": self.title,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "research_questions": self.research_questions,
            "search_strategies": self.search_strategies,
            "focus_areas": self.focus_areas,
            "methodology_interest": self.methodology_interest,
            "recency_preference": self.recency_preference,
            "created_at": self.created_at.isoformat(),
            "status": self.status
        }
    
    def to_markdown(self) -> str:
        """Convert to markdown format for display"""
        md = f"# Research Plan: {self.title}\n\n"
        md += f"**Status:** {self.status}\n"
        md += f"**Created:** {self.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        md += "## Research Focus\n\n"
        md += f"{self.abstract}\n\n"
        
        md += "## Key Research Questions\n\n"
        for i, question in enumerate(self.research_questions, 1):
            md += f"{i}. {question}\n"
        md += "\n"
        
        md += "## Keywords\n\n"
        md += ", ".join(self.keywords) + "\n\n"
        
        md += "## Focus Areas\n\n"
        for i, area in enumerate(self.focus_areas, 1):
            md += f"{i}. {area}\n"
        md += "\n"
        
        md += "## Search Strategies\n\n"
        for i, strategy in enumerate(self.search_strategies, 1):
            md += f"### Strategy {i}: {strategy.get('name', 'Unnamed')}\n\n"
            md += f"Query: `{strategy.get('query', '')}`\n\n"
            md += f"Focus: {strategy.get('focus', '')}\n\n"
            if 'filters' in strategy and strategy['filters']:
                md += "Filters:\n"
                for k, v in strategy['filters'].items():
                    md += f"- {k}: {v}\n"
            md += "\n"
        
        md += "## Preferences\n\n"
        md += f"- Methodology Interest: {self.methodology_interest:.1f}/1.0\n"
        md += f"- Recency Preference: {self.recency_preference:.1f}/1.0\n"
        
        return md

@dataclass
class ResearchProgress:
    """Track progress of the literature review process"""
    plan: ResearchPlan
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_papers_found: int = 0
    papers_after_filtering: int = 0
    papers_selected: int = 0
    queries_executed: List[Dict[str, Any]] = field(default_factory=list)
    search_iterations: int = 0
    current_stage: str = "planning"  # planning, searching, analyzing, synthesizing, completed
    status_messages: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_status(self, message: str, stage: Optional[str] = None) -> None:
        """Add a status message with timestamp"""
        self.status_messages.append({
            "time": datetime.now().isoformat(),
            "message": message,
            "stage": stage or self.current_stage
        })
        if stage:
            self.current_stage = stage
    
    def record_query(self, query: str, num_results: int, strategy_index: int) -> None:
        """Record an executed query and its results"""
        self.queries_executed.append({
            "time": datetime.now().isoformat(),
            "query": query,
            "num_results": num_results,
            "strategy_index": strategy_index
        })
    
    def to_markdown(self) -> str:
        """Convert progress to markdown format"""
        md = "# Literature Review Progress\n\n"
        
        # Basic stats
        md += "## Statistics\n\n"
        md += f"- **Current Stage:** {self.current_stage}\n"
        md += f"- **Start Time:** {self.start_time.strftime('%Y-%m-%d %H:%M')}\n"
        if self.end_time:
            md += f"- **End Time:** {self.end_time.strftime('%Y-%m-%d %H:%M')}\n"
            duration = self.end_time - self.start_time
            md += f"- **Duration:** {duration.total_seconds()/60:.1f} minutes\n"
        md += f"- **Search Iterations:** {self.search_iterations}\n"
        md += f"- **Total Papers Found:** {self.total_papers_found}\n"
        md += f"- **Papers After Filtering:** {self.papers_after_filtering}\n"
        md += f"- **Papers Selected:** {self.papers_selected}\n\n"
        
        # Queries executed
        md += "## Queries Executed\n\n"
        for i, query_data in enumerate(self.queries_executed, 1):
            strategy_idx = query_data.get('strategy_index', 0)
            strategy_name = "Default"
            if 0 <= strategy_idx < len(self.plan.search_strategies):
                strategy_name = self.plan.search_strategies[strategy_idx].get('name', f"Strategy {strategy_idx+1}")
                
            md += f"### Query {i} ({strategy_name})\n\n"
            md += f"```\n{query_data.get('query', '')}\n```\n\n"
            md += f"Results: {query_data.get('num_results', 0)} papers\n\n"
        
        # Status log
        md += "## Progress Log\n\n"
        for status in self.status_messages:
            time_str = datetime.fromisoformat(status['time']).strftime('%H:%M:%S')
            md += f"- **[{time_str} - {status['stage']}]** {status['message']}\n"
        
        return md

@dataclass
class KeyInsight:
    """Represents a key insight extracted from papers"""
    type: str  # methodology, finding, gap, trend, controversy
    description: str
    source_papers: List[str]  # Paper IDs
    confidence: float = 0.5
    keywords: List[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Convert to markdown format"""
        md = f"### {self.type.title()}\n\n"
        md += f"{self.description}\n\n"
        
        if self.keywords:
            md += f"**Keywords:** {', '.join(self.keywords)}\n\n"
            
        md += f"**Confidence:** {self.confidence:.1f}/1.0\n\n"
        
        if self.source_papers:
            md += f"**Sources:** {', '.join(self.source_papers)}\n\n"
            
        return md

@dataclass
class Paper:
    """Data structure for paper information"""
    id: str
    title: str
    abstract: Optional[str]
    authors: List[Dict[str, str]]
    venue: Optional[str]
    year: Optional[int]
    citation_count: Optional[int]
    url: Optional[str]
    pdf_url: Optional[str]
    references: List[str] = None
    relevance_score: float = 0.0
    confidence_score: float = 0.0  # Confidence in the relevance assessment
    relevance_aspects: Dict[str, float] = None  # Detailed breakdown of relevance
    keywords: List[str] = field(default_factory=list)  # Keywords extracted from the paper
    duplicate_of: Optional[str] = None  # ID of the paper this is a duplicate of
    cluster_id: Optional[int] = None  # Cluster/group this paper belongs to
    key_findings: List[str] = field(default_factory=list)  # Key findings extracted from the paper
    methodology_notes: List[str] = field(default_factory=list)  # Notes about the methodology
    
    def get_bibtex_key(self) -> str:
        """Generate a BibTeX key for this paper"""
        if not self.authors:
            first_author = "anonymous"
        else:
            first_author = self.authors[0].get("name", "").split()[-1].lower()
            # Remove special characters
            first_author = re.sub(r'[^a-z]', '', first_author)
            
        year = str(self.year) if self.year else "unknown"
        return f"{first_author}{year}"
    
    def to_bibtex(self) -> str:
        """Convert paper to BibTeX format"""
        key = self.get_bibtex_key()
        
        # Extract author names
        author_str = " and ".join([author.get("name", "") for author in self.authors]) if self.authors else "Unknown"
        
        # Determine entry type
        if not self.venue or "arxiv" in (self.venue or "").lower():
            entry_type = "article"
        elif "conference" in (self.venue or "").lower() or "proceedings" in (self.venue or "").lower():
            entry_type = "inproceedings"
        else:
            entry_type = "article"
            
        # Format BibTeX entry
        entry = f"@{entry_type}{{{key},\n"
        entry += f"  title = {{{self.title}}},\n"
        entry += f"  author = {{{author_str}}},\n"
        
        if self.year:
            entry += f"  year = {{{self.year}}},\n"
        
        if self.venue:
            if entry_type == "article":
                entry += f"  journal = {{{self.venue}}},\n"
            else:
                entry += f"  booktitle = {{{self.venue}}},\n"
                
        if self.url:
            entry += f"  url = {{{self.url}}},\n"
            
        entry += "}\n"
        return entry
    
    def get_content_for_similarity(self) -> str:
        """Get combined content for similarity calculation"""
        title = self.title or ""
        abstract = self.abstract or ""
        return f"{title} {abstract}"
    
    def is_likely_duplicate_of(self, other: 'Paper', threshold: float = 0.8) -> bool:
        """Check if this paper is likely a duplicate of another based on title similarity"""
        # Simple check for exact title match
        if self.title and other.title and self.title.lower() == other.title.lower():
            return True
            
        # Check for high similarity in titles
        if self.title and other.title:
            # Normalize titles
            title1 = re.sub(r'[^\w\s]', '', self.title.lower())
            title2 = re.sub(r'[^\w\s]', '', other.title.lower())
            
            # Calculate Jaccard similarity
            words1 = set(title1.split())
            words2 = set(title2.split())
            
            if not words1 or not words2:
                return False
                
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union > 0:
                similarity = intersection / union
                return similarity > threshold
                
        return False
    
    def to_markdown(self) -> str:
        """Convert paper details to markdown format"""
        md = f"## {self.title}\n\n"
        
        # Basic metadata
        authors = ", ".join([a.get("name", "") for a in self.authors[:3]]) if self.authors else "Unknown"
        if len(self.authors) > 3:
            authors += " et al."
        
        md += f"**Authors:** {authors}\n"
        md += f"**Year:** {self.year or 'Unknown'}\n"
        md += f"**Venue:** {self.venue or 'Unknown'}\n"
        if self.citation_count is not None:
            md += f"**Citations:** {self.citation_count}\n"
        if self.url:
            md += f"**URL:** [{self.url}]({self.url})\n"
        md += "\n"
        
        # Abstract
        if self.abstract:
            md += f"**Abstract:** {self.abstract}\n\n"
        
        # Relevance
        md += f"**Relevance:** {self.relevance_score:.2f} (Confidence: {self.confidence_score:.2f})\n"
        if self.relevance_aspects:
            aspects = ", ".join([f"{k}: {v:.2f}" for k, v in self.relevance_aspects.items()])
            md += f"**Relevance Aspects:** {aspects}\n"
        md += "\n"
        
        # Keywords
        if self.keywords:
            md += f"**Keywords:** {', '.join(self.keywords)}\n\n"
        
        # Key findings
        if self.key_findings:
            md += "**Key Findings:**\n\n"
            for finding in self.key_findings:
                md += f"- {finding}\n"
            md += "\n"
            
        # Methodology
        if self.methodology_notes:
            md += "**Methodology Notes:**\n\n"
            for note in self.methodology_notes:
                md += f"- {note}\n"
            md += "\n"
            
        return md 