"""
AI-Powered Documentation Refinement Agent
Uses feedback to continuously improve documentation and metadata quality
"""

import os
import json
from openai import OpenAI
from supabase import create_client
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, List, Tuple

# Initialize clients
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Load embedding model for similarity search
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


class DocumentationRefinementAgent:
    """
    AI Agent that learns from feedback to improve documentation quality
    """
    
    def __init__(self):
        self.embedding_cache = {}
        self.examples_cache = None
        
    def get_high_quality_examples(self, platform: str = 'boomi', limit: int = 10) -> List[Dict]:
        """
        Retrieve documentation examples that led to 5-star iFlow generation
        
        Args:
            platform: Source platform (boomi, mulesoft, sterling)
            limit: Number of examples to retrieve
            
        Returns:
            List of high-quality documentation examples
        """
        print(f"📚 Retrieving high-quality documentation examples for {platform}...")
        
        # Query feedback for successful conversions
        feedback = supabase.table('migration_feedback')\
            .select('job_id, source_file_name, overall_rating, documentation_quality_rating, what_worked_well')\
            .eq('source_platform', platform)\
            .gte('overall_rating', 4)\
            .gte('documentation_quality_rating', 4)\
            .eq('deployment_successful', True)\
            .order('overall_rating', desc=True)\
            .order('documentation_quality_rating', desc=True)\
            .limit(limit)\
            .execute()
        
        if not feedback.data:
            print(f"⚠️ No high-quality examples found for {platform}")
            return []
        
        print(f"✅ Found {len(feedback.data)} high-quality examples")
        
        # For each, retrieve the actual documentation
        examples = []
        for fb in feedback.data:
            # You'd retrieve from your doc storage
            # For now, placeholder structure
            examples.append({
                'job_id': fb['job_id'],
                'file_name': fb['source_file_name'],
                'rating': fb['overall_rating'],
                'what_worked': fb.get('what_worked_well', []),
                # 'documentation': get_documentation_by_job_id(fb['job_id'])
            })
        
        return examples
    
    def find_similar_examples(self, source_description: str, platform: str = 'boomi', top_k: int = 3) -> List[Dict]:
        """
        Find similar high-quality documentation examples using semantic search
        
        Args:
            source_description: Brief description of what the source file does
            platform: Source platform
            top_k: Number of similar examples to return
            
        Returns:
            Top-k most similar high-quality examples
        """
        print(f"🔍 Finding similar examples for: '{source_description[:100]}...'")
        
        # Get all high-quality examples
        if self.examples_cache is None:
            self.examples_cache = self.get_high_quality_examples(platform, limit=50)
        
        if not self.examples_cache:
            return []
        
        # Embed the query
        query_embedding = embedding_model.encode(source_description)
        
        # Embed all examples (cache for efficiency)
        similarities = []
        for example in self.examples_cache:
            cache_key = example['job_id']
            
            if cache_key not in self.embedding_cache:
                # Create searchable text from example
                example_text = f"{example['file_name']} {' '.join(example.get('what_worked', []))}"
                self.embedding_cache[cache_key] = embedding_model.encode(example_text)
            
            example_embedding = self.embedding_cache[cache_key]
            
            # Compute cosine similarity
            similarity = np.dot(query_embedding, example_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(example_embedding)
            )
            
            similarities.append((similarity, example))
        
        # Sort by similarity
        similarities.sort(reverse=True, key=lambda x: x[0])
        
        # Return top-k
        top_examples = [ex for _, ex in similarities[:top_k]]
        
        print(f"✅ Found {len(top_examples)} similar examples (similarity: {similarities[0][0]:.2f} - {similarities[min(top_k-1, len(similarities)-1)][0]:.2f})")
        
        return top_examples
    
    def generate_documentation_with_examples(
        self, 
        source_file_content: str,
        platform: str = 'boomi',
        source_description: str = None
    ) -> Dict:
        """
        Generate documentation using few-shot learning from high-quality examples
        
        Args:
            source_file_content: Raw content of source file
            platform: Source platform
            source_description: Optional brief description for finding similar examples
            
        Returns:
            Generated documentation with confidence score
        """
        print(f"📝 Generating documentation with AI-powered refinement...")
        
        # Find similar high-quality examples
        similar_examples = []
        if source_description:
            similar_examples = self.find_similar_examples(source_description, platform, top_k=3)
        
        # Build few-shot prompt
        examples_text = ""
        if similar_examples:
            examples_text = "\n\n🌟 EXAMPLES OF HIGH-QUALITY DOCUMENTATION (from 5-star conversions):\n\n"
            for i, ex in enumerate(similar_examples, 1):
                examples_text += f"Example {i} (⭐⭐⭐⭐⭐ rated):\n"
                examples_text += f"Source: {ex['file_name']}\n"
                examples_text += f"What worked well: {', '.join(ex.get('what_worked', ['N/A']))}\n"
                # examples_text += f"Documentation:\n{ex.get('documentation', 'N/A')}\n\n"
                examples_text += "---\n\n"
        
        # Enhanced prompt with examples
        prompt = f"""
You are an expert at analyzing {platform} integration files and creating comprehensive documentation.

{examples_text}

CRITICAL REQUIREMENTS (learned from user feedback):
1. **Component Identification**: Explicitly identify ALL components, especially:
   - Source adapters (SFTP, Mail, etc.)
   - Scheduling components (Timer for polling)
   - Target adapters (OData, SOAP, HTTP, SuccessFactors)
   - Transformation steps (GroovyScript, XSLT)

2. **Integration Pattern**: Clearly state the pattern (e.g., "Scheduled SFTP Polling → Transform → POST to OData")

3. **Data Flow**: Describe step-by-step data flow

4. **Business Logic**: Capture business rules and logic

5. **Configuration Details**: Include authentication, endpoints, polling intervals

6. **Error Handling**: Document exception handling if present

Now analyze this {platform} file and create documentation following the structure and quality of the examples above:

{source_file_content[:10000]}  # Limit to first 10k chars

Generate comprehensive documentation in markdown format.
"""
        
        # Generate documentation
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert integration documentation specialist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Lower temperature for consistency
        )
        
        documentation = response.choices[0].message.content
        
        print(f"✅ Documentation generated ({len(documentation)} chars)")
        
        return {
            'documentation': documentation,
            'used_examples': len(similar_examples),
            'confidence': 0.85 if similar_examples else 0.70
        }
    
    def generate_metadata_with_validation(
        self,
        documentation: str,
        platform: str = 'boomi'
    ) -> Dict:
        """
        Generate metadata from documentation with AI-powered validation
        
        Args:
            documentation: Generated documentation
            platform: Source platform
            
        Returns:
            Validated metadata with quality score
        """
        print(f"🔍 Generating metadata with validation...")
        
        # Get common issues from feedback
        common_issues = supabase.table('migration_feedback')\
            .select('missing_components')\
            .eq('source_platform', platform)\
            .lte('overall_rating', 3)\
            .limit(50)\
            .execute()
        
        # Aggregate most common missing components
        missing_components_freq = {}
        for fb in common_issues.data:
            for comp in fb.get('missing_components', []):
                missing_components_freq[comp] = missing_components_freq.get(comp, 0) + 1
        
        top_missing = sorted(missing_components_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Build validation checklist
        validation_checklist = "\n".join([
            f"- {comp} (missed in {count} previous conversions)"
            for comp, count in top_missing
        ])
        
        # Enhanced metadata extraction prompt
        prompt = f"""
Extract metadata from this documentation with EXTRA ATTENTION to components that are commonly missed:

⚠️ COMMON MISSING COMPONENTS (from user feedback):
{validation_checklist}

Documentation:
{documentation}

Extract and return JSON with this structure:
{{
    "components": [
        {{
            "type": "component_type",
            "name": "component_name",
            "description": "what it does",
            "confidence": 0.0-1.0
        }}
    ],
    "integration_pattern": "pattern description",
    "data_flow": ["step1", "step2", ...],
    "business_logic": "key business rules",
    "validation_checks": [
        {{
            "check": "Timer component for polling?",
            "present": true/false,
            "confidence": 0.0-1.0
        }}
    ],
    "quality_score": 0.0-1.0
}}

Pay special attention to the commonly missed components listed above.
"""
        
        # Generate metadata
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert at extracting structured metadata from integration documentation."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        metadata = json.loads(response.choices[0].message.content)
        
        print(f"✅ Metadata extracted with {len(metadata.get('components', []))} components")
        print(f"   Quality score: {metadata.get('quality_score', 0):.2f}")
        
        return metadata
    
    def refine_with_feedback(
        self,
        documentation: str,
        metadata: Dict,
        feedback: Dict
    ) -> Tuple[str, Dict]:
        """
        Refine documentation and metadata based on user feedback
        
        Args:
            documentation: Original documentation
            metadata: Original metadata
            feedback: User feedback with issues
            
        Returns:
            Refined documentation and metadata
        """
        print(f"🔧 Refining documentation based on feedback...")
        
        # Build refinement prompt
        issues = "\n".join([
            f"- {issue}" for issue in feedback.get('what_needs_improvement', [])
        ])
        
        missing_components = "\n".join([
            f"- {comp}" for comp in feedback.get('missing_components', [])
        ])
        
        prompt = f"""
The following documentation was generated but received user feedback indicating issues:

ORIGINAL DOCUMENTATION:
{documentation}

ORIGINAL METADATA:
{json.dumps(metadata, indent=2)}

USER FEEDBACK:
Issues reported:
{issues}

Missing components:
{missing_components}

Overall rating: {feedback.get('overall_rating', 0)}/5
Documentation rating: {feedback.get('documentation_quality_rating', 0)}/5

Please refine the documentation and metadata to address these issues. Focus on:
1. Adding missing components explicitly
2. Improving clarity where issues were reported
3. Ensuring all integration patterns are captured

Return JSON with:
{{
    "refined_documentation": "improved markdown documentation",
    "refined_metadata": {{ ... }},
    "improvements_made": ["improvement1", "improvement2", ...],
    "confidence": 0.0-1.0
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert at refining integration documentation based on user feedback."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        refined = json.loads(response.choices[0].message.content)
        
        print(f"✅ Documentation refined with {len(refined.get('improvements_made', []))} improvements")
        
        return refined['refined_documentation'], refined['refined_metadata']


# Example usage
if __name__ == "__main__":
    agent = DocumentationRefinementAgent()
    
    # Example: Generate documentation for a new file
    source_file = """
    <process>
        <component type="SFTP">
            <name>PollEmployeeFiles</name>
            <operation>GET</operation>
            <schedule>Every 5 minutes</schedule>
        </component>
        <component type="DataTransform">
            <script>transformEmployeeData.groovy</script>
        </component>
        <component type="HTTPAdapter">
            <operation>POST</operation>
            <endpoint>/sap/odata/EmployeeService</endpoint>
        </component>
    </process>
    """
    
    # Generate with AI
    result = agent.generate_documentation_with_examples(
        source_file_content=source_file,
        platform='boomi',
        source_description="Poll SFTP for employee files every 5 minutes, transform, and post to SAP OData"
    )
    
    print("\n" + "="*80)
    print("GENERATED DOCUMENTATION:")
    print("="*80)
    print(result['documentation'])
    
    # Generate metadata
    metadata = agent.generate_metadata_with_validation(
        documentation=result['documentation'],
        platform='boomi'
    )
    
    print("\n" + "="*80)
    print("GENERATED METADATA:")
    print("="*80)
    print(json.dumps(metadata, indent=2))


