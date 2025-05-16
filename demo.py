"""
Example usage script for LitReviewAgent
"""

from litreview_agent import LitReviewAgent
import os

def run_example():
    # Create output directory
    output_dir = "./example_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the agent
    agent = LitReviewAgent(
        llm_model_name="meta-llama/Meta-Llama-3-8B-Instruct",
        semantic_scholar_api_key=None,  # Add your API key if you have one
        relevance_threshold=0.6,  # Set a higher threshold for better quality results
        max_search_iterations=2   # Number of search refinement iterations
    )
    
    # Example paper information
    title = "Attention Is All You Need: A Comprehensive Survey of Transformer Models"
    abstract = """
    Transformer models have revolutionized natural language processing and 
    increasingly other domains such as computer vision. This survey examines 
    the evolution of transformer architectures since the original 'Attention Is 
    All You Need' paper, analyzing efficiency improvements, domain adaptations, 
    and emerging capabilities across modalities. We categorize key innovations 
    and discuss future research directions.
    """
    
    # Run the literature review with enhanced agentic capabilities
    review_text, bibtex_entries, selected_papers, research_data = agent.run_literature_review(
        title=title,
        abstract=abstract,
        num_papers=10,
        expand_references=True,
        min_relevance_score=0.5,  # Override default threshold if needed
        year_range=(2018, 2023),  # Focus on recent papers
        remove_duplicates=True,   # Remove duplicate papers
        output_dir=output_dir     # Save outputs to specific directory
    )
    
    # Print results summary
    print("\n===== RESEARCH SUMMARY =====\n")
    print(f"Generated {len(selected_papers)} paper literature review based on:")
    print(f"- {len(research_data['research_plan'].research_questions)} research questions")
    print(f"- {len(research_data['research_plan'].search_strategies)} search strategies")
    print(f"- {research_data['search_iterations']} search iterations")
    print(f"- {research_data['total_papers_found']} total papers found")
    print(f"- {len(research_data['insights'])} key insights extracted")
    
    # Print the key insights
    print("\n===== KEY INSIGHTS =====\n")
    for i, insight in enumerate(research_data['insights']):
        print(f"{i+1}. [{insight.type}] {insight.description[:150]}...")
    
    # Print the results
    print("\n===== GENERATED REVIEW SECTION =====\n")
    print(review_text[:500] + "...\n[Review truncated for display]")
    
    print("\n===== FILES GENERATED =====\n")
    print(f"- {output_dir}/review_section.tex (literature review in LaTeX format)")
    print(f"- {output_dir}/references.bib (BibTeX entries)")
    print(f"- {output_dir}/paper_details.md (paper details grouped by clusters)")
    print(f"- {output_dir}/research_plan.md (generated research plan)")
    print(f"- {output_dir}/progress_report.md (progress log and statistics)")
    print(f"- {output_dir}/key_insights.md (key insights extracted from papers)")

if __name__ == "__main__":
    run_example()