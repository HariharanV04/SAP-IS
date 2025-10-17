# MuleSoft to SAP Integration Suite - Architecture Diagram

An interactive React.js application showcasing the architecture for migrating MuleSoft applications to SAP Integration Suite using AI-powered tools.

## Features

- **Interactive Architecture Diagram**: Click on components to see detailed information
- **Animated Data Flow**: Visual representation of data flow between components
- **Responsive Design**: Works on desktop and mobile devices
- **Presentation Ready**: Clean, professional design suitable for presentations
- **Component Details**: Detailed information about each architectural component

## Architecture Components

### Frontend Layer
- **Users**: Developers and architects using the migration platform
- **Frontend App**: React.js interface for file upload and workflow management
- **API Gateway**: Cloud Foundry router for request handling

### Backend Services
- **Documentation API**: Processes MuleSoft XML files and generates documentation
- **SAP Matcher API**: Finds equivalent SAP Integration Suite patterns
- **iFlow Generator**: AI-powered creation of SAP iFlows

### AI Services (Production)
- **SAP AI Core**: Foundation models and AI services for production
- **Generative AI Hub**: AI orchestration and prompt management

### Data & External Services
- **PostgreSQL DB**: Google Cloud Platform hosted database
- **GitHub API**: Access to SAP Integration Suite samples
- **Anthropic API**: Claude AI for documentation and iFlow generation
- **SAP Integration Suite**: Target deployment platform

## Getting Started

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd architecture-diagram
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Building for Production

```bash
npm run build
```

This builds the app for production to the `build` folder.

## Usage

1. **Interactive Exploration**: Click on any component in the diagram to see detailed information
2. **Zoom and Pan**: Use mouse wheel to zoom, drag to pan around the diagram
3. **Minimap**: Use the minimap in the bottom-right for navigation
4. **Controls**: Use the controls in the bottom-left for zoom and fit view

## Customization

### Adding New Components
Edit `src/data/architectureData.js` to add new nodes or modify existing ones:

```javascript
{
  id: 'new-component',
  type: 'custom',
  position: { x: 100, y: 100 },
  data: {
    title: 'Component Name',
    subtitle: 'Component Description',
    category: 'backend', // user, frontend, backend, ai, database, external, sap
    icon: 'server', // see CustomNode.js for available icons
    description: 'Detailed description...',
    features: ['Feature 1', 'Feature 2'],
    technologies: ['Tech 1', 'Tech 2']
  }
}
```

### Styling
- Modify `src/App.css` for global styles
- Edit `tailwind.config.js` for Tailwind CSS customization
- Update `src/components/CustomNode.js` for node styling

## Technologies Used

- **React.js**: Frontend framework
- **React Flow**: Interactive diagram library
- **Framer Motion**: Animation library
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Icon library

## License

This project is licensed under the MIT License.
