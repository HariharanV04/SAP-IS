// D3.js Architecture Diagram Implementation
class ArchitectureDiagram {
    constructor() {
        this.svg = d3.select('#architecture-diagram');
        this.width = 1400;
        this.height = 800;
        this.selectedComponent = null;
        this.animationEnabled = true;
        
        this.initializeSVG();
        this.setupZoom();
        this.createDefinitions();
        this.render();
        this.setupEventListeners();
    }
    
    initializeSVG() {
        this.svg
            .attr('width', this.width)
            .attr('height', this.height)
            .attr('viewBox', `0 0 ${this.width} ${this.height}`);
            
        this.container = this.svg.append('g').attr('class', 'diagram-container');
    }
    
    setupZoom() {
        const zoom = d3.zoom()
            .scaleExtent([0.5, 3])
            .on('zoom', (event) => {
                this.container.attr('transform', event.transform);
            });
            
        this.svg.call(zoom);
        
        // Store zoom behavior for reset functionality
        this.zoomBehavior = zoom;
    }
    
    createDefinitions() {
        const defs = this.svg.append('defs');
        
        // Create gradients for different component categories
        const gradients = [
            { id: 'userGradient', colors: ['#3B82F6', '#1E40AF'] },
            { id: 'frontendGradient', colors: ['#10B981', '#047857'] },
            { id: 'backendGradient', colors: ['#F59E0B', '#D97706'] },
            { id: 'aiGradient', colors: ['#8B5CF6', '#7C3AED'] },
            { id: 'databaseGradient', colors: ['#EF4444', '#DC2626'] },
            { id: 'externalGradient', colors: ['#6B7280', '#4B5563'] },
            { id: 'sapGradient', colors: ['#1E3A8A', '#1E40AF'] }
        ];
        
        gradients.forEach(grad => {
            const gradient = defs.append('linearGradient')
                .attr('id', grad.id)
                .attr('x1', '0%').attr('y1', '0%')
                .attr('x2', '100%').attr('y2', '100%');
                
            gradient.append('stop')
                .attr('offset', '0%')
                .attr('stop-color', grad.colors[0]);
                
            gradient.append('stop')
                .attr('offset', '100%')
                .attr('stop-color', grad.colors[1]);
        });
        
        // Create arrow markers
        const markers = [
            { id: 'arrowhead', color: '#64748b' },
            { id: 'arrowheadAI', color: '#8b5cf6' },
            { id: 'arrowheadDeploy', color: '#059669' }
        ];
        
        markers.forEach(marker => {
            defs.append('marker')
                .attr('id', marker.id)
                .attr('viewBox', '0 0 10 10')
                .attr('refX', 9)
                .attr('refY', 3)
                .attr('markerWidth', 6)
                .attr('markerHeight', 6)
                .attr('orient', 'auto')
                .append('path')
                .attr('d', 'M0,0 L0,6 L9,3 z')
                .attr('fill', marker.color);
        });
    }
    
    render() {
        this.renderTitle();
        this.renderLayers();
        this.renderConnections();
        this.renderComponents();
        this.renderLegend();
    }
    
    renderTitle() {
        this.container.append('text')
            .attr('x', this.width / 2)
            .attr('y', 40)
            .attr('text-anchor', 'middle')
            .attr('class', 'diagram-title')
            .style('font-size', '28px')
            .style('font-weight', 'bold')
            .style('fill', '#1F2937')
            .text('MuleSoft to SAP Integration Suite - AI-Powered Migration Architecture');
    }
    
    renderLayers() {
        const layerLabels = this.container.selectAll('.layer-label')
            .data(architectureData.layers)
            .enter()
            .append('text')
            .attr('class', 'layer-label')
            .attr('x', d => d.x + 90)
            .attr('y', d => d.y)
            .text(d => d.name);
    }
    
    renderConnections() {
        const connections = this.container.selectAll('.connection')
            .data(architectureData.connections)
            .enter()
            .append('path')
            .attr('class', d => `connection ${d.type}`)
            .attr('d', d => this.createConnectionPath(d))
            .attr('marker-end', d => {
                switch(d.type) {
                    case 'ai-powered': return 'url(#arrowheadAI)';
                    case 'deployment': return 'url(#arrowheadDeploy)';
                    default: return 'url(#arrowhead)';
                }
            });
    }
    
    createConnectionPath(connection) {
        const source = architectureData.nodes.find(n => n.id === connection.source);
        const target = architectureData.nodes.find(n => n.id === connection.target);
        
        const sourceX = source.x + source.width;
        const sourceY = source.y + source.height / 2;
        const targetX = target.x;
        const targetY = target.y + target.height / 2;
        
        const midX = (sourceX + targetX) / 2;
        
        return `M ${sourceX} ${sourceY} Q ${midX} ${sourceY} ${midX} ${(sourceY + targetY) / 2} Q ${midX} ${targetY} ${targetX} ${targetY}`;
    }
    
    renderComponents() {
        const components = this.container.selectAll('.component')
            .data(architectureData.nodes)
            .enter()
            .append('g')
            .attr('class', 'component')
            .attr('transform', d => `translate(${d.x}, ${d.y})`)
            .on('click', (event, d) => this.selectComponent(d))
            .on('mouseenter', (event, d) => this.showTooltip(event, d))
            .on('mouseleave', () => this.hideTooltip());
        
        // Component rectangles
        components.append('rect')
            .attr('class', 'component-rect')
            .attr('width', d => d.width)
            .attr('height', d => d.height)
            .attr('fill', d => this.getGradientUrl(d.category));
        
        // Component titles
        components.append('text')
            .attr('class', 'component-text')
            .attr('x', d => d.width / 2)
            .attr('y', d => d.height / 2 - 8)
            .text(d => d.title);
        
        // Component subtitles
        components.append('text')
            .attr('class', 'component-subtitle')
            .attr('x', d => d.width / 2)
            .attr('y', d => d.height / 2 + 8)
            .text(d => d.subtitle);
        
        // Badges
        components.filter(d => d.badge)
            .append('circle')
            .attr('cx', d => d.width - 15)
            .attr('cy', 15)
            .attr('r', 12)
            .attr('fill', '#FCD34D');
            
        components.filter(d => d.badge)
            .append('text')
            .attr('class', 'badge')
            .attr('x', d => d.width - 15)
            .attr('y', 15)
            .attr('fill', '#92400E')
            .text(d => d.badge);
    }
    
