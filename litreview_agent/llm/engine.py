"""
LLM integration for LitReviewAgent
"""

import re
import textwrap
from typing import List, Dict, Any, Optional, Tuple

from vllm import LLM, SamplingParams

from litreview_agent.data.models import Paper, ResearchPlan, KeyInsight

class LLMEngine:
    """Interface to Large Language Models for text generation and analysis"""
    
    def __init__(self, model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"):
        """
        Initialize the LLM engine with a specified model
        
        Args:
            model_name: Name of the VLLM-compatible model to use
        """
        self.model_name = model_name
        self.llm = LLM(model=model_name)
    
    def generate(self, prompt: str, sampling_params: Optional[SamplingParams] = None) -> str:
        """Generate text completion for a prompt"""
        if sampling_params is None:
            sampling_params = SamplingParams(temperature=0.2, max_tokens=1024)
            
        outputs = self.llm.generate([prompt], sampling_params)
        return outputs[0].outputs[0].text.strip()
    
    def generate_research_plan(self, title: str, abstract: str) -> ResearchPlan:
        """
        Generate a research plan based on the paper title and abstract
        
        Args:
            title: Title of the paper
            abstract: Abstract of the paper
            
        Returns:
            ResearchPlan object with research questions, focus areas, etc.
        """
        prompt = f"""You are a research assistant helping to create a literature review. You need to generate a research plan based on a paper title and abstract.

USER'S PAPER:
Title: {title}
Abstract: {abstract}

Generate a comprehensive research plan that includes:
1. 3-5 specific research questions derived from the user's paper
2. 5-8 relevant keywords that will be useful for searching
3. 3-4 specific focus areas for the literature review
4. 3-4 search strategies, each with a specific focus and query
5. A suitable recency preference (0.0-1.0, where 0.0 means prefer seminal works regardless of age, 1.0 means highly prefer recent papers)
6. A methodology interest level (0.0-1.0, where 0.0 means focus only on findings, 1.0 means deeply interested in methodological details)

Format your response as JSON with the following structure:
{{
  "research_questions": ["question1", "question2", ...],
  "keywords": ["keyword1", "keyword2", ...],
  "focus_areas": ["area1", "area2", ...],
  "search_strategies": [
    {{
      "name": "Strategy name",
      "focus": "What this strategy focuses on",
      "query": "The search query to use",
      "filters": {{
        "optional filter": "value"
      }}
    }},
    ...
  ],
  "recency_preference": 0.5,
  "methodology_interest": 0.5
}}

Return ONLY valid JSON without markdown formatting, explanation, or any other text."""

        response = self.generate(prompt)
        
        try:
            import json
            data = json.loads(response)
            
            # Create the research plan object
            plan = ResearchPlan(
                title=title,
                abstract=abstract,
                research_questions=data.get("research_questions", []),
                keywords=data.get("keywords", []),
                focus_areas=data.get("focus_areas", []),
                search_strategies=data.get("search_strategies", []),
                recency_preference=data.get("recency_preference", 0.5),
                methodology_interest=data.get("methodology_interest", 0.5)
            )
            return plan
        except Exception as e:
            print(f"Error parsing research plan: {e}")
            print(f"Response was: {response}")
            
            # Return a basic plan in case of error
            return ResearchPlan(
                title=title,
                abstract=abstract,
                research_questions=["What are the key findings in this research area?"],
                keywords=self.extract_keywords(title, abstract),
                focus_areas=["General overview of the field"],
                search_strategies=[{
                    "name": "Basic search",
                    "focus": "General overview",
                    "query": title
                }]
            )
    
    def extract_keywords(self, title: str, abstract: str, num_keywords: int = 10) -> List[str]:
        """
        Extract keywords from title and abstract
        
        Args:
            title: Paper title
            abstract: Paper abstract
            num_keywords: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        prompt = f"""Extract the most relevant keywords from the following academic paper title and abstract.
Focus on specific technical terms, methods, concepts, and domain-specific vocabulary.

Title: {title}
Abstract: {abstract}

Provide exactly {num_keywords} keywords as a comma-separated list, with no numbering or additional text.
Each keyword should be 1-3 words only."""

        response = self.generate(prompt)
        
        # Clean up and split the response
        keywords = [k.strip() for k in response.split(',')]
        return keywords[:num_keywords]  # Ensure we don't exceed the requested number
        
    def refine_search_query(self, 
                         original_query: str, 
                         plan: ResearchPlan, 
                         previous_results: List[Paper], 
                         focus_area: str,
                         iteration: int) -> str:
        """
        Refine a search query based on previous results and focus area
        
        Args:
            original_query: The original search query
            plan: The research plan
            previous_results: Papers found in previous iterations
            focus_area: The focus area for this search strategy
            iteration: Which iteration of search this is
            
        Returns:
            Refined search query
        """
        # Prepare summary of previous results
        prev_papers = ""
        for i, paper in enumerate(previous_results[:5], 1):  # Limit to top 5 for query context
            prev_papers += f"{i}. {paper.title}"
            if paper.authors and len(paper.authors) > 0:
                prev_papers += f" (by {paper.authors[0].get('name', '')})"
            prev_papers += "\n"
            
        if len(previous_results) > 5:
            prev_papers += f"...and {len(previous_results) - 5} more papers\n"
            
        # Prepare the prompt
        prompt = f"""You are an expert research assistant helping with a literature review search.

RESEARCH FOCUS:
Title: {plan.title}
Abstract: {plan.abstract}

FOCUS AREA FOR THIS SEARCH:
{focus_area}

PREVIOUS SEARCH QUERY:
{original_query}

PAPERS ALREADY FOUND ({len(previous_results)} total):
{prev_papers}

ITERATION: {iteration} (higher iterations should be more exploratory/divergent from initial query)

TASK:
Create an improved search query that will help find additional relevant papers in the focus area.
Your new query should:
1. Be more specific or use different terms based on what's been found so far
2. Address gaps in the current results
3. Use highly specific technical terms where appropriate
4. Be formulated for academic search engines (e.g., use quotes, operators like AND/OR if helpful)
5. Not exceed 200 characters

Return just the search query text with no additional explanation, formatting, or quotes."""

        return self.generate(prompt)
        
    def generate_search_queries(self, title: str, abstract: str, keywords: List[str], num_queries: int = 3) -> List[str]:
        """
        Generate search queries based on paper details
        
        Args:
            title: Paper title
            abstract: Paper abstract
            keywords: Extracted keywords
            num_queries: Number of queries to generate
            
        Returns:
            List of search queries
        """
        prompt = f"""Generate {num_queries} effective academic search queries based on this paper information:

Title: {title}
Abstract: {abstract}
Keywords: {', '.join(keywords)}

Each query should:
1. Be specific and targeted for academic search engines
2. Use different approaches (e.g., methodology-focused, application-focused, concept-focused)
3. Include quotes around phrases where appropriate
4. Use operators (AND, OR) if helpful
5. Not exceed 150 characters

Format: Return ONLY the queries, one per line, with no numbering, explanation, or additional text."""

        response = self.generate(prompt)
        
        # Split the response into individual queries
        queries = [q.strip() for q in response.split('\n') if q.strip()]
        return queries[:num_queries]  # Ensure we don't exceed the requested number
        
    def extract_key_insights(self, papers: List[Paper], research_questions: List[str]) -> List[KeyInsight]:
        """
        Extract key insights across multiple papers
        
        Args:
            papers: List of papers to analyze
            research_questions: Research questions to focus on
            
        Returns:
            List of KeyInsight objects
        """
        # If we have no papers, return empty list
        if not papers:
            return []
            
        # Prepare paper summaries
        paper_summaries = ""
        for i, paper in enumerate(papers, 1):
            summary = f"{i}. \"{paper.title}\""
            if paper.authors and len(paper.authors) > 0:
                summary += f" by {paper.authors[0].get('name', '')}"
                if len(paper.authors) > 1:
                    summary += " et al."
            if paper.year:
                summary += f" ({paper.year})"
            summary += "\n"
            
            if paper.abstract:
                # Truncate long abstracts
                abstract = paper.abstract
                if len(abstract) > 300:
                    abstract = abstract[:300] + "..."
                summary += f"   Abstract: {abstract}\n"
                
            if paper.key_findings:
                summary += "   Key findings:\n"
                for finding in paper.key_findings[:3]:  # Limit to top 3 findings
                    summary += f"   - {finding}\n"
                    
            paper_summaries += summary + "\n"
        
        # Prepare research questions
        questions = "\n".join([f"- {q}" for q in research_questions])
        
        prompt = f"""Analyze the following papers and identify key insights relevant to the research questions.

RESEARCH QUESTIONS:
{questions}

PAPERS:
{paper_summaries}

Identify 4-6 key insights from these papers. Each insight should be one of these types:
- "methodology": Novel or important methodological approaches
- "finding": Key research finding or conclusion
- "gap": Research gap or unanswered question
- "trend": Trend or direction in the field
- "controversy": Area of debate or disagreement

For each insight:
1. Identify the type from the list above
2. Write a clear, specific description (2-3 sentences)
3. List the paper numbers (sources) that support this insight
4. Assign a confidence score (0.1-1.0)
5. List 3-5 relevant keywords

Format your response as JSON:
[
  {{
    "type": "methodology|finding|gap|trend|controversy",
    "description": "Detailed description of the insight",
    "source_papers": ["1", "3", "5"],
    "confidence": 0.8,
    "keywords": ["keyword1", "keyword2", "keyword3"]
  }},
  ...
]

Return ONLY the JSON with no additional text or explanation."""

        response = self.generate(prompt)
        
        try:
            import json
            insights_data = json.loads(response)
            
            insights = []
            for item in insights_data:
                # Convert source paper references from string numbers to actual paper IDs
                sources = []
                for src in item.get("source_papers", []):
                    try:
                        # Convert string "1" to integer 0 (index)
                        idx = int(src) - 1
                        if 0 <= idx < len(papers):
                            sources.append(papers[idx].id)
                    except:
                        # If conversion fails, use the source as is
                        sources.append(src)
                
                insight = KeyInsight(
                    type=item.get("type", "finding"),
                    description=item.get("description", ""),
                    source_papers=sources,
                    confidence=item.get("confidence", 0.5),
                    keywords=item.get("keywords", [])
                )
                insights.append(insight)
                
            return insights
        except Exception as e:
            print(f"Error parsing insights: {e}")
            return []
        
    def extract_paper_findings(self, paper: Paper) -> List[str]:
        """
        Extract key findings from a paper
        
        Args:
            paper: Paper to analyze
            
        Returns:
            List of key findings as strings
        """
        if not paper.abstract:
            return []
            
        prompt = f"""Extract the key findings and contributions from this academic paper.

Title: {paper.title}

Abstract: {paper.abstract}

Return 3-5 specific, concise bullet points that capture the main findings, contributions, or conclusions of this paper. Each should be 1-2 sentences only.

Format your response as a simple list with one finding per line. Do not include numbering, bullet points, or any other formatting."""

        response = self.generate(prompt)
        
        # Split the response into individual findings
        findings = [line.strip() for line in response.split('\n') if line.strip()]
        return findings
        
    def assess_relevance(self, paper: Paper, user_title: str, user_abstract: str) -> Tuple[float, float, Dict[str, float]]:
        """
        Assess the relevance of a paper to the user's research
        
        Args:
            paper: Paper to assess
            user_title: User's paper title
            user_abstract: User's paper abstract
            
        Returns:
            Tuple of (relevance_score, confidence_score, relevance_aspects)
        """
        if not paper.abstract:
            # If we don't have an abstract, make a guess based on title similarity
            from difflib import SequenceMatcher
            title_similarity = SequenceMatcher(None, paper.title.lower(), user_title.lower()).ratio()
            confidence = 0.3  # Low confidence without abstract
            
            # Basic heuristic based on title similarity
            relevance = min(1.0, title_similarity * 1.5)
            
            return relevance, confidence, {"title_similarity": title_similarity}
        
        # For papers with abstracts, use LLM to assess relevance
        prompt = f"""Assess the relevance of the CANDIDATE PAPER to the USER'S RESEARCH.

USER'S RESEARCH:
Title: {user_title}
Abstract: {user_abstract}

CANDIDATE PAPER:
Title: {paper.title}
Abstract: {paper.abstract}

Evaluate the relevance of the candidate paper to the user's research needs across these dimensions:
1. Topical relevance: How closely the subject matter matches
2. Methodological relevance: Similarity in approaches or techniques
3. Contribution relevance: How the findings might inform the user's work
4. Recency/currency: Whether it represents current thinking (if applicable)

Score each dimension from 0.0 to 1.0, where:
- 0.0 = Not relevant at all
- 0.3 = Slightly relevant
- 0.5 = Moderately relevant
- 0.7 = Very relevant
- 1.0 = Extremely relevant

Also provide an overall relevance score and your confidence in the assessment.

Return your evaluation as JSON:
{{
  "overall_relevance": 0.0-1.0,
  "confidence": 0.0-1.0,
  "aspects": {{
    "topical_relevance": 0.0-1.0,
    "methodological_relevance": 0.0-1.0,
    "contribution_relevance": 0.0-1.0,
    "recency_relevance": 0.0-1.0
  }}
}}

Return ONLY the JSON with no additional text."""

        response = self.generate(prompt)
        
        try:
            import json
            data = json.loads(response)
            
            overall_relevance = data.get("overall_relevance", 0.5)
            confidence = data.get("confidence", 0.5)
            aspects = data.get("aspects", {
                "topical_relevance": 0.5,
                "methodological_relevance": 0.5,
                "contribution_relevance": 0.5,
                "recency_relevance": 0.5
            })
            
            return overall_relevance, confidence, aspects
        except Exception as e:
            print(f"Error parsing relevance assessment: {e}")
            # Fallback to a basic assessment
            return 0.5, 0.3, {
                "topical_relevance": 0.5,
                "methodological_relevance": 0.5,
                "contribution_relevance": 0.5,
                "recency_relevance": 0.5
            }
        
    def cluster_papers(self, papers: List[Paper], num_clusters: int = 3) -> Dict[int, List[Paper]]:
        """
        Cluster papers by topic similarity
        
        Args:
            papers: List of papers to cluster
            num_clusters: Target number of clusters
            
        Returns:
            Dictionary mapping cluster IDs to lists of papers
        """
        if len(papers) < num_clusters:
            # If we have fewer papers than clusters, put each in its own cluster
            return {i: [paper] for i, paper in enumerate(papers)}
            
        # Prepare paper data for the prompt
        paper_data = ""
        for i, paper in enumerate(papers, 1):
            paper_data += f"{i}. \"{paper.title}\"\n"
            if paper.abstract:
                abstract = paper.abstract
                if len(abstract) > 200:
                    abstract = abstract[:200] + "..."
                paper_data += f"   Abstract: {abstract}\n"
            if paper.keywords:
                paper_data += f"   Keywords: {', '.join(paper.keywords[:5])}\n"
            paper_data += "\n"
            
        prompt = f"""Cluster the following papers into {num_clusters} groups based on topic similarity.

PAPERS:
{paper_data}

Group these papers into exactly {num_clusters} clusters based on thematic similarity, methodology, or research focus.

For each cluster:
1. Assign a cluster number (0 to {num_clusters-1})
2. Create a short descriptive name (3-5 words)
3. List the paper numbers that belong to this cluster

Each paper must be assigned to exactly one cluster. Every paper must be assigned.

Format your response as JSON:
{{
  "0": {{
    "name": "Short cluster name",
    "papers": [1, 3, 5]
  }},
  "1": {{
    "name": "Another cluster name",
    "papers": [2, 4, 8]
  }},
  ...
}}

Return ONLY the JSON with no additional text."""

        response = self.generate(prompt)
        
        try:
            import json
            clusters_data = json.loads(response)
            
            # Convert the data structure to map cluster IDs to lists of papers
            clusters = {}
            for cluster_id, cluster_info in clusters_data.items():
                cluster_papers = []
                for paper_idx in cluster_info.get("papers", []):
                    try:
                        # Convert from 1-indexed to 0-indexed
                        idx = int(paper_idx) - 1
                        if 0 <= idx < len(papers):
                            # Use the actual paper object
                            cluster_papers.append(papers[idx])
                    except:
                        # Skip if conversion fails
                        pass
                        
                # Convert cluster_id to integer
                try:
                    cid = int(cluster_id)
                except:
                    cid = len(clusters)
                    
                clusters[cid] = cluster_papers
                
            # Ensure all papers are assigned to a cluster
            assigned_papers = set()
            for cluster_papers in clusters.values():
                for paper in cluster_papers:
                    assigned_papers.add(paper.id)
                    
            # Assign unassigned papers to the most appropriate cluster
            for paper in papers:
                if paper.id not in assigned_papers:
                    # Assign to the first cluster as fallback
                    first_cluster_id = next(iter(clusters.keys())) if clusters else 0
                    if first_cluster_id in clusters:
                        clusters[first_cluster_id].append(paper)
                    else:
                        clusters[first_cluster_id] = [paper]
                        
            return clusters
        except Exception as e:
            print(f"Error parsing clusters: {e}")
            # Fallback: put all papers in one cluster
            return {0: papers}
        
    def generate_review_section(self, 
                             user_title: str, 
                             user_abstract: str, 
                             papers: List[Paper],
                             insights: List[KeyInsight] = None) -> str:
        """
        Generate a literature review section
        
        Args:
            user_title: User's paper title
            user_abstract: User's paper abstract
            papers: List of papers to include in the review
            insights: Optional list of key insights
            
        Returns:
            Formatted literature review text in markdown format
        """
        # Prepare papers representation
        papers_data = ""
        for i, paper in enumerate(papers, 1):
            paper_data = f"{i}. \"{paper.title}\""
            if paper.authors:
                if len(paper.authors) == 1:
                    paper_data += f" by {paper.authors[0].get('name', '')}"
                elif len(paper.authors) == 2:
                    paper_data += f" by {paper.authors[0].get('name', '')} and {paper.authors[1].get('name', '')}"
                else:
                    paper_data += f" by {paper.authors[0].get('name', '')} et al."
            
            if paper.year:
                paper_data += f" ({paper.year})"
            
            paper_data += f" [relevance: {paper.relevance_score:.2f}]"
            papers_data += paper_data + "\n"
            
            if paper.abstract:
                abstract = paper.abstract
                if len(abstract) > 150:  # Truncate long abstracts
                    abstract = abstract[:150] + "..."
                papers_data += f"   Abstract: {abstract}\n"
                
            if paper.key_findings:
                papers_data += "   Key findings:\n"
                for finding in paper.key_findings[:3]:  # Limit to top 3 findings
                    papers_data += f"   - {finding}\n"
                    
            papers_data += "\n"
            
        # Prepare insights data if available
        insights_data = ""
        if insights:
            insights_data = "KEY INSIGHTS:\n"
            for i, insight in enumerate(insights, 1):
                insights_data += f"{i}. [{insight.type.upper()}] {insight.description}\n"
                if insight.keywords:
                    insights_data += f"   Keywords: {', '.join(insight.keywords)}\n"
                if insight.source_papers:
                    insights_data += f"   Sources: Papers {', '.join([str(i+1) for i, p in enumerate(papers) if p.id in insight.source_papers])}\n"
                insights_data += "\n"
        
        # Create the prompt
        prompt = f"""Write a comprehensive literature review section based on the following research papers.

CONTEXT:
The literature review is for a paper titled: "{user_title}"
Abstract: {user_abstract}

PAPERS TO INCLUDE:
{papers_data}

{insights_data}

INSTRUCTIONS:
1. Structure the review thematically, grouping related papers and findings
2. Critically analyze the literature, highlighting agreements, contradictions, and research gaps
3. Use LaTeX citation format \\cite{{bibtexKey}} when mentioning papers (Example: \\cite{{smith2020}})
4. For each paper's bibtex key, use the format: [first author's last name][year] (e.g., smith2020)
5. The review should be well-structured with clear paragraphs and section divisions
6. Maintain academic tone and style throughout
7. Format the result as Markdown with appropriate headings

Return a complete, polished literature review section that could be included in an academic paper."""

        # Generate with a larger response allowance for the full review
        sampling_params = SamplingParams(temperature=0.2, max_tokens=4096)
        response = self.generate(prompt, sampling_params)
        
        # Post-process to fix citation keys if needed
        for paper in papers:
            bibtex_key = paper.get_bibtex_key()
            
            # Find author names to handle variations in citation formatting
            author_last_name = ""
            if paper.authors and paper.authors[0].get("name"):
                author_parts = paper.authors[0].get("name", "").split()
                if author_parts:
                    author_last_name = author_parts[-1].lower()
            
            # Handle missing citations - replace author mentions with citations
            if author_last_name and paper.year:
                # Check for mentions of author name + year without citation
                pattern = f"({author_last_name}\\s*et al\\.?|{author_last_name})\\s*\\({paper.year}\\)"
                replacement = f"\\\\cite{{{bibtex_key}}}"
                response = re.sub(pattern, replacement, response, flags=re.IGNORECASE)
                
        return response 