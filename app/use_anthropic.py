import os
import sys
import logging
import importlib
from dotenv import load_dotenv

# Set up logging with more detail and color
logging.basicConfig(
    level=logging.INFO,
    format='\033[92m%(asctime)s - %(levelname)s\033[0m: \033[94m%(message)s\033[0m',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Ensure the root logger passes everything through
logging.getLogger().setLevel(logging.INFO)

# Add parent paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "final"))

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "final", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"\033[1;32mLoaded environment variables from: {env_path}\033[0m")
else:
    print("\033[1;33mNo .env file found - relying on system environment variables\033[0m")

# Check for API keys
openai_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")

print("\n\033[1;33m=== MuleSoft Documentation Generator (Anthropic) ===\033[0m")
print(f"\033[1;36mPython Version:\033[0m {sys.version}")
print(f"\033[1;36mCurrent Directory:\033[0m {os.getcwd()}")
print(f"\033[1;36mScript Directory:\033[0m {os.path.dirname(os.path.abspath(__file__))}")

# Check API availability
print("\n\033[1;33m=== LLM Services Status ===\033[0m")
print(f"\033[1;36mOpenAI API Key:\033[0m {'✅ Available' if openai_key else '❌ Not Available'}")
print(f"\033[1;36mAnthropic API Key:\033[0m {'✅ Available' if anthropic_key else '❌ Not Available'}")

if not anthropic_key:
    print("\033[1;31mWARNING: No Anthropic API key available. This script requires Anthropic!\033[0m")
    print("\033[1;31mTo enable enhancement, set ANTHROPIC_API_KEY in the .env file\033[0m")
    sys.exit(1)
    
print("\033[1;33m===========================\033[0m\n")

# Monkey patch the LLMDocumentationEnhancer class to use Anthropic
try:
    # First import the module - this is needed before we can modify it
    from final.mule_flow_documentation import LLMDocumentationEnhancer
    
    # Create a monkey-patched version of the initializer
    original_init = LLMDocumentationEnhancer.__init__
    
    def patched_init(self):
        self.service = 'anthropic'  # Force use of Anthropic
        print(f"\033[1;32mUsing Anthropic for LLM enhancement\033[0m")
        
        try:
            from documentation_enhancer import DocumentationEnhancer
            self.enhancer = DocumentationEnhancer(selected_service=self.service)
            logging.info(f"DocumentationEnhancer initialized with '{self.service}' service.")
        except Exception as e:
            logging.error(f"Error initializing DocumentationEnhancer: {str(e)}")
            logging.info("Falling back to default service.")
            self.enhancer = DocumentationEnhancer()
    
    # Replace the original __init__ with our patched version
    LLMDocumentationEnhancer.__init__ = patched_init
    print("\033[1;32mSuccessfully patched LLMDocumentationEnhancer to use Anthropic\033[0m")
    
except Exception as e:
    print(f"\033[1;31mFailed to patch LLMDocumentationEnhancer: {str(e)}\033[0m")
    sys.exit(1)

# Import and run the Flask app
try:
    from app import app
    
    print("\033[1;32mStarting Flask application with Anthropic model...\033[0m")
    
    # Run in debug mode but with reloader off to see all output
    app.run(debug=True, use_reloader=False, port=5001)  # Use different port to avoid conflicts
    
except Exception as e:
    print(f"\033[1;31mError starting application: {str(e)}\033[0m")
    import traceback
    traceback.print_exc() 