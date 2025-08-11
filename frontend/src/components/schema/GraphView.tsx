import React, { useEffect, useRef, useState } from 'react';
import cytoscape, { Core, EdgeDefinition, NodeDefinition } from 'cytoscape';
import dagre from 'cytoscape-dagre';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { ZoomIn, ZoomOut, Maximize2, Search, Filter } from 'lucide-react';
import { cn } from '../../utils/cn';

// Register the dagre extension
cytoscape.use(dagre);

interface GraphNode {
  id: string;
  label: string;
  type: 'table' | 'column';
  columns?: number;
  metadata?: Record<string, any>;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  type: 'foreign_key' | 'relationship';
}

interface GraphViewProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedTable?: string;
  onTableSelect?: (tableName: string) => void;
  className?: string;
}

const GraphView: React.FC<GraphViewProps> = ({
  nodes,
  edges,
  selectedTable,
  onTableSelect,
  className
}) => {
  const cyRef = useRef<HTMLDivElement>(null);
  const cyInstanceRef = useRef<Core | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    if (!cyRef.current || nodes.length === 0) return;

    // Prepare nodes for Cytoscape
    const cyNodes: NodeDefinition[] = nodes.map(node => ({
      data: {
        id: node.id,
        label: node.label,
        type: node.type,
        columns: node.columns || 0,
        metadata: node.metadata || {}
      }
    }));

    // Prepare edges for Cytoscape
    const cyEdges: EdgeDefinition[] = edges.map(edge => ({
      data: {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label || '',
        type: edge.type
      }
    }));

    // Initialize Cytoscape
    const cy = cytoscape({
      container: cyRef.current,
      elements: [...cyNodes, ...cyEdges],
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'background-color': '#f1f5f9',
            'border-color': '#cbd5e1',
            'border-width': 2,
            'color': '#1e293b',
            'font-size': '12px',
            'font-weight': 'bold',
            'width': '120px',
            'height': '60px',
            'shape': 'roundrectangle',
            'text-wrap': 'wrap',
            'text-max-width': '100px'
          }
        },
        {
          selector: 'node[type="table"]',
          style: {
            'background-color': '#dbeafe',
            'border-color': '#3b82f6',
            'border-width': 3,
          }
        },
        {
          selector: 'node:selected',
          style: {
            'background-color': '#fef3c7',
            'border-color': '#f59e0b',
            'border-width': 4
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#64748b',
            'target-arrow-color': '#64748b',
            'target-arrow-shape': 'triangle',
            'arrow-scale': 1.2,
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'text-rotation': 'autorotate',
            'text-margin-y': -10,
            'color': '#64748b'
          }
        },
        {
          selector: 'edge[type="foreign_key"]',
          style: {
            'line-color': '#10b981',
            'target-arrow-color': '#10b981',
            'line-style': 'solid'
          }
        },
        {
          selector: 'edge:selected',
          style: {
            'width': 4,
            'line-color': '#f59e0b',
            'target-arrow-color': '#f59e0b'
          }
        }
      ],
      layout: {
        name: 'dagre',
        rankDir: 'TB',
        spacingFactor: 1.2,
        nodeSep: 50,
        edgeSep: 10,
        rankSep: 80
      },
      userZoomingEnabled: true,
      userPanningEnabled: true,
      boxSelectionEnabled: true,
      wheelSensitivity: 0.2
    });

    // Store reference
    cyInstanceRef.current = cy;

    // Event handlers
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const nodeId = node.data('id');
      const nodeType = node.data('type');
      
      if (nodeType === 'table' && onTableSelect) {
        onTableSelect(nodeId);
      }
      
      // Highlight connected nodes and edges
      cy.elements().removeClass('highlighted');
      node.addClass('highlighted');
      node.connectedEdges().addClass('highlighted');
      node.connectedEdges().connectedNodes().addClass('highlighted');
    });

    // Auto-select table if specified
    if (selectedTable) {
      const selectedNode = cy.getElementById(selectedTable);
      if (selectedNode.length > 0) {
        selectedNode.select();
        cy.center(selectedNode);
      }
    }

    // Cleanup function
    return () => {
      if (cyInstanceRef.current) {
        cyInstanceRef.current.destroy();
        cyInstanceRef.current = null;
      }
    };
  }, [nodes, edges, selectedTable, onTableSelect]);

  const handleZoomIn = () => {
    if (cyInstanceRef.current) {
      cyInstanceRef.current.zoom(cyInstanceRef.current.zoom() * 1.2);
    }
  };

  const handleZoomOut = () => {
    if (cyInstanceRef.current) {
      cyInstanceRef.current.zoom(cyInstanceRef.current.zoom() * 0.8);
    }
  };

  const handleFit = () => {
    if (cyInstanceRef.current) {
      cyInstanceRef.current.fit();
    }
  };

  const handleSearch = (term: string) => {
    setSearchTerm(term);
    
    if (!cyInstanceRef.current) return;
    
    if (!term.trim()) {
      // Reset highlighting
      cyInstanceRef.current.elements().removeClass('dimmed highlighted');
      return;
    }

    const cy = cyInstanceRef.current;
    
    // Find matching nodes
    const matchingNodes = cy.nodes().filter((node) => {
      const label = node.data('label').toLowerCase();
      return label.includes(term.toLowerCase());
    });

    if (matchingNodes.length > 0) {
      // Dim all elements first
      cy.elements().addClass('dimmed');
      
      // Highlight matching nodes and their connections
      matchingNodes.removeClass('dimmed').addClass('highlighted');
      matchingNodes.connectedEdges().removeClass('dimmed').addClass('highlighted');
      matchingNodes.connectedEdges().connectedNodes().removeClass('dimmed').addClass('highlighted');
      
      // Center on first match
      cy.center(matchingNodes.first());
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  return (
    <Card className={cn(
      "relative",
      isFullscreen && "fixed inset-0 z-50 rounded-none",
      className
    )}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle>Schema Relationships</CardTitle>
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search tables..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-8 w-48"
              />
            </div>
            <Button variant="outline" size="icon" onClick={handleZoomOut}>
              <ZoomOut className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={handleZoomIn}>
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={handleFit}>
              <Filter className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={toggleFullscreen}>
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        <div 
          ref={cyRef}
          className={cn(
            "w-full bg-background border-t border-border",
            isFullscreen ? "h-[calc(100vh-4rem)]" : "h-96"
          )}
          style={{ 
            minHeight: isFullscreen ? 'calc(100vh - 4rem)' : '400px'
          }}
        />
        
        {nodes.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <div className="mb-4">
                <svg className="mx-auto h-12 w-12 text-muted-foreground/50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 1.79 4 4 4h8c2.21 0 4-1.79 4-4V7c0-2.21-1.79-4-4-4H8c-2.21 0-4 1.79-4 4z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="m9 12 2 2 4-4" />
                </svg>
              </div>
              <p className="text-lg font-medium">No Schema Data</p>
              <p className="text-sm">Connect to a database to view table relationships</p>
            </div>
          </div>
        )}

        {/* Legend */}
        {nodes.length > 0 && (
          <div className="absolute top-4 left-4 bg-background/90 backdrop-blur-sm border border-border rounded-md p-3 text-xs space-y-2">
            <div className="font-semibold text-foreground mb-2">Legend</div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-blue-100 border-2 border-blue-500 rounded"></div>
              <span className="text-muted-foreground">Table</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-1 bg-green-500"></div>
              <span className="text-muted-foreground">Foreign Key</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-yellow-100 border-2 border-yellow-500 rounded"></div>
              <span className="text-muted-foreground">Selected</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default GraphView;