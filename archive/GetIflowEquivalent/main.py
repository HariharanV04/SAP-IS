# Import the functions from each step
from extract_terms import extract_terms_from_markdown, generate_search_terms
from search_discovery import SAPDiscoverySearcher
from score_results import ContentSimilarityScorer
from present_findings import ResultsPresenter
import os
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_markdown_for_iflow(markdown_file_path, output_dir=None, github_token=None):
    """
    Process a markdown file to find SAP Integration Suite (iFlow) equivalents.

    Args:
        markdown_file_path (str): Path to the markdown file with MuleSoft documentation
        output_dir (str, optional): Directory to save output files. If None, uses the current directory.
        github_token (str, optional): GitHub token for API access. If None, tries to get from environment.

    Returns:
        dict: Dictionary with paths to generated files and other information
    """
    if github_token is None:
        github_token = os.environ.get("GITHUB_TOKEN", None)

    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(markdown_file_path))

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create a charts directory in the output directory
    charts_dir = os.path.join(output_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    # Initialize result dictionary
    result = {
        "status": "failed",
        "message": "",
        "files": {}
    }

    try:
        # Step 1: Extract terms from markdown
        logger.info("Step 1: Extracting terms from markdown...")
        extracted_terms = extract_terms_from_markdown(markdown_file_path)
        search_terms = generate_search_terms(extracted_terms)
        logger.info("Extracted key terms and generated search terms")
        logger.info(f"Primary search terms: {search_terms['primary'][:3]}...")

        # Step 2: Search SAP Integration Recipes from GitHub repository
        logger.info("Step 2: Searching SAP Integration Recipes via GitHub API...")
        searcher = SAPDiscoverySearcher(github_token=github_token)
        search_results = searcher.execute_search_strategy(search_terms)
        logger.info(f"Found {search_results['total_count']} potential matches")

        if search_results['total_count'] == 0:
            result["message"] = "No matches found. Please check your search terms."
            return result

        # Step 3: Score and rank results
        logger.info("Step 3: Scoring and ranking results...")
        scorer = ContentSimilarityScorer(extracted_terms)
        scored_results = scorer.score_and_rank_results(search_results['results'], search_results['sources'])
        logger.info("Scored and ranked results based on similarity")

        # Step 4: Present findings
        logger.info("Step 4: Presenting findings...")
        presenter = ResultsPresenter(scored_results, extracted_terms, search_terms)

        # Generate report and charts
        report_filename = "integration_match_report.html"
        report_path = presenter.save_report(os.path.join(output_dir, report_filename))
        chart_paths = presenter.create_charts(charts_dir)

        # Create a summary JSON file
        summary = {
            "total_matches": search_results['total_count'],
            "top_matches": [
                {
                    "name": result.get("Name", "Unknown"),
                    "description": result.get("Description", ""),
                    "score": result.get("_scores", {}).get("combined_score", 0),
                    "url": result.get("GitHubUrl", "")
                }
                for result in scored_results[:5]  # Include top 5 matches
            ],
            "search_terms": search_terms
        }

        summary_filename = "iflow_match_summary.json"
        summary_path = os.path.join(output_dir, summary_filename)
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        # Update result dictionary
        result["status"] = "success"
        result["message"] = f"Found {search_results['total_count']} potential matches"
        result["files"] = {
            "report": report_path,
            "charts": chart_paths,
            "summary": summary_path
        }

        logger.info(f"Generated detailed report: {report_path}")
        logger.info(f"Generated charts in: {charts_dir}")
        logger.info(f"Generated summary: {summary_path}")
        logger.info("Process completed successfully!")

        return result

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

        result["status"] = "failed"
        result["message"] = f"Error processing markdown: {str(e)}"

        return result

def main():
    """Command-line entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Process MuleSoft documentation to find SAP Integration Suite equivalents")
    parser.add_argument("--input", "-i", required=True, help="Path to markdown file with MuleSoft documentation")
    parser.add_argument("--output", "-o", help="Directory to save output files")
    parser.add_argument("--token", "-t", help="GitHub token for API access")

    args = parser.parse_args()

    result = process_markdown_for_iflow(
        markdown_file_path=args.input,
        output_dir=args.output,
        github_token=args.token
    )

    if result["status"] == "success":
        print(f"\nProcess completed successfully!")
        print(f"Report: {result['files']['report']}")
        print(f"Summary: {result['files']['summary']}")
    else:
        print(f"\nProcess failed: {result['message']}")

if __name__ == "__main__":
    main()

