// Architecture data for D3.js diagram
const architectureData = {
    nodes: [
        // User Layer
        {
            id: 'users',
            title: 'Users',
            subtitle: 'Developers & Architects',
            category: 'user',
            x: 100,
            y: 200,
            width: 180,
            height: 80,
            description: 'Development teams using the migration platform to convert MuleSoft applications to SAP Integration Suite.',
            features: ['File Upload Interface', 'Progress Monitoring', 'Documentation Review', 'iFlow Deployment'],
            technologies: ['Web Browser', 'Mobile App'],
            color: '#3B82F6'
        },

        // Frontend Layer
        {
            id: 'frontend-app',
            title: 'Frontend App',
            subtitle: 'React.js Interface',
            category: 'frontend',
            x: 350,
            y: 120,
            width: 180,
            height: 80,
            description: 'Modern React.js application providing intuitive interface for MuleSoft migration workflow.',
            features: ['File Upload', 'Documentation Viewer', 'iFlow Generator', 'Deployment Dashboard', 'Progress Tracking'],
            technologies: ['React.js', 'Tailwind CSS', 'Axios', 'React Router'],
            color: '#10B981'
        },

        {
            id: 'api-gateway',
            title: 'API Gateway',
            subtitle: 'Cloud Foundry Router',
            category: 'frontend',
            x: 350,
            y: 250,
            width: 180,
            height: 80,
            description: 'Cloud Foundry application router handling API requests and load balancing.',
            features: ['Request Routing', 'Load Balancing', 'Authentication', 'Rate Limiting'],
            technologies: ['Cloud Foundry', 'Node.js', 'Express'],
            color: '#10B981'
        },

        // Backend Services
        {
            id: 'doc-api',
            title: 'Documentation API',
            subtitle: 'MuleSoft Parser',
            category: 'backend',
            x: 600,
            y: 100,
            width: 180,
            height: 80,
            description: 'Processes MuleSoft XML files and generates comprehensive documentation with AI enhancement.',
            features: ['XML Parsing', 'Documentation Generation', 'Markdown Export', 'HTML Conversion'],
            technologies: ['Python', 'Flask', 'BeautifulSoup', 'Jinja2'],
            color: '#F59E0B'
        },

        {
            id: 'matcher-api',
            title: 'SAP Matcher API',
            subtitle: 'Integration Finder',
            category: 'backend',
            x: 600,
            y: 200,
            width: 180,
            height: 80,
            description: 'Analyzes MuleSoft components and finds equivalent SAP Integration Suite patterns.',
            features: ['Component Analysis', 'Pattern Matching', 'Similarity Scoring', 'GitHub Integration'],
            technologies: ['Python', 'Flask', 'GitHub API', 'NLP Libraries'],
            color: '#F59E0B'
        },

        {
            id: 'iflow-generator',
            title: 'iFlow Generator',
            subtitle: 'AI-Powered Creation',
            category: 'backend',
            x: 600,
            y: 300,
            width: 180,
            height: 80,
            badge: 'AI',
            description: 'Generates SAP Integration Suite iFlows using AI based on MuleSoft application analysis.',
            features: ['AI-Powered Generation', 'Template Engine', 'Package Creation', 'Validation'],
            technologies: ['Python', 'Flask', 'Anthropic API', 'XML Processing'],
            color: '#F59E0B'
        },

        // Machine Learning Services
        {
            id: 'ml-pattern-matcher',
            title: 'ML Pattern Matcher',
            subtitle: 'NLTK + ML Engine',
            category: 'ai',
            x: 900,
            y: 150,
            width: 180,
            height: 80,
            description: 'Machine learning engine using NLTK for pattern matching and similarity analysis of MuleSoft components.',
            features: ['Pattern Recognition', 'Similarity Analysis', 'Component Classification', 'Match Scoring'],
            technologies: ['Python', 'NLTK', 'Scikit-learn', 'TensorFlow'],
            color: '#8B5CF6'
        },

        // Database
        {
            id: 'database',
            title: 'PostgreSQL DB',
            subtitle: 'Google Cloud Platform',
            category: 'database',
            x: 600,
            y: 450,
            width: 180,
            height: 80,
            description: 'PostgreSQL database hosted on Google Cloud Platform for data persistence and job management.',
            features: ['Job Management', 'Document Storage', 'User Sessions', 'System Metrics', 'Vector Storage'],
            technologies: ['PostgreSQL', 'Google Cloud SQL', 'Connection Pooling'],
            color: '#EF4444'
        },

        // External Services
        {
            id: 'github-api',
            title: 'GitHub API',
            subtitle: 'Repository Access',
            category: 'external',
            x: 1200,
            y: 150,
            width: 180,
            height: 80,
            description: 'GitHub API integration for accessing SAP Integration Suite sample repositories.',
            features: ['Repository Scanning', 'File Access', 'Pattern Matching', 'Authentication'],
            technologies: ['GitHub REST API', 'OAuth', 'Git'],
            color: '#6B7280'
        },

        {
            id: 'anthropic-api-docs',
            title: 'Anthropic API (Docs)',
            subtitle: 'Claude AI - Documentation',
            category: 'external',
            x: 1200,
            y: 250,
            width: 180,
            height: 80,
            description: 'Anthropic Claude API for AI-powered documentation generation and enhancement.',
            features: ['Natural Language Processing', 'Code Analysis', 'Documentation Generation', 'Content Enhancement'],
            technologies: ['Anthropic API', 'Claude 3', 'REST API'],
            color: '#6B7280'
        },

        {
            id: 'anthropic-api-iflow',
            title: 'Anthropic API (iFlow)',
            subtitle: 'Claude AI - iFlow Generation',
            category: 'external',
            x: 1200,
            y: 400,
            width: 180,
            height: 80,
            description: 'Anthropic Claude API for AI-powered iFlow generation based on documentation.',
            features: ['iFlow Generation', 'XML Processing', 'Integration Patterns', 'Code Generation'],
            technologies: ['Anthropic API', 'Claude 3', 'REST API'],
            color: '#6B7280'
        },

        // Generated Document (Intermediate Output)
        {
            id: 'generated-document',
            title: 'Generated Document',
            subtitle: 'Documentation Output',
            category: 'backend',
            x: 900,
            y: 250,
            width: 180,
            height: 80,
            description: 'AI-generated documentation from MuleSoft code analysis, used for similarity search and iFlow generation.',
            features: ['Structured Documentation', 'Component Analysis', 'Flow Description', 'Technical Specifications'],
            technologies: ['Markdown', 'JSON', 'Technical Documentation'],
            color: '#F59E0B'
        },

        // iFlow Code (Generated Output)
        {
            id: 'iflow-code',
            title: 'iFlow Code',
            subtitle: 'Generated Output',
            category: 'backend',
            x: 1200,
            y: 550,
            width: 180,
            height: 80,
            description: 'Generated iFlow XML code ready for deployment to SAP Integration Suite.',
            features: ['XML Structure', 'Component Configuration', 'Flow Logic', 'Parameter Mapping'],
            technologies: ['XML', 'SAP CPI Format', 'Integration Patterns'],
            color: '#F59E0B'
        },

        // SAP Integration Suite
        {
            id: 'sap-integration',
            title: 'SAP Integration Suite',
            subtitle: 'Target Platform',
            category: 'sap',
            x: 900,
            y: 650,
            width: 180,
            height: 80,
            badge: 'TARGET',
            description: 'SAP Integration Suite where generated iFlows are deployed and managed.',
            features: ['iFlow Deployment', 'Runtime Management', 'Monitoring', 'API Management'],
            technologies: ['SAP CPI', 'SAP API Management', 'Cloud Integration'],
            color: '#1E40AF'
        }
    ],

    connections: [
        // User to Frontend
        { source: 'users', target: 'frontend-app', type: 'standard' },

        // Frontend to API Gateway
        { source: 'frontend-app', target: 'api-gateway', type: 'standard' },

        // API Gateway to Backend Services
        { source: 'api-gateway', target: 'doc-api', type: 'standard' },
        { source: 'api-gateway', target: 'matcher-api', type: 'standard' },
        { source: 'api-gateway', target: 'iflow-generator', type: 'standard' },

        // STEP 1: Documentation API to Anthropic API (Generate documentation using GenAI)
        { source: 'doc-api', target: 'anthropic-api', type: 'ai-powered' },

        // STEP 2: Documentation API to SAP Matcher API (Pass generated documentation)
        { source: 'doc-api', target: 'matcher-api', type: 'data-flow' },

        // STEP 3: Documentation API to iFlow Generator (Pass generated documentation)
        { source: 'doc-api', target: 'iflow-generator', type: 'data-flow' },

        // STEP 4: SAP Matcher API to ML Pattern Matcher (Use docs for similarity search)
        { source: 'matcher-api', target: 'ml-pattern-matcher', type: 'ai-powered' },

        // STEP 5: ML Pattern Matcher to GitHub API (Repository access for pattern matching)
        { source: 'ml-pattern-matcher', target: 'github-api', type: 'standard' },

        // STEP 6: iFlow Generator to Anthropic API (Generate iFlow using GenAI + documentation)
        { source: 'iflow-generator', target: 'anthropic-api', type: 'ai-powered' },

        // STEP 7: Anthropic API to iFlow Code (Generated iFlow code output)
        { source: 'anthropic-api', target: 'iflow-code', type: 'deployment' },

        // STEP 8: iFlow Code to SAP Integration Suite (Deploy generated iFlow)
        { source: 'iflow-code', target: 'sap-integration', type: 'deployment' },

        // Backend to Database (data persistence)
        { source: 'doc-api', target: 'database', type: 'standard' },
        { source: 'matcher-api', target: 'database', type: 'standard' },
        { source: 'iflow-generator', target: 'database', type: 'standard' }
    ],

    layers: [
        { name: 'USER LAYER', x: 100, y: 80 },
        { name: 'FRONTEND LAYER', x: 350, y: 80 },
        { name: 'BACKEND SERVICES', x: 600, y: 80 },
        { name: 'AI SERVICES', x: 900, y: 80 },
        { name: 'EXTERNAL', x: 1200, y: 80 }
    ]
};
