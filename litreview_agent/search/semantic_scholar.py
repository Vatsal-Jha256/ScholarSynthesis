"""
Search functionality using the Semantic Scholar API
"""

import requests
from typing import List, Dict, Any, Optional, Tuple

from litreview_agent.data.models import Paper

class SemanticScholarSearch:
    """Search interface using Semantic Scholar API"""
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize search with optional API key"""
        self.api_key = api_key
        self.headers = {"x-api-key": api_key} if api_key else {}
    
    def search_papers(self, query: str, limit: int = 10, year_range: Optional[Tuple[int, int]] = None) -> List[Paper]:
        """
        Search for papers using Semantic Scholar API
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            year_range: Optional tuple of (start_year, end_year) to filter papers
            
        Returns:
            List of Paper objects
        """
        endpoint = f"{self.BASE_URL}/paper/search"
        
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,abstract,authors,venue,year,citationCount,url,externalIds",
        }
        
        if year_range:
            min_year, max_year = year_range
            params["year"] = f"{min_year}-{max_year}"
        
        response = requests.get(endpoint, params=params, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        
        papers = []
        for item in data.get("data", []):
            # Extract paper ID
            paper_id = item.get("paperId", "")
            if not paper_id and "externalIds" in item:
                # Fallback to alternate IDs
                external_ids = item.get("externalIds", {})
                paper_id = external_ids.get("DOI", "") or external_ids.get("ArXiv", "") or external_ids.get("MAG", "")
            
            if not paper_id:
                # Skip papers without any ID
                continue
                
            # Extract authors
            authors = []
            for author in item.get("authors", []):
                authors.append({
                    "name": author.get("name", ""),
                    "id": author.get("authorId", "")
                })
            
            # Create Paper object
            paper = Paper(
                id=paper_id,
                title=item.get("title", ""),
                abstract=item.get("abstract"),
                authors=authors,
                venue=item.get("venue"),
                year=item.get("year"),
                citation_count=item.get("citationCount"),
                url=item.get("url"),
                pdf_url=None,  # Not provided in search results
                references=[]  # Will be populated later if needed
            )
            
            papers.append(paper)
            
        return papers
    
    def get_paper_references(self, paper_id: str, limit: int = 10) -> List[Paper]:
        """
        Get references for a specific paper
        
        Args:
            paper_id: ID of the paper to get references for
            limit: Maximum number of references to return
            
        Returns:
            List of Paper objects representing the references
        """
        endpoint = f"{self.BASE_URL}/paper/{paper_id}/references"
        
        params = {
            "limit": limit,
            "fields": "title,abstract,authors,venue,year,citationCount,url,externalIds",
        }
        
        response = requests.get(endpoint, params=params, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        
        papers = []
        for item in data.get("data", []):
            cited_paper = item.get("citedPaper", {})
            
            # Extract paper ID
            paper_id = cited_paper.get("paperId", "")
            if not paper_id and "externalIds" in cited_paper:
                # Fallback to alternate IDs
                external_ids = cited_paper.get("externalIds", {})
                paper_id = external_ids.get("DOI", "") or external_ids.get("ArXiv", "") or external_ids.get("MAG", "")
            
            if not paper_id:
                # Skip papers without any ID
                continue
                
            # Extract authors
            authors = []
            for author in cited_paper.get("authors", []):
                authors.append({
                    "name": author.get("name", ""),
                    "id": author.get("authorId", "")
                })
            
            # Create Paper object
            paper = Paper(
                id=paper_id,
                title=cited_paper.get("title", ""),
                abstract=cited_paper.get("abstract"),
                authors=authors,
                venue=cited_paper.get("venue"),
                year=cited_paper.get("year"),
                citation_count=cited_paper.get("citationCount"),
                url=cited_paper.get("url"),
                pdf_url=None,  # Not provided in reference results
                references=[]  # We don't need to go deeper
            )
            
            papers.append(paper)
            
        return papers 