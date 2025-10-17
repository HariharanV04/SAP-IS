# MuleSoft to SAP Integration Suite - D3.js Architecture Diagram

An interactive D3.js visualization showcasing the architecture for migrating MuleSoft applications to SAP Integration Suite using AI-powered tools.

## Features

- **Interactive Components**: Click on any component to see detailed information
- **Smooth Animations**: Animated data flow connections showing AI processing and deployment
- **Zoom & Pan**: Navigate the diagram with mouse controls
- **Component Details Panel**: Slide-out panel with comprehensive component information
- **Export Functionality**: Export the diagram as SVG
- **Responsive Design**: Works on desktop and mobile devices
- **Professional Styling**: Clean, modern design suitable for presentations

## Architecture Overview

### User Layer
- **Users**: Developers and architects using the migration platform

### Frontend Layer
- **Frontend App**: React.js interface for file upload and workflow management
- **API Gateway**: Cloud Foundry router for request handling

### Backend Services
- **Documentation API**: Processes MuleSoft XML files and generates documentation
- **SAP Matcher API**: Finds equivalent SAP Integration Suite patterns
- **iFlow Generator**: AI-powered creation of SAP iFlows

### AI Services (Production Ready)
- **SAP AI Core**: Foundation models and AI services for production deployment
- **Generative AI Hub**: AI orchestration and prompt management

### Data & External Services
- **PostgreSQL DB**: Google Cloud Platform hosted database
- **GitHub API**: Access to SAP Integration Suite samples
- **Anthropic API**: Claude AI for documentation and iFlow generation
- **SAP Integration Suite**: Target deployment platform

## Getting Started

### Option 1: Simple HTTP Server (Python)
```bash
cd d3-diagram
python -m http.server 8000
```
Then open: http://localhost:8000

### Option 2: Live Server (Node.js)
```bash
cd d3-diagram
npm install
npm run serve
```
Then open: http://localhost:8080

### Option 3: Direct File Access
Simply open `index.html` in your web browser (some features may be limited due to CORS restrictions).

## Usage

### Interactive Features
1. **Component Selection**: Click any component to see detailed information in the side panel
2. **Zoom Controls**: 
   - Mouse wheel to zoom in/out
   - Drag to pan around the diagram
   - "Reset View" button to return to original position
3. **Animation Toggle**: Turn on/off animated data flow connections
4. **Export**: Download the diagram as an SVG file

### Data Flow Types
- **Standard Flow** (Gray): Regular data processing and API calls
- **AI-Powered Flow** (Purple): AI-enhanced processing using SAP AI Core and Anthropic API
- **Deployment Flow** (Green): Direct deployment to SAP Integration Suite

## Customization

### Adding New Components
Edit `data.js` to add new nodes:

```javascript
{
    id: 'new-component',
    title: 'Component Name',
    subtitle: 'Component Description',
    category: 'backend', // user, frontend, backend, ai, database, external, sap
    x: 100,
    y: 100,
    width: 180,
    height: 80,
    description: 'Detailed description...',
    features: ['Feature 1', 'Feature 2'],
    technologies: ['Tech 1', 'Tech 2'],
    color: '#F59E0B'
}
```

### Adding New Connections
Add to the connections array in `data.js`:

```javascript
{ 
    source: 'source-component-id', 
    target: 'target-component-id', 
    type: 'standard' // standard, ai-powered, deployment
}
```

### Styling
- **CSS**: Modify `styles.css` for visual styling
- **Colors**: Update gradient definitions in `diagram.js`
- **Animations**: Adjust CSS animations in `styles.css`

## Technical Details

### Dependencies
- **D3.js v7**: Core visualization library
- **Modern Browser**: Supports ES6+ features

### Browser Compatibility
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

### Performance
- Optimized for up to 50 components
- Smooth animations at 60fps
- Responsive design for various screen sizes

## File Structure
```
d3-diagram/
├── index.html          # Main HTML file
├── styles.css          # CSS styling
├── diagram.js          # D3.js implementation
├── data.js             # Architecture data
├── package.json        # Dependencies
└── README.md           # This file
```

## Presentation Tips

1. **Full Screen**: Use F11 for full-screen presentation mode
2. **Component Focus**: Click components to highlight and show details
3. **Zoom for Detail**: Zoom in on specific areas during explanation
4. **Animation Control**: Toggle animations on/off as needed
5. **Export**: Save as SVG for inclusion in other presentations

## License

This project is licensed under the MIT License.

## Support

For questions or issues, please contact the development team at IT Resonance.
