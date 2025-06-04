# ScholarSynthesis: Your AI-Powered Literature Review Assistant

Automatically generate comprehensive literature reviews for research papers with minimal effort.

## Overview

ScholarSynthesis helps researchers create focused literature reviews by:
1. Taking your paper's title and abstract as input
2. Finding the most relevant related papers using Semantic Scholar
3. Ranking papers by relevance to your research
4. Generating a coherent literature review section with proper citations
5. Creating BibTeX entries for all referenced papers

## Features

- **Automated Search**: Leverages Semantic Scholar API to find relevant papers
- **Relevance Ranking**: Uses advanced LLM techniques to evaluate paper relevance
- **Reference Expansion**: Explores citation networks to find important related work
- **Review Generation**: Creates coherent thematic literature reviews, not just summaries
- **Multiple Output Formats**: Generate outputs in Markdown, LaTeX, or HTML
- **Progress Tracking**: Visual indicators show real-time progress of your literature review
- **Configurable**: Adjust preferences via configuration files
- **Caching System**: Save time with cached search results and LLM responses
- **Modular Architecture**: Easily extendable for future enhancements

## Quick Start Guide

### Installation

#### On Windows:
1. Double-click the `setup-script.bat` file
2. Follow the prompts to complete installation
3. When setup is complete, a command prompt will open with the virtual environment activated

#### On Linux/Mac:
1. Open a terminal in the project directory
2. Run: `chmod +x setup-script.sh`
3. Run: `./setup-script.sh`
4. Activate the environment: `source litreview_env/bin/activate`

### Your First Literature Review

Try this simple example to generate your first literature review:

```bash
litreview-agent --title "Machine Learning in Healthcare" --abstract "This paper explores applications of machine learning techniques in healthcare diagnostics and treatment planning."
```

When you run this command:
1. ScholarSynthesis searches for relevant papers using Semantic Scholar
2. It analyzes the papers for relevance to your topic
3. It generates a comprehensive literature review
4. It creates properly formatted citations

### Viewing Results

Look in the `output` directory for these files:
- `review_section.tex`: Your literature review (LaTeX format)
- `references.bib`: BibTeX citations for all papers
- `paper_details.md`: Details about each paper found
- `research_plan.md`: The research plan generated to guide the review
- `progress_report.md`: Log of the literature review process
- `key_insights.md`: Key insights extracted from the papers

## Detailed Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Access to a suitable LLM model supported by VLLM (e.g., Llama 3)

### Option 1: Using the setup script (Linux/Mac)

1. Clone this repository:
   ```bash
   git clone https://github.com/Vatsal-Jha256/ScholarSynthesis.git
   cd ScholarSynthesis
   ```

2. Make the setup script executable and run it:
   ```bash
   chmod +x setup-script.sh
   ./setup-script.sh
   ```

3. Activate the virtual environment:
   ```bash
   source litreview_env/bin/activate
   ```

### Option 2: Manual installation (All platforms including Windows)

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ScholarSynthesis.git
   cd ScholarSynthesis
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv litreview_env
   litreview_env\Scripts\activate

   # On Linux/Mac
   python3 -m venv litreview_env
   source litreview_env/bin/activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Usage

### Basic Usage

After installation, you can use ScholarSynthesis directly from the command line:

```bash
litreview-agent --title "Your Paper Title" --abstract "Your paper abstract" --num_papers 15
```

### Common Usage Scenarios

#### More Papers
To include more papers in your review:
```bash
litreview-agent --title "Your Title" --abstract "Your abstract" --num_papers 25
```

#### Different Output Format
To generate HTML output instead of LaTeX:
```bash
litreview-agent --title "Your Title" --abstract "Your abstract" --output_format html
```

#### Time-Limited Search
To only include recent papers (2020-2023):
```bash
litreview-agent --title "Your Title" --abstract "Your abstract" --start_year 2020 --end_year 2023
```

### Advanced Usage

#### Command-line Arguments

```
usage: litreview-agent [-h] --title TITLE --abstract ABSTRACT [--num_papers NUM_PAPERS] [--output_dir OUTPUT_DIR]
                       [--model MODEL] [--api_key API_KEY] [--no_expand_refs] [--relevance_threshold RELEVANCE_THRESHOLD]
                       [--start_year START_YEAR] [--end_year END_YEAR] [--keep_duplicates] [--max_iterations MAX_ITERATIONS]
```

| Argument | Description | Default |
|----------|-------------|---------|
| `--title` | Title of your paper | Required |
| `--abstract` | Abstract of your paper | Required |
| `--num_papers` | Number of papers to include | 15 |
| `--output_dir` | Directory to save output files | ./output |
| `--model` | VLLM model to use | meta-llama/Meta-Llama-3-8B-Instruct |
| `--api_key` | Semantic Scholar API key | None |
| `--no_expand_refs` | Disable reference expansion | False |
| `--relevance_threshold` | Minimum relevance score (0.0-1.0) | 0.5 |
| `--start_year` | Start year for filtering papers | None |
| `--end_year` | End year for filtering papers | None |
| `--keep_duplicates` | Don't remove duplicate papers | False |
| `--max_iterations` | Maximum search iterations per strategy | 3 |

#### Configuration File

You can customize ScholarSynthesis by creating a configuration file. Create a file named `config.json` in your working directory:

```json
{
  "llm": {
    "model_name": "meta-llama/Meta-Llama-3-8B-Instruct",
    "temperature": 0.1,
    "max_tokens": 1024
  },
  "search": {
    "api_key": null,
    "max_papers_per_query": 15,
    "max_search_iterations": 3
  },
  "analysis": {
    "relevance_threshold": 0.5,
    "duplicate_threshold": 0.8,
    "min_keywords": 5
  },
  "output": {
    "default_format": "markdown",
    "output_dir": "./output",
    "create_summary": true,
    "verbose_output": true
  },
  "caching": {
    "enabled": true,
    "cache_dir": "./.cache",
    "max_cache_age_days": 7
  }
}
```

## Examples

### Simple Literature Review

```bash
litreview-agent --title "Transformers in Natural Language Processing" --abstract "This paper explores the impact of transformer-based models on NLP tasks."
```

### Focused Review with Time Frame

```bash
litreview-agent --title "Recent Advances in Quantum Computing" --abstract "This paper reviews recent developments in quantum computing algorithms." --start_year 2020 --end_year 2023 --relevance_threshold 0.7
```

## Troubleshooting

### Common Issues

1. **VLLM Model Not Found**: Ensure that you have the specified model available for VLLM.
   ```bash
   # For local models, verify the path
   # For Hugging Face models, check your internet connection
   ```

2. **API Rate Limiting**: Semantic Scholar has rate limits. Consider obtaining an API key for higher limits.

3. **Output Quality Issues**: Try adjusting the relevance threshold or increasing the number of papers.

4. **Low Memory/Out of Memory**: Try using a smaller LLM model or reduce the number of papers.

5. **Other Issues**:
   - Make sure you're using Python 3.8 or higher
   - Verify that you have an internet connection for paper searches
   - Ensure you have sufficient disk space for caching

## Package Structure

The project is organized in a proper Python package structure:
```
scholarSynthesis/
├── __init__.py        # Package initialization
├── data/              # Data models
├── search/            # Search functionality
├── llm/               # LLM integration
├── analysis/          # Paper analysis
├── core/              # Core agent logic
├── config/            # Configuration management
├── cache/             # Caching system
├── utils/             # Utilities
└── output/            # Output formatting
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
