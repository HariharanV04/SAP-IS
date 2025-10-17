export const initialNodes = [
  // User Layer
  {
    id: '1',
    type: 'custom',
    position: { x: 50, y: 180 },
    data: {
      title: 'Users',
      subtitle: 'Developers & Architects',
      category: 'user',
      icon: 'user',
      description: 'Development teams using the migration platform to convert MuleSoft applications to SAP Integration Suite.',
      features: ['File Upload Interface', 'Progress Monitoring', 'Documentation Review', 'iFlow Deployment'],
      technologies: ['Web Browser', 'Mobile App']
    },
  },

  // Frontend Layer
  {
    id: '2',
    type: 'custom',
    position: { x: 200, y: 180 },
    data: {
      title: 'Frontend App',
      subtitle: 'React.js Interface',
      category: 'frontend',
      icon: 'frontend',
      description: 'Modern React.js application providing intuitive interface for MuleSoft migration workflow.',
      features: ['File Upload', 'Documentation Viewer', 'iFlow Generator', 'Deployment Dashboard', 'Progress Tracking'],
      technologies: ['React.js', 'Tailwind CSS', 'Axios', 'React Router']
    },
  },

  {
    id: '3',
    type: 'custom',
    position: { x: 200, y: 320 },
    data: {
      title: 'API Gateway',
      subtitle: 'Cloud Foundry Router',
      category: 'frontend',
      icon: 'api',
      description: 'Cloud Foundry application router handling API requests and load balancing.',
      features: ['Request Routing', 'Load Balancing', 'Authentication', 'Rate Limiting'],
      technologies: ['Cloud Foundry', 'Node.js', 'Express']
    },
  },

  // Backend Services
  {
    id: '4',
    type: 'custom',
    position: { x: 400, y: 60 },
    data: {
      title: 'Documentation API',
      subtitle: 'MuleSoft Parser',
      category: 'backend',
      icon: 'document',
      description: 'Processes MuleSoft XML files and generates comprehensive documentation with AI enhancement.',
      features: ['XML Parsing', 'Documentation Generation', 'Markdown Export', 'HTML Conversion'],
      technologies: ['Python', 'Flask', 'BeautifulSoup', 'Jinja2']
    },
  },

  {
    id: '5',
    type: 'custom',
    position: { x: 400, y: 240 },
    data: {
      title: 'SAP Matcher API',
      subtitle: 'Integration Finder',
      category: 'backend',
      icon: 'api',
      description: 'Analyzes MuleSoft components and finds equivalent SAP Integration Suite patterns.',
      features: ['Component Analysis', 'Pattern Matching', 'Similarity Scoring', 'GitHub Integration'],
      technologies: ['Python', 'Flask', 'GitHub API', 'NLP Libraries']
    },
  },

  {
    id: '6',
    type: 'custom',
    position: { x: 400, y: 320 },
    data: {
      title: 'iFlow Generator',
      subtitle: 'AI-Powered Creation',
      category: 'backend',
      icon: 'api',
      badge: 'AI',
      description: 'Generates SAP Integration Suite iFlows using AI based on MuleSoft application analysis.',
      features: ['AI-Powered Generation', 'Template Engine', 'Package Creation', 'Validation'],
      technologies: ['Python', 'Flask', 'Anthropic API', 'XML Processing']
    },
  },

  // Machine Learning Services
  {
    id: '7',
    type: 'custom',
    position: { x: 600, y: 240 },
    data: {
      title: 'ML Pattern Matcher',
      subtitle: 'NLTK + ML Engine',
      category: 'ai',
      icon: 'ai',
      description: 'Machine learning engine using NLTK for pattern matching and similarity analysis of MuleSoft components.',
      features: ['Pattern Recognition', 'Similarity Analysis', 'Component Classification', 'Match Scoring'],
      technologies: ['Python', 'NLTK', 'Scikit-learn', 'TensorFlow']
    },
  },

  // Database
  {
    id: '8',
    type: 'custom',
    position: { x: 550, y: 460 },
    data: {
      title: 'PostgreSQL DB',
      subtitle: 'Google Cloud Platform',
      category: 'database',
      icon: 'database',
      description: 'PostgreSQL database hosted on Google Cloud Platform for data persistence and job management.',
      features: ['Job Management', 'Document Storage', 'User Sessions', 'System Metrics', 'Vector Storage'],
      technologies: ['PostgreSQL', 'Google Cloud SQL', 'Connection Pooling']
    },
  },

  // External Services
  {
    id: '9',
    type: 'custom',
    position: { x: 800, y: 240 },
    data: {
      title: 'GitHub API',
      subtitle: 'Repository Access',
      category: 'external',
      icon: 'github',
      description: 'GitHub API integration for accessing SAP Integration Suite sample repositories.',
      features: ['Repository Scanning', 'File Access', 'Pattern Matching', 'Authentication'],
      technologies: ['GitHub REST API', 'OAuth', 'Git']
    },
  },

  {
    id: '10',
    type: 'custom',
    position: { x: 600, y: 60 },
    data: {
      title: 'Anthropic API (Docs)',
      subtitle: 'Claude AI - Documentation',
      category: 'external',
      icon: 'ai',
      description: 'Anthropic Claude API for AI-powered documentation generation and enhancement.',
      features: ['Natural Language Processing', 'Code Analysis', 'Documentation Generation', 'Content Enhancement'],
      technologies: ['Anthropic API', 'Claude 3', 'REST API']
    },
  },

  {
    id: '11',
    type: 'custom',
    position: { x: 600, y: 320 },
    data: {
      title: 'Anthropic API (iFlow)',
      subtitle: 'Claude AI - iFlow Generation',
      category: 'external',
      icon: 'ai',
      description: 'Anthropic Claude API for AI-powered iFlow generation based on documentation.',
      features: ['iFlow Generation', 'XML Processing', 'Integration Patterns', 'Code Generation'],
      technologies: ['Anthropic API', 'Claude 3', 'REST API']
    },
  },

  // Generated Document (Intermediate Output)
  {
    id: '12',
    type: 'custom',
    position: { x: 800, y: 60 },
    data: {
      title: 'Generated Document',
      subtitle: 'Documentation Output',
      category: 'backend',
      icon: 'document',
      description: 'AI-generated documentation from MuleSoft code analysis, used for similarity search and iFlow generation.',
      features: ['Structured Documentation', 'Component Analysis', 'Flow Description', 'Technical Specifications'],
      technologies: ['Markdown', 'JSON', 'Technical Documentation']
    },
  },

  // iFlow Code (Generated Output)
  {
    id: '13',
    type: 'custom',
    position: { x: 800, y: 320 },
    data: {
      title: 'iFlow Code',
      subtitle: 'Generated Output',
      category: 'backend',
      icon: 'code',
      description: 'Generated iFlow XML code ready for deployment to SAP Integration Suite.',
      features: ['XML Structure', 'Component Configuration', 'Flow Logic', 'Parameter Mapping'],
      technologies: ['XML', 'SAP CPI Format', 'Integration Patterns']
    },
  },

  // SAP Integration Suite
  {
    id: '14',
    type: 'custom',
    position: { x: 1000, y: 320 },
    data: {
      title: 'SAP Integration Suite',
      subtitle: 'Target Platform',
      category: 'sap',
      icon: 'cloud',
      badge: 'TARGET',
      description: 'SAP Integration Suite where generated iFlows are deployed and managed.',
      features: ['iFlow Deployment', 'Runtime Management', 'Monitoring', 'API Management'],
      technologies: ['SAP CPI', 'SAP API Management', 'Cloud Integration']
    },
  },
];

