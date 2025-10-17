#!/bin/bash
echo "Installing dependencies for MuleToIS-API..."
echo

# Install basic dependencies
pip install flask==2.3.3 flask-cors==4.0.0 python-dotenv==1.0.0 anthropic==0.51.0 requests==2.31.0 werkzeug==2.3.7 waitress==2.1.2 tabulate==0.9.0

# Install dependencies that might require pre-built wheels
pip install --only-binary=:all: numpy==1.26.0
pip install --only-binary=:all: scikit-learn==1.3.2
pip install --only-binary=:all: matplotlib==3.8.0

# Install other dependencies
pip install beautifulsoup4==4.12.2 markdown==3.5.2 nltk==3.8.1 termcolor==2.3.0

# Install platform-specific dependencies
if [[ "$OSTYPE" != "win"* ]]; then
    pip install gunicorn==21.2.0
fi

echo
echo "Dependencies installation completed."
echo
echo "You can now run the API with: python app.py"
