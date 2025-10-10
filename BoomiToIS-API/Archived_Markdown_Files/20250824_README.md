# Boomi to SAP Integration Suite (iFlow) Converter

A comprehensive tool for converting Boomi integration processes to SAP Integration Suite iFlow format.

## 🏗️ Project Structure

```
BoomiToIS-API/
├── 📁 Core Components/
│   ├── enhanced_genai_iflow_generator.py    # Main iFlow generator
│   ├── json_to_iflow_converter.py           # JSON to iFlow converter
│   ├── enhanced_iflow_templates.py          # iFlow templates
│   ├── bpmn_templates.py                    # BPMN templates
│   └── config_driven_generator.py           # Configuration-driven generator
├── 📁 API & Web Interface/
│   ├── app.py                               # Main Flask application
│   ├── iflow_generator_api.py               # API endpoints
│   └── cors_config.py                       # CORS configuration
├── 📁 Configuration & Validation/
│   ├── config_validation_engine.py          # Configuration validator
│   ├── config/                              # Configuration files
│   └── .env*                                # Environment files
├── 📁 Utils/
│   ├── run.py                               # Development server runner
│   ├── setup_dependencies.py                # Dependency setup
│   ├── nltk_setup.py                        # NLTK configuration
│   └── client.py                            # API client example
├── 📁 Specialized/
│   └── enhanced_prompt_generator.py         # Advanced prompt generation
├── 📁 Processing & Utilities/
│   ├── boomi_xml_processor.py               # Boomi XML processor
│   ├── iflow_fixer.py                       # iFlow XML fixer
│   └── sap_btp_integration.py               # SAP BTP integration
├── 📁 Deployment & Setup/
│   ├── direct_iflow_deployment.py           # Direct deployment
│   ├── deploy.*                              # Deployment scripts
│   └── setup.*                              # Setup scripts
├── 📁 Documentation/
│   ├── COMPONENT_MAPPING_REFERENCE.md       # Component mapping
│   ├── DEPLOYMENT_GUIDE.md                  # Deployment guide
│   ├── IMPLEMENTATION_SUMMARY.md            # Implementation summary
│   └── README_DEPLOYMENT.md                 # Deployment README
├── 📁 Archive/                              # Archived files
│   ├── test_results/                        # Old test results
│   ├── test_scripts/                        # Old test scripts
│   ├── debug_files/                         # Old debug files
│   ├── sample_files/                        # Old sample files
│   └── old_versions/                        # Old versions
└── 📁 Working Directories/
    ├── genai_debug/                         # Current debug files
    ├── genai_output/                        # Generated outputs
    ├── results/                             # Current results
    └── uploads/                             # File uploads
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- SAP Integration Suite access
- Boomi integration export

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Run the application
python app.py
```

### Usage

#### 1. Web Interface
- Start the Flask app: `python app.py` or `python utils/run.py`
- Access: `http://localhost:5000`
- Upload Boomi XML or JSON files
- Generate iFlow ZIP files

#### 2. Command Line
```bash
# Generate iFlow from JSON blueprint
python tools/iflow_generate_template.py --json blueprint.json --name MyFlow --out output/

# Convert Boomi XML to iFlow
python json_to_iflow_converter.py --input boomi.xml --output iflow.zip

# Test the API with a markdown file
python utils/client.py --markdown-file example.md --iflow-name MyFlow
```

#### 3. API Usage
```python
import requests

# Generate iFlow
response = requests.post('http://localhost:5000/api/generate', 
                        json={'blueprint': blueprint_data})
iflow_zip = response.content
```

## 🔧 Configuration

### Environment Variables
- `SAP_CLIENT_ID`: SAP BTP client ID
- `SAP_CLIENT_SECRET`: SAP BTP client secret
- `SAP_TENANT`: SAP BTP tenant
- `ANTHROPIC_API_KEY`: Anthropic API key (optional)

### Component Mapping
Edit `COMPONENT_MAPPING_REFERENCE.md` to customize component translations.

## 📊 Features

- ✅ **Boomi XML Processing**: Parse and analyze Boomi integration processes
- ✅ **iFlow Generation**: Create SAP Integration Suite compatible iFlows
- ✅ **Template System**: Flexible template-based generation
- ✅ **Validation**: Comprehensive iFlow validation and fixing
- ✅ **Deployment**: Direct deployment to SAP BTP
- ✅ **API Interface**: RESTful API for integration
- ✅ **Web UI**: User-friendly web interface

## 🧪 Testing

Test files and results are archived in `archive/test_results/` and `archive/test_scripts/`.

## 📚 Documentation

- **Component Mapping**: `COMPONENT_MAPPING_REFERENCE.md`
- **Deployment**: `DEPLOYMENT_GUIDE.md`
- **Implementation**: `IMPLEMENTATION_SUMMARY.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review archived test results
3. Create an issue with detailed information

---

**Last Updated**: August 2025
**Version**: 2.0.0
**Status**: Production Ready