export const initialEdges = [
  // User to Frontend
  { id: 'e1-2', source: '1', target: '2', type: 'smoothstep', animated: true },

  // Frontend to API Gateway
  { id: 'e2-3', source: '2', target: '3', type: 'smoothstep' },

  // API Gateway to Backend Services
  { id: 'e3-4', source: '3', target: '4', type: 'smoothstep' },
  { id: 'e3-5', source: '3', target: '5', type: 'smoothstep' },
  { id: 'e3-6', source: '3', target: '6', type: 'smoothstep' },

  // STEP 1: Documentation API to Anthropic API (Generate documentation using GenAI)
  { id: 'e4-10', source: '4', target: '10', type: 'smoothstep', animated: true, style: { stroke: '#8b5cf6', strokeWidth: 3 }, label: '1. Generate Docs' },

  // STEP 2: Anthropic API (Docs) to Generated Document
  { id: 'e10-12', source: '10', target: '12', type: 'smoothstep', animated: true, style: { stroke: '#059669', strokeWidth: 3 }, label: '2. Document Output' },

  // STEP 3: Generated Document to SAP Matcher API (Pass documentation)
  { id: 'e12-5', source: '12', target: '5', type: 'smoothstep', animated: true, style: { stroke: '#10b981', strokeWidth: 2 }, label: '3. Pass Docs' },

  // STEP 4: Generated Document to iFlow Generator (Pass documentation)
  { id: 'e12-6', source: '12', target: '6', type: 'smoothstep', animated: true, style: { stroke: '#10b981', strokeWidth: 2 }, label: '4. Pass Docs' },

  // STEP 5: SAP Matcher API to ML Pattern Matcher (Use docs for similarity search)
  { id: 'e5-7', source: '5', target: '7', type: 'smoothstep', animated: true, style: { stroke: '#f59e0b', strokeWidth: 3 }, label: '5. Similarity Search' },

  // STEP 6: ML Pattern Matcher to GitHub API (Repository access for pattern matching)
  { id: 'e7-9', source: '7', target: '9', type: 'smoothstep', style: { stroke: '#4b5563', strokeWidth: 2 }, label: '6. Repo Access' },

  // STEP 7: iFlow Generator to Anthropic API (iFlow) - Generate iFlow using documentation
  { id: 'e6-11', source: '6', target: '11', type: 'smoothstep', animated: true, style: { stroke: '#8b5cf6', strokeWidth: 3 }, label: '7. Generate iFlow' },

  // STEP 8: Anthropic API (iFlow) to iFlow Code (Generated iFlow code output)
  { id: 'e11-13', source: '11', target: '13', type: 'smoothstep', animated: true, style: { stroke: '#059669', strokeWidth: 3 }, label: '8. iFlow Code' },

  // STEP 9: iFlow Code to SAP Integration Suite (Deploy generated iFlow)
  { id: 'e13-14', source: '13', target: '14', type: 'smoothstep', animated: true, style: { stroke: '#059669', strokeWidth: 4 }, label: '9. Deploy iFlow' },

  // Backend to Database (data persistence)
  { id: 'e4-8', source: '4', target: '8', type: 'smoothstep' },
  { id: 'e5-8', source: '5', target: '8', type: 'smoothstep' },
  { id: 'e6-8', source: '6', target: '8', type: 'smoothstep' },
];
