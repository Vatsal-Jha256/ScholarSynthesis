"""
Command-line interface for LitReviewAgent
"""

import os
import argparse
import json
from typing import Optional, Tuple

from litreview_agent import LitReviewAgent

def main():
    """Entry point for the LitReviewAgent CLI"""
    parser = argparse.ArgumentParser(description="LitReviewAgent: AI-powered literature review generator")
    parser.add_argument("--title", type=str, required=True, help="Title of your paper")
    parser.add_argument("--abstract", type=str, required=True, help="Abstract of your paper")
    parser.add_argument("--num_papers", type=int, default=15, help="Number of papers to include in review")
    parser.add_argument("--output_dir", type=str, default="./output", help="Directory to save output files")
    parser.add_argument("--model", type=str, default="meta-llama/Meta-Llama-3-8B-Instruct", 
                       help="VLLM model to use")
    parser.add_argument("--api_key", type=str, default=None, 
                       help="Semantic Scholar API key (optional)")
    parser.add_argument("--no_expand_refs", action="store_true", 
                       help="Disable reference expansion")
    parser.add_argument("--relevance_threshold", type=float, default=0.5,
                       help="Minimum relevance score for including papers (0.0-1.0)")
    parser.add_argument("--start_year", type=int, default=None,
                       help="Start year for filtering papers")
    parser.add_argument("--end_year", type=int, default=None,
                       help="End year for filtering papers")
    parser.add_argument("--keep_duplicates", action="store_true",
                       help="Don't remove duplicate papers")
    parser.add_argument("--max_iterations", type=int, default=3,
                       help="Maximum number of search iterations per strategy")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Setup year range if provided
    year_range = None
    if args.start_year is not None and args.end_year is not None:
        year_range = (args.start_year, args.end_year)
    
    # Initialize agent
    agent = LitReviewAgent(
        llm_model_name=args.model, 
        semantic_scholar_api_key=args.api_key,
        relevance_threshold=args.relevance_threshold,
        max_search_iterations=args.max_iterations
    )
    
    # Run literature review
    review_text, bibtex_entries, selected_papers, research_data = agent.run_literature_review(
        title=args.title,
        abstract=args.abstract,
        num_papers=args.num_papers,
        expand_references=not args.no_expand_refs,
        year_range=year_range,
        remove_duplicates=not args.keep_duplicates,
        output_dir=args.output_dir
    )
    
    # Save outputs
    with open(os.path.join(args.output_dir, "review_section.tex"), "w", encoding="utf-8") as f:
        f.write("\\section{Related Work}\n")
        f.write(review_text)
    
    with open(os.path.join(args.output_dir, "references.bib"), "w", encoding="utf-8") as f:
        f.write(bibtex_entries)
    
    # Save paper details including clusters
    with open(os.path.join(args.output_dir, "paper_details.md"), "w", encoding="utf-8") as f:
        f.write("# Retrieved Papers Details\n\n")
        
        # Group papers by cluster
        clusters = {}
        for paper in selected_papers:
            cluster_id = paper.cluster_id if paper.cluster_id is not None else 0
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(paper)
            
        # Write details by cluster
        for cluster_id, papers in sorted(clusters.items()):
            f.write(f"## Cluster {cluster_id}\n\n")
            
            for i, paper in enumerate(papers):
                authors = ", ".join([a.get("name", "") for a in paper.authors[:3]]) if paper.authors else "Unknown"
                if len(paper.authors) > 3:
                    authors += " et al."
                    
                f.write(f"### {i+1}. {paper.title}\n")
                f.write(f"**Authors:** {authors}\n")
                f.write(f"**Year:** {paper.year or 'Unknown'}\n")
                f.write(f"**Venue:** {paper.venue or 'Unknown'}\n")
                f.write(f"**Relevance:** {paper.relevance_score:.2f} (Confidence: {paper.confidence_score:.2f})\n")
                f.write(f"**Keywords:** {', '.join(paper.keywords) if paper.keywords else 'None'}\n")
                
                if paper.key_findings:
                    f.write("\n**Key Findings:**\n")
                    for finding in paper.key_findings:
                        f.write(f"- {finding}\n")
                
                if paper.methodology_notes:
                    f.write("\n**Methodology Notes:**\n")
                    for note in paper.methodology_notes:
                        f.write(f"- {note}\n")
                
                if paper.abstract:
                    f.write(f"\n**Abstract:** {paper.abstract}\n")
                f.write("\n")
        
    print(f"Literature review complete! Output saved to {args.output_dir}")
    print(f"- Review section: {os.path.join(args.output_dir, 'review_section.tex')}")
    print(f"- BibTeX entries: {os.path.join(args.output_dir, 'references.bib')}")
    print(f"- Paper details: {os.path.join(args.output_dir, 'paper_details.md')}")
    print(f"- Research plan: {os.path.join(args.output_dir, 'research_plan.md')}")
    print(f"- Progress log: {os.path.join(args.output_dir, 'progress_report.md')}")
    print(f"- Key insights: {os.path.join(args.output_dir, 'key_insights.md')}")

if __name__ == "__main__":
    main() 