    getGradientUrl(category) {
        const gradientMap = {
            'user': 'url(#userGradient)',
            'frontend': 'url(#frontendGradient)',
            'backend': 'url(#backendGradient)',
            'ai': 'url(#aiGradient)',
            'database': 'url(#databaseGradient)',
            'external': 'url(#externalGradient)',
            'sap': 'url(#sapGradient)'
        };
        return gradientMap[category] || 'url(#backendGradient)';
    }
    
    renderLegend() {
        const legend = this.container.append('g')
            .attr('class', 'legend')
            .attr('transform', 'translate(50, 650)');
        
        // Legend background
        legend.append('rect')
            .attr('width', 300)
            .attr('height', 120)
            .attr('rx', 8)
            .attr('fill', 'white')
            .attr('stroke', '#E5E7EB')
            .attr('stroke-width', 1);
        
        // Legend title
        legend.append('text')
            .attr('x', 15)
            .attr('y', 25)
            .style('font-size', '14px')
            .style('font-weight', 'bold')
            .style('fill', '#1F2937')
            .text('Data Flow Legend');
        
        // Legend items
        const legendItems = [
            { type: 'standard', color: '#64748b', label: 'Standard Data Flow', y: 45 },
            { type: 'ai-powered', color: '#8b5cf6', label: 'AI-Powered Processing', y: 65 },
            { type: 'deployment', color: '#059669', label: 'Deployment Pipeline', y: 85 }
        ];
        
        legendItems.forEach(item => {
            legend.append('line')
                .attr('x1', 15)
                .attr('y1', item.y)
                .attr('x2', 65)
                .attr('y2', item.y)
                .attr('stroke', item.color)
                .attr('stroke-width', item.type === 'standard' ? 2 : 3)
                .attr('stroke-dasharray', item.type !== 'standard' ? '8,4' : null);
                
            legend.append('text')
                .attr('x', 75)
                .attr('y', item.y + 4)
                .style('font-size', '12px')
                .style('fill', item.color)
                .text(item.label);
        });
        
        legend.append('text')
            .attr('x', 15)
            .attr('y', 110)
            .style('font-size', '10px')
            .style('fill', '#6B7280')
            .text('Click components for detailed information');
    }
    
    selectComponent(component) {
        // Remove previous selection
        this.container.selectAll('.component').classed('selected', false);
        
        // Add selection to clicked component
        this.container.selectAll('.component')
            .filter(d => d.id === component.id)
            .classed('selected', true);
        
        this.selectedComponent = component;
        this.showComponentDetails(component);
    }
    
    showComponentDetails(component) {
        const detailsPanel = document.getElementById('component-details');
        const title = document.getElementById('details-title');
        const description = document.getElementById('details-description');
        const featuresDiv = document.getElementById('details-features');
        const technologiesDiv = document.getElementById('details-technologies');
        
        title.textContent = component.title;
        description.textContent = component.description;
        
        // Features
        featuresDiv.innerHTML = '<h4>Key Features:</h4><ul>' + 
            component.features.map(feature => `<li>${feature}</li>`).join('') + 
            '</ul>';
        
        // Technologies
        technologiesDiv.innerHTML = '<h4>Technologies:</h4><div class="tech-tags">' +
            component.technologies.map(tech => `<span class="tech-tag">${tech}</span>`).join('') +
            '</div>';
        
        detailsPanel.classList.add('visible');
    }
    
    showTooltip(event, component) {
        const tooltip = document.getElementById('tooltip');
        tooltip.innerHTML = `<strong>${component.title}</strong><br>${component.subtitle}`;
        tooltip.style.left = (event.pageX + 10) + 'px';
        tooltip.style.top = (event.pageY - 10) + 'px';
        tooltip.classList.add('visible');
    }
    
    hideTooltip() {
        document.getElementById('tooltip').classList.remove('visible');
    }
    
    setupEventListeners() {
        // Reset zoom button
        document.getElementById('resetZoom').addEventListener('click', () => {
            this.svg.transition().duration(750).call(
                this.zoomBehavior.transform,
                d3.zoomIdentity
            );
        });
        
        // Toggle animation button
        document.getElementById('toggleAnimation').addEventListener('click', () => {
            this.animationEnabled = !this.animationEnabled;
            this.container.selectAll('.connection.ai-powered, .connection.deployment')
                .style('animation', this.animationEnabled ? null : 'none');
        });
        
        // Export SVG button
        document.getElementById('exportSVG').addEventListener('click', () => {
            this.exportSVG();
        });
        
        // Close details panel
        document.getElementById('close-details').addEventListener('click', () => {
            document.getElementById('component-details').classList.remove('visible');
            this.container.selectAll('.component').classed('selected', false);
        });
    }
    
    exportSVG() {
        const svgElement = document.getElementById('architecture-diagram');
        const serializer = new XMLSerializer();
        const svgString = serializer.serializeToString(svgElement);
        
        const blob = new Blob([svgString], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = 'mulesoft-sap-architecture.svg';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
    }
}

// Initialize the diagram when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ArchitectureDiagram();
});
