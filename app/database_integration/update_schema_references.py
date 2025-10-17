"""
Script to update all table references in supabase_manager.py to use schema
"""

import re

def update_supabase_manager():
    """Update all table references to use schema"""
    
    file_path = 'database_integration/supabase_manager.py'
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace all table references
    replacements = [
        (r"self\.client\.table\('jobs'\)", "self._get_table('jobs')"),
        (r"self\.client\.table\('documents'\)", "self._get_table('documents')"),
        (r"self\.client\.table\('job_history'\)", "self._get_table('job_history')"),
        (r"self\.client\.table\('user_activity'\)", "self._get_table('user_activity')"),
        (r"self\.client\.table\('user_feedback'\)", "self._get_table('user_feedback')"),
        (r"self\.client\.table\('system_metrics'\)", "self._get_table('system_metrics')"),
        (r"self\.client\.table\('iflow_generations'\)", "self._get_table('iflow_generations')"),
    ]
    
    # Apply replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Update RPC calls to use schema
    content = re.sub(
        r"self\.client\.rpc\('search_documents'",
        f"self.client.rpc('{self.schema_name}.search_documents'",
        content
    )
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Updated all table references to use schema")

if __name__ == "__main__":
    update_supabase_manager()
