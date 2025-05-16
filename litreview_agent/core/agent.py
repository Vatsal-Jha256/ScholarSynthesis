"""
Core agent functionality for LitReviewAgent
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from litreview_agent.data.models import Paper, ResearchPlan, ResearchProgress, KeyInsight
from litreview_agent.search.semantic_scholar import SemanticScholarSearch
from litreview_agent.llm.engine import LLMEngine
from litreview_agent.analysis.analyzer import PaperAnalyzer

class LitReviewAgent:
    """Main agent class for literature review automation"""
    
    def __init__(self, 
                 llm_model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct", 
                 semantic_scholar_api_key: Optional[str] = None,
                 relevance_threshold: float = 0.5,
                 max_search_iterations: int = 3):
        """Initialize LitReviewAgent with configurable components"""
        self.llm_engine = LLMEngine(model_name=llm_model_name)
        self.search_engine = SemanticScholarSearch(api_key=semantic_scholar_api_key)
        self.analyzer = PaperAnalyzer(llm_engine=self.llm_engine)
        self.relevance_threshold = relevance_threshold
        self.max_search_iterations = max_search_iterations
    
    def run_literature_review(self, 
                              title: str, 
                              abstract: str, 
                              num_papers: int = 15,
                              expand_references: bool = True,
                              min_relevance_score: Optional[float] = None,
                              year_range: Optional[Tuple[int, int]] = None,
                              remove_duplicates: bool = True,
                              output_dir: str = "./output") -> Tuple[str, str, List[Paper], Dict[str, Any]]:
        """
        Run a complete literature review process
        
        Args:
            title: Title of the user's paper
            abstract: Abstract of the user's paper
            num_papers: Target number of papers to include
            expand_references: Whether to expand search by following references
            min_relevance_score: Minimum relevance score for papers to include
            year_range: Optional tuple of (start_year, end_year) to filter papers
            remove_duplicates: Whether to remove duplicate papers
            output_dir: Directory to save output files
            
        Returns:
            Tuple of (review_text, bibtex_citations, papers, metadata)
        """
        min_relevance = min_relevance_score if min_relevance_score is not None else self.relevance_threshold
        
        # Ensure output directory exists
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        # Step 1: Generate research plan
        print(f"🧠 Generating research plan for: {title}")
        research_plan = self.llm_engine.generate_research_plan(title, abstract)
        
        # Initialize progress tracking
        progress = ResearchProgress(plan=research_plan)
        progress.add_status(f"Research plan generated with {len(research_plan.research_questions)} research questions", "planning")
        
        # For diagnostics
        metadata = {
            "title": title,
            "abstract": abstract,
            "research_plan": research_plan.to_dict(),
            "timestamp": datetime.now().isoformat(),
            "settings": {
                "num_papers": num_papers,
                "expand_references": expand_references,
                "min_relevance_score": min_relevance,
                "year_range": year_range,
                "remove_duplicates": remove_duplicates
            }
        }
        
        # Step 2: Perform adaptive search
        papers = []
        all_papers = []  # Keep track of all papers for diagnostics
        
        progress.add_status("Starting literature search", "searching")
        for iteration in range(self.max_search_iterations):
            iteration_papers = []
            
            # Execute each search strategy
            for i, strategy in enumerate(research_plan.search_strategies):
                strategy_name = strategy.get('name', f"Strategy {i+1}")
                focus_area = strategy.get('focus', 'general')
                base_query = strategy.get('query', title)
                
                # Refine query based on previous results and focus area
                if iteration == 0:
                    query = base_query
                else:
                    query = self.llm_engine.refine_search_query(
                        base_query, 
                        research_plan, 
                        papers, 
                        focus_area, 
                        iteration
                    )
                
                # Execute search
                progress.add_status(f"Executing search query (iteration {iteration+1}, {strategy_name}): {query}")
                query_papers = self.search_engine.search_papers(
                    query=query, 
                    limit=15, 
                    year_range=year_range
                )
                
                # Record the query in progress
                progress.record_query(query, len(query_papers), i)
                progress.total_papers_found += len(query_papers)
                
                # Add results to this iteration
                iteration_papers.extend(query_papers)
            
            # Assess relevance
            for paper in iteration_papers:
                relevance_score, confidence, aspects = self.llm_engine.assess_relevance(paper, title, abstract)
                paper.relevance_score = relevance_score
                paper.confidence_score = confidence
                paper.relevance_aspects = aspects
            
            # Filter by relevance
            filtered_papers = [paper for paper in iteration_papers if paper.relevance_score >= min_relevance]
            progress.papers_after_filtering += len(filtered_papers)
            
            # Remove duplicates if enabled
            if remove_duplicates:
                filtered_papers = self.analyzer.detect_duplicates(filtered_papers)
                
                # Also check against existing papers
                if papers:
                    for new_paper in filtered_papers[:]:
                        for existing_paper in papers:
                            if new_paper.is_likely_duplicate_of(existing_paper):
                                new_paper.duplicate_of = existing_paper.id
                                filtered_papers.remove(new_paper)
                                break
            
            # Add unique papers to our collection
            papers.extend([p for p in filtered_papers if not p.duplicate_of])
            all_papers.extend(iteration_papers)  # For diagnostics
            
            # Update progress
            progress.search_iterations += 1
            progress.papers_selected = len(papers)
            progress.add_status(f"Iteration {iteration+1} complete: found {len(iteration_papers)} papers, {len(filtered_papers)} relevant")
            
            # Check if we have enough papers
            if len(papers) >= num_papers:
                progress.add_status(f"Found {len(papers)} relevant papers, which meets our target of {num_papers}")
                break
                
            # Log next iteration
            if iteration < self.max_search_iterations - 1:
                progress.add_status(f"Need more papers (have {len(papers)}, want {num_papers}). Starting iteration {iteration+2}...")
        
        # Step 3: Expand search by following references if enabled and needed
        if expand_references and len(papers) < num_papers:
            progress.add_status("Expanding search by following references", "searching")
            
            # Sort papers by relevance to prioritize most relevant first
            papers_by_relevance = sorted(papers, key=lambda p: p.relevance_score, reverse=True)
            
            for paper in papers_by_relevance[:5]:  # Only check top 5 papers
                # Fetch references
                references = self.search_engine.get_paper_references(paper.id, limit=10)
                progress.total_papers_found += len(references)
                
                # Assess relevance
                for ref_paper in references:
                    relevance_score, confidence, aspects = self.llm_engine.assess_relevance(ref_paper, title, abstract)
                    ref_paper.relevance_score = relevance_score
                    ref_paper.confidence_score = confidence
                    ref_paper.relevance_aspects = aspects
                
                # Filter by relevance
                filtered_refs = [ref for ref in references if ref.relevance_score >= min_relevance]
                progress.papers_after_filtering += len(filtered_refs)
                
                # Check for duplicates
                if remove_duplicates:
                    filtered_refs = self.analyzer.detect_duplicates(filtered_refs)
                    
                    # Also check against existing papers
                    for new_paper in filtered_refs[:]:
                        for existing_paper in papers:
                            if new_paper.is_likely_duplicate_of(existing_paper):
                                new_paper.duplicate_of = existing_paper.id
                                filtered_refs.remove(new_paper)
                                break
                
                # Add to collection
                papers.extend([p for p in filtered_refs if not p.duplicate_of])
                all_papers.extend(references)  # For diagnostics
                
                progress.papers_selected = len(papers)
                progress.add_status(f"Added {len([p for p in filtered_refs if not p.duplicate_of])} relevant references from paper: {paper.title}")
                
                # Check if we have enough papers
                if len(papers) >= num_papers:
                    progress.add_status(f"Found {len(papers)} relevant papers, which meets our target of {num_papers}")
                    break
        
        # Step 4: Extract keywords and findings
        if papers:
            progress.add_status("Analyzing papers", "analyzing")
            
            # Extract keywords
            papers = self.analyzer.extract_paper_keywords(papers)
            
            # Extract findings
            papers = self.analyzer.extract_findings(papers)
            
            # Cluster papers
            if len(papers) >= 3:
                progress.add_status("Clustering papers by topic")
                clusters = self.llm_engine.cluster_papers(papers)
                
                # Assign cluster IDs to papers
                for cluster_id, cluster_papers in clusters.items():
                    for paper in cluster_papers:
                        # Find the actual paper object in our collection
                        for p in papers:
                            if p.id == paper.id:
                                p.cluster_id = cluster_id
                                break
        
        # Step 5: Extract key insights across papers
        progress.add_status("Extracting key insights across papers", "synthesizing")
        insights = self.llm_engine.extract_key_insights(papers, research_plan.research_questions)
        
        # Step 6: Generate the review section
        progress.add_status("Generating literature review", "synthesizing")
        review_text = self.llm_engine.generate_review_section(title, abstract, papers, insights)
        
        # Generate BibTeX
        bibtex_citations = "\n".join([paper.to_bibtex() for paper in papers if paper.relevance_score >= min_relevance])
        
        # Save outputs
        if output_dir:
            # Save review text
            with open(os.path.join(output_dir, "literature_review.md"), "w", encoding="utf-8") as f:
                f.write(review_text)
            
            # Save BibTeX
            with open(os.path.join(output_dir, "references.bib"), "w", encoding="utf-8") as f:
                f.write(bibtex_citations)
            
            # Save research plan
            with open(os.path.join(output_dir, "research_plan.md"), "w", encoding="utf-8") as f:
                f.write(research_plan.to_markdown())
                
            # Save progress report
            with open(os.path.join(output_dir, "progress_report.md"), "w", encoding="utf-8") as f:
                f.write(progress.to_markdown())
            
            # Save insights
            with open(os.path.join(output_dir, "key_insights.md"), "w", encoding="utf-8") as f:
                f.write("# Key Insights\n\n")
                for insight in insights:
                    f.write(insight.to_markdown())
            
            # Save metadata for diagnostics
            metadata.update({
                "num_search_iterations": progress.search_iterations,
                "total_papers_found": progress.total_papers_found,
                "papers_after_filtering": progress.papers_after_filtering,
                "papers_selected": progress.papers_selected,
                "insights_extracted": len(insights)
            })
            
            with open(os.path.join(output_dir, "metadata.json"), "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, default=str)
                
        # Finalize progress
        progress.current_stage = "completed"
        progress.end_time = datetime.now()
        progress.add_status(f"Literature review completed with {len(papers)} papers", "completed")
        
        # Return the results along with metadata in the expected format
        research_data = {
            "research_plan": research_plan,
            "search_iterations": progress.search_iterations,
            "total_papers_found": progress.total_papers_found,
            "papers_after_filtering": progress.papers_after_filtering,
            "papers_selected": progress.papers_selected,
            "insights": insights,
        }
        
        return review_text, bibtex_citations, papers, research_data 