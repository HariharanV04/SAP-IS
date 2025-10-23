"""
Configuration file for Supabase Text Agent
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Supabase Configuration - Updated Service Role Key
# SUPABASE_URL = "https://jnoobtfelhtjfermohfx.supabase.co"
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impub29idGZlbGh0amZlcm1vaGZ4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTY3MTQyMiwiZXhwIjoyMDcxMjQ3NDIyfQ.RcMrsnsu9COzmeNgIJ3-tcn_LJhrcKFWMAAjA3uQVaU"

SUPABASE_URL ="https://csdzhpskeyqswqmffvxv.supabase.co"

SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNzZHpocHNrZXlxc3dxbWZmdnh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg0OTU5NzIsImV4cCI6MjA2NDA3MTk3Mn0.AmKTGFbDjFgnLIWnKBjBXELLgPrRkYV-pT7N-9apPvs"

# OpenAI Configuration - Updated API key
OPENAI_API_KEY = "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"

# Text Files Configuration
TEXT_FILES_DIRECTORY = os.getenv("TEXT_FILES_DIR", str(BASE_DIR / "text_files"))

# Agent Configuration
AGENT_MODEL = os.getenv("AGENT_MODEL", "gpt-4o-mini")  # Changed to gpt-4o-mini for better compatibility
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.1"))
AGENT_MAX_TOKENS = int(os.getenv("AGENT_MAX_TOKENS", "2000"))
AGENT_STREAM = os.getenv("AGENT_STREAM", "false").lower() == "true"  # Disable streaming by default

# Database Query Configuration
MAX_QUERY_RESULTS = int(os.getenv("MAX_QUERY_RESULTS", "10"))
MAX_TEXT_MATCHES = int(os.getenv("MAX_TEXT_MATCHES", "10"))

# Database Configuration (for RAG + Knowledge Graph) 
POSTGRES_URL = "postgresql://postgres:Vamsikrishna@2003@db.jnoobtfelhtjfermohfx.supabase.co:5432/postgres"

# Neo4j Configuration - Updated credentials
NEO4J_URI='neo4j+s://a09ee8ee.databases.neo4j.io' 
NEO4J_USER='neo4j'  # Changed from NEO4J_USERNAME to NEO4J_USER
NEO4J_USERNAME='neo4j'  # Keep for backward compatibility
NEO4J_PASSWORD='X1hAOjlDuAPAMLE3cA7inKb5RQL6JHKeJeV57hKQ_YY'
NEO4J_DATABASE='neo4j'
AURA_INSTANCEID='a09ee8ee' 
AURA_INSTANCENAME='CompleteKG'

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
VERBOSE_AGENT = os.getenv("VERBOSE_AGENT", "false").lower() == "true"
