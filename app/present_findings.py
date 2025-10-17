import json
import os
import datetime
from tabulate import tabulate
# Set matplotlib backend to Agg (non-interactive) to avoid Tkinter issues
import matplotlib
matplotlib.use('Agg')  # This must be done before importing pyplot
import matplotlib.pyplot as plt
import numpy as np
from termcolor import colored

class ResultsPresenter:
    """
    Present the search results and recommendations in a useful format
    """

    def __init__(self, scored_results, extracted_terms, search_terms):
        """
        Initialize with scored results and terms

        Args:
            scored_results (list): List of scored and ranked results
            extracted_terms (dict): Dictionary of extracted terms from Mulesoft
            search_terms (dict): Dictionary of search terms used
        """
        self.scored_results = scored_results
        self.extracted_terms = extracted_terms
        self.search_terms = search_terms

        # Set threshold for high-quality matches
        self.high_quality_threshold = 20
        self.medium_quality_threshold = 10

    def generate_summary(self):
        """
        Generate a summary of the search results

        Returns:
            dict: Summary information
        """
        if not self.scored_results:
            return {
                "total_results": 0,
                "high_quality_matches": 0,
                "medium_quality_matches": 0,
                "top_match": None,
                "recommendation": "No matches found. Consider broadening your search terms."
            }

        # Count results by quality
        high_quality = 0
        medium_quality = 0

        for result in self.scored_results:
            score = result.get('_scores', {}).get('combined_score', 0)
            if score >= self.high_quality_threshold:
                high_quality += 1
            elif score >= self.medium_quality_threshold:
                medium_quality += 1

        # Get top match if available
        top_match = self.scored_results[0] if self.scored_results else None

        # Generate recommendation
        if high_quality > 0:
            recommendation = f"Found {high_quality} high-quality matches. Review the top matches for potential integration."
        elif medium_quality > 0:
            recommendation = f"Found {medium_quality} medium-quality matches. These may require some adaptation."
        else:
            recommendation = "Only lower-quality matches found. Consider searching with different terms or creating a custom integration."

        return {
            "total_results": len(self.scored_results),
            "high_quality_matches": high_quality,
            "medium_quality_matches": medium_quality,
            "top_match": top_match,
            "recommendation": recommendation
        }

    def print_table_results(self, max_results=10):
        """
        Print results in a tabular format

        Args:
            max_results (int): Maximum number of results to show
        """
        if not self.scored_results:
            print("No results found.")
            return

        # Limit results
        results_to_show = self.scored_results[:max_results]

        # Prepare table data
        table_data = []
        for i, result in enumerate(results_to_show):
            name = result.get('Name', '')
            content_type = result.get('ContentType', '')
            score = result.get('_scores', {}).get('combined_score', 0)

            # Determine quality level
            if score >= self.high_quality_threshold:
                quality = "High"
            elif score >= self.medium_quality_threshold:
                quality = "Medium"
            else:
                quality = "Low"

            # Get matching terms (up to 3)
            matching_terms = []
            for term in self.extracted_terms.get('domain_terms', []) + self.extracted_terms.get('technical_terms', []):
                if term.lower() in (result.get('Name', '') + ' ' + result.get('Description', '')).lower():
                    matching_terms.append(term)
                    if len(matching_terms) >= 3:
                        break

            matching_terms_str = ", ".join(matching_terms[:3])
            if len(matching_terms) > 3:
                matching_terms_str += "..."

            table_data.append([
                i + 1,
                name,
                content_type,
                f"{score:.2f}",
                quality,
                matching_terms_str
            ])

        # Print table
        headers = ["Rank", "Name", "Type", "Score", "Quality", "Matching Terms"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def print_detailed_result(self, result_index=0):
        """
        Print detailed information about a specific result

        Args:
            result_index (int): Index of the result to show (default: 0 for top result)
        """
        if not self.scored_results or result_index >= len(self.scored_results):
            print("Result not found.")
            return

        result = self.scored_results[result_index]

        # Extract information
        name = result.get('Name', '')
        description = result.get('Description', '')
        content_type = result.get('ContentType', '')
        categories = result.get('Categories', [])
        tags = result.get('Tags', [])
        version = result.get('Version', '')
        scores = result.get('_scores', {})

        # Print header
        print("\n" + "=" * 80)
        print(f" DETAILED INFORMATION FOR: {name} (Rank: {result_index + 1})")
        print("=" * 80)

        # Print basic information
        print(f"Type:        {content_type}")
        print(f"Version:     {version}")
        print(f"Description: {description}")

        # Print categories and tags
        if categories:
            print(f"Categories:  {', '.join(categories)}")
        if tags:
            print(f"Tags:        {', '.join(tags)}")

        # Print scores
        print("\nSIMILARITY SCORES:")
        print(f"  Term Match:          {scores.get('term_match', 0):.2f}")
        print(f"  Endpoint Match:      {scores.get('endpoint_match', 0):.2f}")
        print(f"  Content Similarity:  {scores.get('content_similarity', 0):.2f}")
        print(f"  Search Priority:     {scores.get('search_priority', 0):.2f}")
        print(f"  Combined Score:      {scores.get('combined_score', 0):.2f}")

        # Determine quality level
        score = scores.get('combined_score', 0)
        if score >= self.high_quality_threshold:
            quality = "HIGH"
            color = "green"
        elif score >= self.medium_quality_threshold:
            quality = "MEDIUM"
            color = "yellow"
        else:
            quality = "LOW"
            color = "red"

        print(f"\nOverall Match Quality: {colored(quality, color)}")

        # Print matching terms
        matching_terms = []
        for term in self.extracted_terms.get('domain_terms', []) + self.extracted_terms.get('technical_terms', []):
            if term.lower() in (name + ' ' + description).lower():
                matching_terms.append(term)

        if matching_terms:
            print("\nMATCHING TERMS:")
            for term in matching_terms:
                print(f"  - {term}")

        print("\n" + "=" * 80)

    def generate_recommendations(self):
        """
        Generate recommendations based on the search results

        Returns:
            list: List of recommendation dictionaries
        """
        recommendations = []

        # If no results or low quality results
        if not self.scored_results or all(result.get('_scores', {}).get('combined_score', 0) < self.medium_quality_threshold for result in self.scored_results):
            recommendations.append({
                "type": "warning",
                "message": "No high-quality matches found",
                "details": "Consider creating a custom integration or modifying your search terms.",
                "action": "Try searching with broader business domain terms or focus on technical patterns."
            })

        # If we have good matches
        high_quality_matches = [result for result in self.scored_results if result.get('_scores', {}).get('combined_score', 0) >= self.high_quality_threshold]
        if high_quality_matches:
            top_match = high_quality_matches[0]
            recommendations.append({
                "type": "success",
                "message": f"Found {len(high_quality_matches)} high-quality matches",
                "details": f"The top match '{top_match.get('Name')}' is a good candidate for your implementation.",
                "action": f"Review the details and consider downloading this integration package."
            })

            # If multiple high-quality matches, suggest comparison
            if len(high_quality_matches) > 1:
                recommendations.append({
                    "type": "info",
                    "message": "Multiple good matches found",
                    "details": "Consider comparing the top matches to find the best fit for your requirements.",
                    "action": "Use the detailed view to compare features and compatibility."
                })

        # If we have medium quality matches
        medium_quality_matches = [result for result in self.scored_results if result.get('_scores', {}).get('combined_score', 0) >= self.medium_quality_threshold and result.get('_scores', {}).get('combined_score', 0) < self.high_quality_threshold]
        if medium_quality_matches and not high_quality_matches:
            recommendations.append({
                "type": "info",
                "message": f"Found {len(medium_quality_matches)} medium-quality matches",
                "details": "These may require some adaptation to fit your requirements.",
                "action": "Review these matches for useful patterns or components that can be adapted."
            })

        # Add general recommendation about integration approach
        if self.scored_results:
            # Check if there are any API/flow matches
            api_matches = [result for result in self.scored_results if 'api' in result.get('ContentType', '').lower() or 'flow' in result.get('ContentType', '').lower()]

            if api_matches:
                recommendations.append({
                    "type": "info",
                    "message": "Integration approach recommendation",
                    "details": "Found API/flow integration patterns that match your Mulesoft implementation.",
                    "action": "Consider a direct API approach for migrating your Mulesoft implementation."
                })
            else:
                recommendations.append({
                    "type": "info",
                    "message": "Integration approach recommendation",
                    "details": "Consider package-based integration for your implementation.",
                    "action": "Review the matched integration packages for compatibility with your requirements."
                })

        return recommendations

    def save_report(self, output_path="integration_match_report.html"):
        """
        Save a detailed HTML report with all findings

        Args:
            output_path (str): Path to save the HTML report
        """
        # Generate summary
        summary = self.generate_summary()

        # Generate recommendations
        recommendations = self.generate_recommendations()

        # Prepare results data (limit to top 20)
        results_data = []
        for i, result in enumerate(self.scored_results[:20]):
            # Get matching terms
            matching_terms = []
            for term in self.extracted_terms.get('domain_terms', []) + self.extracted_terms.get('technical_terms', []):
                if term.lower() in (result.get('Name', '') + ' ' + result.get('Description', '')).lower():
                    matching_terms.append(term)

            # Determine quality level
            score = result.get('_scores', {}).get('combined_score', 0)
            if score >= self.high_quality_threshold:
                quality = "High"
                quality_class = "high"
            elif score >= self.medium_quality_threshold:
                quality = "Medium"
                quality_class = "medium"
            else:
                quality = "Low"
                quality_class = "low"

            results_data.append({
                "rank": i + 1,
                "name": result.get('Name', ''),
                "description": result.get('Description', ''),
                "content_type": result.get('ContentType', ''),
                "categories": result.get('Categories', []),
                "tags": result.get('Tags', []),
                "version": result.get('Version', ''),
                "scores": result.get('_scores', {}),
                "matching_terms": matching_terms,
                "quality": quality,
                "quality_class": quality_class
            })

        # Create HTML content
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Integration Match Report</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }
                .container { max-width: 1200px; margin: 0 auto; }
                h1, h2, h3 { color: #2c3e50; }
                .summary { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                .recommendations { margin-bottom: 20px; }
                .recommendation { padding: 10px; margin-bottom: 10px; border-radius: 5px; }
                .recommendation.warning { background-color: #fff3cd; border-left: 5px solid #ffc107; }
                .recommendation.success { background-color: #d4edda; border-left: 5px solid #28a745; }
                .recommendation.info { background-color: #d1ecf1; border-left: 5px solid #17a2b8; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
                .quality-high { color: #28a745; font-weight: bold; }
                .quality-medium { color: #ffc107; font-weight: bold; }
                .quality-low { color: #dc3545; font-weight: bold; }
                .detail-view { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; display: none; }
                .score-bar { background-color: #e9ecef; height: 20px; border-radius: 5px; margin-bottom: 5px; }
                .score-fill { height: 100%; border-radius: 5px; }
                .term-match { background-color: #007bff; }
                .endpoint-match { background-color: #28a745; }
                .content-similarity { background-color: #ffc107; }
                .search-priority { background-color: #6c757d; }
                .combined-score { background-color: #dc3545; }
                .toggle-btn { background-color: #4CAF50; color: white; padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; }
                .tag { display: inline-block; background-color: #e9ecef; padding: 3px 8px; border-radius: 3px; margin-right: 5px; margin-bottom: 5px; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Integration Match Report</h1>
                <p>Generated on: """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>

                <div class="summary">
                    <h2>Summary</h2>
                    <p><strong>Total Results:</strong> """ + str(summary.get("total_results", 0)) + """</p>
                    <p><strong>High-Quality Matches:</strong> """ + str(summary.get("high_quality_matches", 0)) + """</p>
                    <p><strong>Medium-Quality Matches:</strong> """ + str(summary.get("medium_quality_matches", 0)) + """</p>
                    <p><strong>Recommendation:</strong> """ + summary.get("recommendation", "") + """</p>
                </div>

                <div class="recommendations">
                    <h2>Recommendations</h2>
        """

        # Add recommendations
        for rec in recommendations:
            html_content += """
                    <div class="recommendation """ + rec.get("type", "") + """">
                        <h3>""" + rec.get("message", "") + """</h3>
                        <p>""" + rec.get("details", "") + """</p>
                        <p><strong>Recommended Action:</strong> """ + rec.get("action", "") + """</p>
                    </div>
            """

        html_content += """
                </div>

                <h2>Match Results</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Score</th>
                            <th>Quality</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        # Add results
        for result in results_data:
            html_content += """
                        <tr>
                            <td>""" + str(result.get("rank", "")) + """</td>
                            <td>""" + result.get("name", "") + """</td>
                            <td>""" + result.get("content_type", "") + """</td>
                            <td>""" + f"{result.get('scores', {}).get('combined_score', 0):.2f}" + """</td>
                            <td class="quality-""" + result.get("quality_class", "") + """">""" + result.get("quality", "") + """</td>
                            <td><button class="toggle-btn" onclick="toggleDetail('detail-""" + str(result.get("rank", "")) + """')">Details</button></td>
                        </tr>
            """

        html_content += """
                    </tbody>
                </table>
        """

        # Add detail views
        for result in results_data:
            html_content += """
                <div id="detail-""" + str(result.get("rank", "")) + """" class="detail-view">
                    <h3>""" + result.get("name", "") + """</h3>
                    <p><strong>Description:</strong> """ + result.get("description", "") + """</p>
                    <p><strong>Type:</strong> """ + result.get("content_type", "") + """</p>
                    <p><strong>Version:</strong> """ + result.get("version", "") + """</p>

                    <h4>Categories</h4>
                    <div>
            """

            # Add categories
            for category in result.get("categories", []):
                html_content += """<span class="tag">""" + category + """</span>"""

            html_content += """
                    </div>

                    <h4>Tags</h4>
                    <div>
            """

            # Add tags
            for tag in result.get("tags", []):
                html_content += """<span class="tag">""" + tag + """</span>"""

            html_content += """
                    </div>

                    <h4>Matching Terms</h4>
                    <div>
            """

            # Add matching terms
            for term in result.get("matching_terms", []):
                html_content += """<span class="tag">""" + term + """</span>"""

            scores = result.get("scores", {})

            html_content += """
                    </div>

                    <h4>Similarity Scores</h4>

                    <p>Term Match: """ + f"{scores.get('term_match', 0):.2f}" + """</p>
                    <div class="score-bar">
                        <div class="score-fill term-match" style="width: """ + str(min(100, scores.get("term_match", 0) * 2)) + """%"></div>
                    </div>

                    <p>Endpoint Match: """ + f"{scores.get('endpoint_match', 0):.2f}" + """</p>
                    <div class="score-bar">
                        <div class="score-fill endpoint-match" style="width: """ + str(min(100, scores.get("endpoint_match", 0) * 5)) + """%"></div>
                    </div>

                    <p>Content Similarity: """ + f"{scores.get('content_similarity', 0):.2f}" + """</p>
                    <div class="score-bar">
                        <div class="score-fill content-similarity" style="width: """ + str(min(100, scores.get("content_similarity", 0) * 100)) + """%"></div>
                    </div>

                    <p>Search Priority: """ + f"{scores.get('search_priority', 0):.2f}" + """</p>
                    <div class="score-bar">
                        <div class="score-fill search-priority" style="width: """ + str(min(100, scores.get("search_priority", 0) * 10)) + """%"></div>
                    </div>

                    <p><strong>Combined Score: """ + f"{scores.get('combined_score', 0):.2f}" + """</strong></p>
                    <div class="score-bar">
                        <div class="score-fill combined-score" style="width: """ + str(min(100, scores.get("combined_score", 0) * 2)) + """%"></div>
                    </div>
                </div>
            """

        # Add JavaScript for toggling details
        html_content += """
                <script>
                    function toggleDetail(id) {
                        var element = document.getElementById(id);
                        if (element.style.display === "block") {
                            element.style.display = "none";
                        } else {
                            element.style.display = "block";
                        }
                    }
                </script>
            </div>
        </body>
        </html>
        """

        # Write HTML to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def create_charts(self, output_dir="charts"):
        """
        Create visualization charts for the results

        Args:
            output_dir (str): Directory to save the charts

        Returns:
            list: List of paths to generated chart files
        """
        if not self.scored_results:
            return []

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        chart_files = []

        # 1. Top matches bar chart
        plt.figure(figsize=(12, 6))

        # Get top 10 results
        top_results = self.scored_results[:10]
        names = [result.get('Name', '')[:20] + '...' if len(result.get('Name', '')) > 20 else result.get('Name', '') for result in top_results]
        scores = [result.get('_scores', {}).get('combined_score', 0) for result in top_results]

        # Create bars
        bars = plt.bar(names, scores, color='skyblue')

        # Color bars based on score
        for i, bar in enumerate(bars):
            if scores[i] >= self.high_quality_threshold:
                bar.set_color('green')
            elif scores[i] >= self.medium_quality_threshold:
                bar.set_color('orange')
            else:
                bar.set_color('red')

        plt.xlabel('Integration Content')
        plt.ylabel('Match Score')
        plt.title('Top 10 Integration Matches')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save chart
        chart_path = os.path.join(output_dir, 'top_matches.png')
        plt.savefig(chart_path)
        plt.close()
        chart_files.append(chart_path)

        # 2. Score breakdown for top 5 matches
        plt.figure(figsize=(12, 8))

        # Get top 5 results
        top_5_results = self.scored_results[:5]
        names = [result.get('Name', '')[:15] + '...' if len(result.get('Name', '')) > 15 else result.get('Name', '') for result in top_5_results]

        # Get score components
        term_match_scores = [result.get('_scores', {}).get('term_match', 0) for result in top_5_results]
        endpoint_match_scores = [result.get('_scores', {}).get('endpoint_match', 0) for result in top_5_results]
        content_similarity_scores = [result.get('_scores', {}).get('content_similarity', 0) * 20 for result in top_5_results]  # Scale for visibility
        search_priority_scores = [result.get('_scores', {}).get('search_priority', 0) for result in top_5_results]

        # Set bar width
        bar_width = 0.2

        # Set positions
        r1 = np.arange(len(names))
        r2 = [x + bar_width for x in r1]
        r3 = [x + bar_width for x in r2]
        r4 = [x + bar_width for x in r3]

        # Create grouped bars
        plt.bar(r1, term_match_scores, width=bar_width, label='Term Match', color='royalblue')
        plt.bar(r2, endpoint_match_scores, width=bar_width, label='Endpoint Match', color='seagreen')
        plt.bar(r3, content_similarity_scores, width=bar_width, label='Content Similarity (x20)', color='gold')
        plt.bar(r4, search_priority_scores, width=bar_width, label='Search Priority', color='gray')

        plt.xlabel('Integration Content')
        plt.ylabel('Score Component Value')
        plt.title('Score Breakdown for Top 5')
        plt.xticks([r + bar_width * 1.5 for r in range(len(names))], names, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()

        # Save chart
        chart_path = os.path.join(output_dir, 'score_breakdown.png')
        plt.savefig(chart_path)
        plt.close()
        chart_files.append(chart_path)

        # 3. Quality distribution pie chart
        plt.figure(figsize=(8, 8))

        # Count results by quality
        high_quality = 0
        medium_quality = 0
        low_quality = 0

        for result in self.scored_results:
            score = result.get('_scores', {}).get('combined_score', 0)
            if score >= self.high_quality_threshold:
                high_quality += 1
            elif score >= self.medium_quality_threshold:
                medium_quality += 1
            else:
                low_quality += 1

        # Create pie chart
        labels = ['High Quality', 'Medium Quality', 'Low Quality']
        sizes = [high_quality, medium_quality, low_quality]
        colors = ['green', 'orange', 'red']
        explode = (0.1, 0, 0)  # Explode high quality slice

        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title('Quality Distribution of Matches')

        # Save chart
        chart_path = os.path.join(output_dir, 'quality_distribution.png')
        plt.savefig(chart_path)
        plt.close()
        chart_files.append(chart_path)

        return chart_files
