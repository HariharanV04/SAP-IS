import requests
import json
import time
import re
import base64
from collections import defaultdict

class SAPDiscoverySearcher:
    """
    Class to search for SAP integration content using GitHub API
    """

    def __init__(self, github_token=None):
        """
        Initialize with GitHub token for API access

        Args:
            github_token (str, optional): GitHub personal access token
        """
        self.repo_owner = "SAP"
        self.repo_name = "apibusinesshub-integration-recipes"
        self.github_token = github_token
        self.results_cache = {}  # Cache search results
        self.integration_content = []

        # Base headers for GitHub API
        self.headers = {
            'Accept': 'application/vnd.github+json'
        }

        # Add token if provided
        if self.github_token:
            self.headers['Authorization'] = f'token {self.github_token}'

    def _fetch_directory_contents(self, path=""):
        """
        Fetch contents of a directory from GitHub

        Args:
            path (str): Path within the repository

        Returns:
            list: Directory contents
        """
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{path}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching directory contents: {response.status_code} - {response.text}")
            return []

    def _fetch_file_content(self, path):
        """
        Fetch content of a file from GitHub

        Args:
            path (str): Path to the file

        Returns:
            str: File content
        """
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{path}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            content_data = response.json()
            if content_data.get('encoding') == 'base64':
                return base64.b64decode(content_data.get('content')).decode('utf-8')
            return content_data.get('content', '')
        else:
            print(f"Error fetching file content: {response.status_code} - {response.text}")
            return ""

    def _parse_readme_content(self, content, path):
        """
        Parse README content to extract metadata

        Args:
            content (str): README content
            path (str): Path to the README

        Returns:
            dict: Metadata for the integration content
        """
        try:
            # Extract name from first heading
            name_match = self._extract_first_heading(content)
            name = name_match if name_match else path.split('/')[-1]

            # Extract description (first paragraph after title)
            description = self._extract_first_paragraph(content, name)

            # Extract categories and tags
            categories = self._extract_metadata(content, ["Category:", "Categories:", "Type:", "Types:"])
            tags = self._extract_metadata(content, ["Tag:", "Tags:", "Keywords:", "Keyword:"])

            # Generate ID from path
            content_id = path.replace('/', '-')

            # Find version information
            version = "1.0.0"  # Default version
            version_match = self._extract_version(content)
            if version_match:
                version = version_match

            # Determine content type based on path
            content_type = "IntegrationPattern"
            if "Integration Flow" in path:
                content_type = "IntegrationFlow"
            elif "Adapters" in path:
                content_type = "Adapter"

            # Create content item
            content_item = {
                "Id": content_id,
                "Name": name,
                "Description": description,
                "Categories": categories,
                "Tags": tags,
                "Version": version,
                "ContentType": content_type,
                "Path": path,
                "GitHubUrl": f"https://github.com/{self.repo_owner}/{self.repo_name}/tree/master/{path}"
            }

            return content_item

        except Exception as e:
            print(f"Error parsing README {path}: {e}")
            return None

    def _extract_first_heading(self, content):
        """Extract the first heading from markdown content"""
        heading_match = self._first_match(content, r'# (.*?)(?:\n|$)')
        if not heading_match:
            heading_match = self._first_match(content, r'## (.*?)(?:\n|$)')
        return heading_match

    def _extract_first_paragraph(self, content, title):
        """Extract the first paragraph after a title"""
        # Try to find paragraph after the title
        title_escaped = title.replace('[', r'\[').replace(']', r'\]')
        paragraph_match = self._first_match(content, f'# {title_escaped}.*?\n+([^\n#].*?)(?:\n\n|\n#|$)', re.DOTALL)
        if not paragraph_match:
            # Try to find the first paragraph
            paragraph_match = self._first_match(content, r'\n+([^\n#].*?)(?:\n\n|\n#|$)', re.DOTALL)
        return paragraph_match if paragraph_match else ""

    def _extract_metadata(self, content, indicators):
        """Extract metadata items from content based on indicators"""
        items = []
        for indicator in indicators:
            match = self._first_match(content, f"{indicator}(.*?)(?:\n\n|\n#|\n\*\*|$)", re.DOTALL)
            if match:
                # Split by commas or new lines
                extracted_items = [item.strip() for item in re.split(r',|\n', match) if item.strip()]
                items.extend(extracted_items)
        return items

    def _extract_version(self, content):
        """Extract version information from content"""
        version_match = self._first_match(content, r'[Vv]ersion:?\s*(\d+\.\d+\.\d+|\d+\.\d+|\d+)')
        return version_match

    def _first_match(self, text, pattern, flags=0):
        """Return the first match group or None"""
        import re
        match = re.search(pattern, text, flags)
        return match.group(1).strip() if match else None

    def _scan_primary_directories(self):
        """Scan the main README.md to extract all recipes"""
        print("Scanning repository for integration recipes...")

        # Get the main README.md from Recipes directory
        readme_path = "Recipes/readme.md"
        readme_content = self._fetch_file_content(readme_path)

        if not readme_content:
            print(f"Error: Could not find main README at {readme_path}")
            return []

        all_content = []

        # Parse recipe tables from the README
        # Each table has format: Recipe|Description|Author
        recipe_tables = re.findall(r'Recipe\|Description\|Author\s*\n[-|]+\s*\n([\s\S]+?)(?:\n\n|\n\*\*\*|\n#|$)', readme_content)

        for table_content in recipe_tables:
            # Process each row in the table
            rows = table_content.strip().split('\n')
            for row in rows:
                parts = row.split('|')
                if len(parts) >= 3:
                    # Extract recipe name, link, and description
                    recipe_part = parts[0].strip()
                    description = parts[1].strip()
                    author = parts[2].strip()

                    # Parse recipe link - format: [name](link)
                    recipe_match = re.search(r'\[(.*?)\]\((.*?)\)', recipe_part)

                    if recipe_match:
                        recipe_name = recipe_match.group(1)
                        recipe_link = recipe_match.group(2)
                        recipe_id = recipe_link.replace('/', '-')

                        # Extract topic from context
                        topic = self._extract_current_topic(readme_content, row)

                        # Create content item
                        content_item = {
                            "Id": recipe_id,
                            "Name": recipe_name,
                            "Description": description,
                            "Author": author,
                            "Topic": topic,
                            "Categories": [topic] if topic else [],
                            "Tags": self._extract_tags_from_description(description),
                            "ContentType": self._determine_content_type(recipe_name, description),
                            "Path": recipe_link,
                            "GitHubUrl": f"https://github.com/{self.repo_owner}/{self.repo_name}/tree/master/{recipe_link}"
                        }

                        all_content.append(content_item)
                        print(f"Found recipe: {recipe_name}")

        self.integration_content = all_content
        print(f"Scanned repository and found {len(all_content)} integration recipes")
        return all_content

    def _extract_current_topic(self, readme_content, current_row):
        """Extract the current topic section from the README"""
        # Find the position of the current row
        row_pos = readme_content.find(current_row)
        if row_pos == -1:
            return ""

        # Find the last heading before this position
        readme_before = readme_content[:row_pos]
        heading_matches = list(re.finditer(r'### (.*?)(?:\n|$)', readme_before))

        if heading_matches:
            last_heading = heading_matches[-1]
            return last_heading.group(1).strip()

        return ""

    def _extract_tags_from_description(self, description):
        """Extract potential tags from description"""
        # Look for key terms in description
        words = re.findall(r'\b[A-Z][a-zA-Z]+\b', description)
        return list(set([word for word in words if len(word) > 3]))

    def _determine_content_type(self, name, description):
        """Determine content type based on name and description"""
        name_lower = name.lower()
        desc_lower = description.lower()

        if "flow" in name_lower or "flow" in desc_lower:
            return "IntegrationFlow"
        elif "adapter" in name_lower or "adapter" in desc_lower:
            return "Adapter"
        elif "pattern" in name_lower or "pattern" in desc_lower:
            return "IntegrationPattern"
        else:
            return "IntegrationContent"

    def _process_directory(self, path, all_content):
        """Process a directory to find README.md and extract metadata"""
        contents = self._fetch_directory_contents(path)

        # Check if README.md exists
        readme_item = next((item for item in contents if item['name'] == 'README.md'), None)

        if readme_item:
            # Fetch and parse README content
            readme_content = self._fetch_file_content(readme_item['path'])
            content_item = self._parse_readme_content(readme_content, path)

            if content_item:
                all_content.append(content_item)

        # Process subdirectories
        for item in contents:
            if item['type'] == 'dir':
                self._process_directory(item['path'], all_content)

                # Rate limiting
                time.sleep(1)

    def search_discovery_content(self, search_term, content_type=None, page_size=20, skip=0):
        """
        Search for content in the integration content data

        Args:
            search_term (str): Search keyword(s)
            content_type (str, optional): Filter by content type
            page_size (int, optional): Number of results per page
            skip (int, optional): Number of results to skip (for pagination)

        Returns:
            dict: The search results
        """
        # Check if we need to scan the repository
        if not self.integration_content:
            print("Scanning repository for content...")
            self._scan_primary_directories()

        # Check if this search is in cache
        cache_key = f"{search_term}_{content_type}_{page_size}_{skip}"
        if cache_key in self.results_cache:
            return self.results_cache[cache_key]

        print(f"Searching for: {search_term} with content type: {content_type}")

        # Ensure search term is lowercase for case-insensitive matching
        search_term_lower = search_term.lower()
        search_terms = search_term_lower.split()

        matching_results = []

        for item in self.integration_content:
            # Skip if content type doesn't match
            if content_type and item.get("ContentType") != content_type:
                continue

            # Calculate a match score
            score = 0

            # Get lowercase versions of item fields for case-insensitive matching
            name_lower = item.get("Name", "").lower()
            desc_lower = item.get("Description", "").lower()
            tags_lower = [tag.lower() for tag in item.get("Tags", [])]
            categories_lower = [cat.lower() for cat in item.get("Categories", [])]

            # Check exact phrase in name (highest weight)
            if search_term_lower in name_lower:
                score += 10

            # Check for individual terms in name
            for term in search_terms:
                if term in name_lower:
                    score += 5

            # Check exact phrase in description
            if search_term_lower in desc_lower:
                score += 7

            # Check for individual terms in description
            for term in search_terms:
                if term in desc_lower:
                    score += 3

            # Check tags
            for tag in tags_lower:
                if search_term_lower in tag:
                    score += 5
                for term in search_terms:
                    if term in tag:
                        score += 2

            # Check categories
            for category in categories_lower:
                if search_term_lower in category:
                    score += 4
                for term in search_terms:
                    if term in category:
                        score += 2

            # Add to results if there's any match
            if score > 0:
                result_item = item.copy()
                result_item["_match_score"] = score
                matching_results.append(result_item)

        # Sort by match score
        matching_results.sort(key=lambda x: x["_match_score"], reverse=True)

        # Apply pagination
        paginated_results = matching_results[skip:skip + page_size]

        # Format the response
        response = {
            "value": paginated_results
        }

        # Cache the result
        self.results_cache[cache_key] = response

        print(f"Found {len(paginated_results)} matches for '{search_term}' with content type '{content_type}'")

        return response

    def get_content_details(self, content_id):
        """
        Get detailed information about a specific integration content

        Args:
            content_id (str): The ID of the content to retrieve

        Returns:
            dict: The content details
        """
        # Check if we need to scan the repository
        if not self.integration_content:
            print("Scanning repository for content...")
            self._scan_primary_directories()

        # Check if this content is in cache
        cache_key = f"details_{content_id}"
        if cache_key in self.results_cache:
            return self.results_cache[cache_key]

        # Find the content by ID
        for item in self.integration_content:
            if item.get("Id") == content_id:
                # Get the README content
                try:
                    path = item.get("Path")
                    readme_path = f"{path}/README.md"
                    readme_content = self._fetch_file_content(readme_path)

                    # Add the README content to the item
                    detailed_item = item.copy()
                    detailed_item["ReadmeContent"] = readme_content

                    # Cache the result
                    self.results_cache[cache_key] = detailed_item

                    return detailed_item
                except Exception as e:
                    print(f"Error fetching README for content {content_id}: {e}")
                    return item

        return None

    def execute_search_strategy(self, search_terms, content_types=None):
        """
        Execute the search strategy using different priority levels of search terms

        Args:
            search_terms (dict): Dictionary with prioritized search terms
            content_types (list, optional): List of content types to search

        Returns:
            dict: Combined search results with metadata
        """
        # Check if GitHub token is available
        if not self.github_token:
            print("INFO:Accessing SAP Integration Suite Knowledge Hub...")
            # Continue execution - public repository doesn't require token

        if content_types is None:
            content_types = ["IntegrationFlow", "IntegrationPattern", "Adapter"]

        all_results = {}
        result_sources = {}  # Track which search term found each result

        # Search with primary terms (most specific)
        for term in search_terms.get('primary', []):
            for content_type in content_types:
                results = self.search_discovery_content(term, content_type)
                if results and 'value' in results and results['value']:
                    for item in results['value']:
                        content_id = item.get('Id')
                        if content_id not in all_results:
                            all_results[content_id] = item
                            result_sources[content_id] = {'term': term, 'priority': 'primary'}

            # Rate limiting to avoid overwhelming the API
            time.sleep(0.1)

        # If we have few results, search with secondary terms
        if len(all_results) < 10:
            for term in search_terms.get('secondary', []):
                for content_type in content_types:
                    results = self.search_discovery_content(term, content_type)
                    if results and 'value' in results and results['value']:
                        for item in results['value']:
                            content_id = item.get('Id')
                            if content_id not in all_results:
                                all_results[content_id] = item
                                result_sources[content_id] = {'term': term, 'priority': 'secondary'}

                # Rate limiting
                time.sleep(0.1)

                # Stop if we have enough results
                if len(all_results) >= 20:
                    break

        # If we still have few results, search with tertiary terms
        if len(all_results) < 5:
            for term in search_terms.get('tertiary', [])[:5]:  # Only use top 5 tertiary terms
                for content_type in content_types:
                    results = self.search_discovery_content(term, content_type)
                    if results and 'value' in results and results['value']:
                        for item in results['value']:
                            content_id = item.get('Id')
                            if content_id not in all_results:
                                all_results[content_id] = item
                                result_sources[content_id] = {'term': term, 'priority': 'tertiary'}

                # Rate limiting
                time.sleep(0.1)

                # Stop if we have enough results
                if len(all_results) >= 20:
                    break

        return {
            'results': list(all_results.values()),
            'sources': result_sources,
            'total_count': len(all_results)
        }