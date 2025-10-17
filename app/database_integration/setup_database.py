"""
Database Setup Script
Run this to set up your Supabase database with all required tables and functions
"""

import os
import sys
import logging
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_sql_file(file_path: str) -> str:
    """Read SQL file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read SQL file {file_path}: {str(e)}")
        return ""

def setup_database():
    """Set up the Supabase database with required schema"""
    
    # Get Supabase credentials
    url = os.getenv('SUPABASE_URL')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not service_role_key:
        logger.error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env file")
        return False
    
    try:
        # Create admin client (service role has full access)
        supabase = create_client(url, service_role_key)
        logger.info("Connected to Supabase successfully")
        
        # Read schema file
        schema_file = os.path.join(os.path.dirname(__file__), 'supabase_schema.sql')
        schema_sql = read_sql_file(schema_file)
        
        if not schema_sql:
            logger.error("Failed to read schema SQL file")
            return False
        
        # Execute the entire SQL script at once
        logger.info("Executing SQL schema...")

        try:
            # For Supabase, we need to execute the SQL directly in the SQL Editor
            # This script will show you what to run
            print("\n" + "="*60)
            print("COPY AND PASTE THE FOLLOWING SQL INTO YOUR SUPABASE SQL EDITOR:")
            print("="*60)
            print(schema_sql)
            print("="*60)
            print("\nAfter running the SQL in Supabase, press Enter to continue...")
            input()

            logger.info("✅ SQL schema should now be executed in Supabase")

        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            return False
        
        logger.info("✅ Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {str(e)}")
        return False

def test_database_setup():
    """Test the database setup by checking if tables exist"""
    
    url = os.getenv('SUPABASE_URL')
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not anon_key:
        logger.error("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
        return False
    
    try:
        # Create client
        supabase = create_client(url, anon_key)
        
        # Test tables
        tables_to_test = ['jobs', 'documents', 'user_feedback', 'job_history', 'user_activity']
        
        for table in tables_to_test:
            try:
                result = supabase.table(table).select('id').limit(1).execute()
                logger.info(f"✅ Table '{table}' is accessible")
            except Exception as e:
                logger.error(f"❌ Table '{table}' test failed: {str(e)}")
                return False
        
        # Test vector search function
        try:
            # This will fail if the function doesn't exist
            result = supabase.rpc('get_schema_version').execute()
            logger.info(f"✅ Schema version: {result.data}")
        except Exception as e:
            logger.warning(f"⚠️ Schema version check failed: {str(e)}")
        
        logger.info("✅ Database test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database test failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 IS-Migration Database Setup")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file with your Supabase credentials:")
        print("SUPABASE_URL=your_supabase_url")
        print("SUPABASE_ANON_KEY=your_anon_key")
        print("SUPABASE_SERVICE_ROLE_KEY=your_service_role_key")
        return
    
    # Load environment variables
    load_dotenv()
    
    print("1. Setting up database schema...")
    if setup_database():
        print("✅ Database schema setup completed!")
    else:
        print("❌ Database schema setup failed!")
        return
    
    print("\n2. Testing database setup...")
    if test_database_setup():
        print("✅ Database test completed!")
    else:
        print("❌ Database test failed!")
        return
    
    print("\n🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Install requirements: pip install -r database_integration/requirements.txt")
    print("2. Update your application to use the integrated_manager")
    print("3. Configure S3 credentials when ready")

if __name__ == "__main__":
    main()
