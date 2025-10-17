import React, { useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
} from 'reactflow';
import { motion } from 'framer-motion';
import 'reactflow/dist/style.css';

import CustomNode from './CustomNode';
import { initialNodes, initialEdges } from '../data/architectureData';

const nodeTypes = {
  custom: CustomNode,
};

const ArchitectureDiagram = ({ selectedComponent, setSelectedComponent }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((event, node) => {
    setSelectedComponent(node.data);
  }, [setSelectedComponent]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
      className="h-[800px] w-full"
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
      >
        <Controls className="bg-white shadow-lg rounded-lg" />
        <MiniMap 
          className="bg-white shadow-lg rounded-lg"
          nodeColor={(node) => {
            switch (node.data.category) {
              case 'user': return '#3B82F6';
              case 'frontend': return '#10B981';
              case 'backend': return '#F59E0B';
              case 'ai': return '#8B5CF6';
              case 'database': return '#EF4444';
              case 'external': return '#6B7280';
              default: return '#9CA3AF';
            }
          }}
        />
        <Background color="#f1f5f9" gap={20} />
      </ReactFlow>
    </motion.div>
  );
};

export default ArchitectureDiagram;
