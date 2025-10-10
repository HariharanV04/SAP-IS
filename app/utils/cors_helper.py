# cors_helper.py - Helper for enabling CORS in Flask app

import os
from flask import request

def enable_cors(app):
    """
    Enable CORS for the Flask application with settings appropriate for local development and Cloud Foundry
    """
    # Instead of using the Flask-CORS extension, we'll handle CORS manually
    # to avoid duplicate headers

    # Create a simple OPTIONS route handler for the root path
    @app.route('/', methods=['OPTIONS'])
    def options_root():
        return _build_cors_preflight_response()

    # Create a simple OPTIONS route handler for all other paths
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_path(path):
        return _build_cors_preflight_response()

    # Create a simple OPTIONS route handler for API paths
    @app.route('/api/<path:path>', methods=['OPTIONS'])
    def options_api(path):
        return _build_cors_preflight_response()

    # Helper function to build preflight response
    def _build_cors_preflight_response():
        response = app.make_default_options_response()
        _add_cors_headers(response)
        return response

    # Helper function to add CORS headers
    def _add_cors_headers(response):
        # Get the origin from the request
        origin = request.headers.get('Origin')
        print(f"DEBUG: Request origin: {origin}")
        print(f"DEBUG: Request method: {request.method}")

        # Get allowed origins from environment variables or use defaults
        dev_frontend_url = os.environ.get('DEV_FRONTEND_URL', 'http://localhost:5173')
        dev_frontend_url_alt = 'http://localhost:3000'  # Alternative port for different dev setups
        prod_frontend_url = os.environ.get('PROD_FRONTEND_URL', 'https://ifa-project.cfapps.eu10.hana.ondemand.com')

        # Check if CORS_ORIGIN is explicitly set
        if os.environ.get('CORS_ORIGIN'):
            # Parse the CORS_ORIGIN value - it might contain multiple origins separated by commas
            cors_origins = [origin.strip() for origin in os.environ.get('CORS_ORIGIN').split(',')]

            # If the request origin is in the allowed list, use it
            if origin and origin in cors_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
            # If the request has no origin or it's not in the allowed list, use the first one
            elif cors_origins:
                response.headers['Access-Control-Allow-Origin'] = cors_origins[0]
            # Fallback to * if no origins are specified
            else:
                response.headers['Access-Control-Allow-Origin'] = '*'

            # Make sure we still set the credentials header
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
            response.headers['Access-Control-Allow-Methods'] = 'GET, PUT, POST, DELETE, OPTIONS'
            
            # Only set credentials to true if origin is not wildcard
            origin_header = response.headers.get('Access-Control-Allow-Origin')
            if origin_header != '*' and origin_header is not None:
                response.headers['Access-Control-Allow-Credentials'] = 'true'
            else:
                # Remove credentials header if origin is wildcard
                response.headers.pop('Access-Control-Allow-Credentials', None)
                
            response.headers['Access-Control-Max-Age'] = '3600'  # Cache preflight response for 1 hour
            response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition, Content-Length, Content-Type'
            return response

        # List of allowed origins
        allowed_origins = [
            'http://localhost:5173',  # Vite dev server
            'http://localhost:5174',  # Alternative Vite port
            'http://localhost:3000',  # Alternative dev server
            dev_frontend_url,  # Local development
            prod_frontend_url  # Production frontend
        ]

        # Add any additional origins from environment variable
        additional_origins = os.environ.get('ADDITIONAL_CORS_ORIGINS', '')
        if additional_origins:
            for additional_origin in additional_origins.split(','):
                if additional_origin.strip():
                    allowed_origins.append(additional_origin.strip())

        # Set the appropriate CORS header based on the request origin
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            print(f"DEBUG: Set origin to: {origin}")
        else:
            # For development, allow localhost on any port
            if origin and 'localhost' in origin:
                response.headers['Access-Control-Allow-Origin'] = origin
                print(f"DEBUG: Allowed localhost origin: {origin}")
            else:
                # Check environment to determine default
                env = os.environ.get('FLASK_ENV', 'development')
                if env == 'production':
                    # Default to the production frontend if origin is not in the allowed list
                    response.headers['Access-Control-Allow-Origin'] = prod_frontend_url
                else:
                    # Default to the development frontend
                    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
                print(f"DEBUG: Used default origin")

        # Always set these headers
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
        response.headers['Access-Control-Allow-Methods'] = 'GET, PUT, POST, DELETE, OPTIONS'
        
        # Only set credentials to true if origin is not wildcard
        origin_header = response.headers.get('Access-Control-Allow-Origin')
        print(f"DEBUG: Checking origin header: '{origin_header}'")
        if origin_header != '*' and origin_header is not None:
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            print(f"DEBUG: Set credentials to 'true' for origin: '{origin_header}'")
        else:
            # Remove credentials header if origin is wildcard
            response.headers.pop('Access-Control-Allow-Credentials', None)
            print(f"DEBUG: Removed credentials header for wildcard origin")
            
        response.headers['Access-Control-Max-Age'] = '3600'  # Cache preflight response for 1 hour

        # Add Content-Disposition to the exposed headers for file downloads
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition, Content-Length, Content-Type'

        print(f"DEBUG: Final CORS headers:")
        print(f"  Access-Control-Allow-Origin: '{response.headers.get('Access-Control-Allow-Origin')}'")
        print(f"  Access-Control-Allow-Credentials: '{response.headers.get('Access-Control-Allow-Credentials')}'")
        print(f"  Request Origin: '{origin}'")
        print(f"  Request Method: '{request.method}'")

        return response

    # Add CORS headers to all responses
    @app.after_request
    def after_request(response):
        # Add CORS headers to every response
        _add_cors_headers(response)

        # For non-OPTIONS methods, ensure we have the right content type
        if request.method != 'OPTIONS':
            # If it's a JSON response, ensure proper content type
            if response.headers.get('Content-Type') is None:
                if response.get_json() is not None:
                    response.headers['Content-Type'] = 'application/json'

        return response

    return app
