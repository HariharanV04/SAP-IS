import React from 'react';
import { Handle, Position } from 'reactflow';
import { motion } from 'framer-motion';
import { 
  User, 
  Monitor, 
  Server, 
  Database, 
  Brain, 
  Cloud, 
  FileText, 
  Zap,
  GitBranch,
  Settings
} from 'lucide-react';

const iconMap = {
  user: User,
  frontend: Monitor,
  backend: Server,
  database: Database,
  ai: Brain,
  cloud: Cloud,
  document: FileText,
  api: Zap,
  github: GitBranch,
  config: Settings,
};

const categoryColors = {
  user: 'from-blue-500 to-blue-600',
  frontend: 'from-green-500 to-green-600',
  backend: 'from-amber-500 to-amber-600',
  ai: 'from-purple-500 to-purple-600',
  database: 'from-red-500 to-red-600',
  external: 'from-gray-500 to-gray-600',
  sap: 'from-blue-700 to-blue-800',
};

const CustomNode = ({ data, selected }) => {
  const Icon = iconMap[data.icon] || Server;
  const colorClass = categoryColors[data.category] || 'from-gray-500 to-gray-600';

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.05 }}
      className={`
        relative px-4 py-3 rounded-xl shadow-lg cursor-pointer
        bg-gradient-to-br ${colorClass}
        text-white min-w-[180px] max-w-[220px]
        border-2 ${selected ? 'border-yellow-400' : 'border-white/20'}
        transition-all duration-200
      `}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="w-3 h-3 bg-white/80 border-2 border-gray-300"
      />
      
      <div className="flex items-center space-x-3">
        <div className="flex-shrink-0">
          <Icon size={24} className="text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-bold text-white truncate">
            {data.title}
          </h3>
          <p className="text-xs text-white/80 mt-1 line-clamp-2">
            {data.subtitle}
          </p>
        </div>
      </div>

      {data.badge && (
        <div className="absolute -top-2 -right-2 bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded-full">
          {data.badge}
        </div>
      )}

      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 bg-white/80 border-2 border-gray-300"
      />
    </motion.div>
  );
};

export default CustomNode;
