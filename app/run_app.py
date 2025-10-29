import os
import sys
import logging
import platform
from dotenv import load_dotenv
from app import app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "final"))

# Log important information for debugging
print("=== ENVIRONMENT AND PORT INFORMATION ===")
print(f"Platform: {platform.system()}")
for key, value in os.environ.items():
    if key in ['PORT', 'VCAP_APP_PORT', 'CF_INSTANCE_PORT']:
        print(f"{key}: {value}")
print("=====================================")

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "final", ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loaded environment variables from: {env_path}")
else:
    local_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(local_env_path):
        load_dotenv(local_env_path)
        print(f"Loaded environment variables from: {local_env_path}")
    else:
        print("No .env file found - relying on system environment variables")

# Check for API keys
openai_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")

print("\n\033[1;33m=== MuleSoft Documentation Generator ===\033[0m")
print(f"\033[1;36mPython Version:\033[0m {sys.version}")
print(f"\033[1;36mCurrent Directory:\033[0m {os.getcwd()}")
print(f"\033[1;36mScript Directory:\033[0m {os.path.dirname(os.path.abspath(__file__))}")

# Check API availability
print("\n\033[1;33m=== LLM Services Status ===\033[0m")
print(f"\033[1;36mOpenAI API Key:\033[0m {'✅ Available' if openai_key else '❌ Not Available'}")
print(f"\033[1;36mAnthropic API Key:\033[0m {'✅ Available' if anthropic_key else '❌ Not Available'}")
if not openai_key and not anthropic_key:
    print("\033[1;31mWARNING: No LLM API keys available. Documentation enhancement will not work!\033[0m")
    print("\033[1;31mTo enable enhancement, set OPENAI_API_KEY or ANTHROPIC_API_KEY in the .env file\033[0m")
print("\033[1;33m===========================\033[0m\n")

# Apply CORS to allow cross-origin requests
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Add a health check endpoint to the Flask app
@app.route('/health', methods=['GET'])
def app_health_check():
    return 'OK', 200

# Simple debug endpoint to check if app is running
@app.route('/_app_status', methods=['GET'])
def app_status():
    port = os.environ.get('PORT', 'Not set')
    vcap_port = os.environ.get('VCAP_APP_PORT', 'Not set')
    cf_port = os.environ.get('CF_INSTANCE_PORT', 'Not set')
    return {
        'status': 'running',
        'platform': platform.system(),
        'port_env': port,
        'vcap_app_port': vcap_port,
        'cf_instance_port': cf_port,
        'python_version': sys.version
    }

if __name__ == '__main__':
    # This is critical: Cloud Foundry sets the PORT environment variable
    # and expects the app to listen on that port
    PORT = int(os.getenv('PORT', 8080))
    
    logger.info("="*80)
    logger.info("Starting MuleSoft Documentation Generator API")
    logger.info(f"Running on port: {PORT}")
    logger.info("="*80)
    
    # Check if we're running on Windows
    is_windows = platform.system() == "Windows"
    
    # Print all environment variables for debugging
    for key, value in os.environ.items():
        if key.startswith('VCAP_') or key == 'PORT':
            logger.info(f"{key}: {value}")
    
    # Choose the appropriate server for the platform
    if is_windows:
        # On Windows, try to use Waitress
        try:
            from waitress import serve
            logger.info("Using Waitress WSGI server (Windows-compatible)")
            serve(app, host='0.0.0.0', port=PORT, threads=10)
        except ImportError:
            # Fall back to Flask's built-in server on Windows
            logger.warning("Waitress not found. Using Flask's development server.")
            app.run(host='0.0.0.0', port=PORT, debug=False)
    else:
        # On Linux/Unix (Cloud Foundry), try Gunicorn first, then Waitress
        try:
            # Check if we can import Gunicorn (Linux/Unix only)
            import gunicorn
            logger.info("Using Gunicorn for production deployment")
            os.system(f"gunicorn --bind 0.0.0.0:{PORT} --workers 4 app:app")
        except (ImportError, ModuleNotFoundError):
            # Try Waitress as fallback
            try:
                from waitress import serve
                logger.info("Using Waitress WSGI server for production deployment")
                serve(app, host='0.0.0.0', port=PORT, threads=10)
            except ImportError:
                # Last resort: Flask's built-in server
                logger.warning("No production WSGI server found. Using Flask's development server.")
                app.run(host='0.0.0.0', port=PORT, debug=False)

