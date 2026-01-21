import { motion } from 'framer-motion';
import { MapPin, Clock, Users, AlertCircle } from 'lucide-react';

interface Incident {
  id: string;
  title: string;
  location: string;
  state?: string;
  date: string;
  fatalities: number;
  type: string;
  severity: 'Criminal' | 'Communal' | 'Terrorism' | 'Banditry';
}

interface IncidentCardProps {
  incident: Incident;
  index: number;
}

// Format date to relative time
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
  
  if (diffInDays === 0) return 'Today';
  if (diffInDays === 1) return 'Yesterday';
  if (diffInDays < 7) return `${diffInDays} days ago`;
  if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
  return date.toLocaleDateString();
};

// Get icon for incident type
const getTypeIcon = (type: string) => {
  return <AlertCircle className="w-5 h-5" />;
};

// Get severity color
const getSeverityColor = (severity: string) => {
  const colors = {
    Criminal: 'bg-red-100 text-red-700 border-red-300',
    Communal: 'bg-blue-100 text-blue-700 border-blue-300',
    Terrorism: 'bg-purple-100 text-purple-700 border-purple-300',
    Banditry: 'bg-orange-100 text-orange-700 border-orange-300',
  };
  return colors[severity as keyof typeof colors] || colors.Criminal;
};

export const AnimatedIncidentCard = ({ incident, index }: IncidentCardProps) => {
  return (
    <motion.div
      className="incident-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.4 }}
      whileHover={{ 
        scale: 1.02, 
        x: 4,
        boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)'
      }}
    >
      <div className="incident-card-content">
        {/* Icon container with subtle rotation animation */}
        <motion.div
          className="incident-icon-container"
          whileHover={{ rotate: [0, -5, 5, 0] }}
          transition={{ duration: 0.5 }}
        >
          <div className={`incident-icon ${incident.severity.toLowerCase()}`}>
            {getTypeIcon(incident.type)}
          </div>
        </motion.div>
        
        {/* Content */}
        <div className="incident-details">
          {/* Header */}
          <div className="incident-header">
            <h3 className="incident-title">{incident.title}</h3>
            <span className={`severity-badge ${getSeverityColor(incident.severity)}`}>
              {incident.severity}
            </span>
          </div>
          
          {/* Meta information */}
          <div className="incident-meta">
            <div className="meta-item">
              <MapPin className="meta-icon" />
              <span>{incident.location}{incident.state && `, ${incident.state}`}</span>
            </div>
            <div className="meta-item">
              <Clock className="meta-icon" />
              <span>{formatDate(incident.date)}</span>
            </div>
          </div>
          
          {/* Fatalities count */}
          {incident.fatalities > 0 && (
            <motion.div
              className="fatalities-count"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 + 0.2 }}
            >
              <Users className="fatalities-icon" />
              <span className="fatalities-number">
                <strong>{incident.fatalities}</strong> fatalit{incident.fatalities === 1 ? 'y' : 'ies'}
              </span>
            </motion.div>
          )}
        </div>
      </div>
      
      {/* Hover indicator */}
      <motion.div
        className="hover-indicator"
        initial={{ width: 0 }}
        whileHover={{ width: '100%' }}
        transition={{ duration: 0.3 }}
      />
      
      <style jsx>{`
        .incident-card {
          position: relative;
          background: white;
          border-radius: 0.75rem;
          padding: 1.25rem;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
          border: 1px solid #e5e7eb;
          cursor: pointer;
          overflow: hidden;
          transition: all 0.3s ease;
        }
        
        .incident-card:hover {
          border-color: #3b82f6;
        }
        
        .incident-card-content {
          display: flex;
          gap: 1rem;
          position: relative;
          z-index: 1;
        }
        
        .incident-icon-container {
          flex-shrink: 0;
        }
        
        .incident-icon {
          width: 48px;
          height: 48px;
          border-radius: 0.75rem;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s ease;
        }
        
        .incident-icon.criminal {
          background: linear-gradient(135deg, #fee2e2, #fecaca);
          color: #dc2626;
        }
        
        .incident-icon.communal {
          background: linear-gradient(135deg, #dbeafe, #bfdbfe);
          color: #2563eb;
        }
        
        .incident-icon.terrorism {
          background: linear-gradient(135deg, #f3e8ff, #e9d5ff);
          color: #9333ea;
        }
        
        .incident-icon.banditry {
          background: linear-gradient(135deg, #fed7aa, #fdba74);
          color: #ea580c;
        }
        
        .incident-details {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }
        
        .incident-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 1rem;
        }
        
        .incident-title {
          font-size: 1rem;
          font-weight: 600;
          color: #111827;
          line-height: 1.4;
        }
        
        .severity-badge {
          flex-shrink: 0;
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 600;
          border: 1px solid;
          white-space: nowrap;
        }
        
        .incident-meta {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        
        .meta-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.875rem;
          color: #6b7280;
        }
        
        .meta-icon {
          width: 16px;
          height: 16px;
          flex-shrink: 0;
        }
        
        .fatalities-count {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 0.75rem;
          background: #fef3c7;
          border-radius: 0.5rem;
          border: 1px solid #fde68a;
          width: fit-content;
        }
        
        .fatalities-icon {
          width: 16px;
          height: 16px;
          color: #d97706;
        }
        
        .fatalities-number {
          font-size: 0.875rem;
          color: #92400e;
        }
        
        .fatalities-number strong {
          font-weight: 700;
        }
        
        .hover-indicator {
          position: absolute;
          bottom: 0;
          left: 0;
          height: 3px;
          background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        }
        
        /* Dark mode */
        [data-theme="dark"] .incident-card {
          background: #1e293b;
          border-color: #334155;
        }
        
        [data-theme="dark"] .incident-card:hover {
          border-color: #3b82f6;
        }
        
        [data-theme="dark"] .incident-title {
          color: #f1f5f9;
        }
        
        [data-theme="dark"] .meta-item {
          color: #94a3b8;
        }
        
        /* Responsive */
        @media (max-width: 640px) {
          .incident-card-content {
            flex-direction: column;
          }
          
          .incident-header {
            flex-direction: column;
            align-items: flex-start;
          }
        }
      `}</style>
    </motion.div>
  );
};

// Container for incident list
export const IncidentsList = ({ 
  incidents, 
  title = "Recent Incidents",
  subtitle = "Latest verified conflict events with details"
}: { 
  incidents: Incident[];
  title?: string;
  subtitle?: string;
}) => {
  return (
    <div className="incidents-section">
      <div className="incidents-header">
        <h2 className="incidents-title">{title}</h2>
        <p className="incidents-subtitle">{subtitle}</p>
      </div>
      
      <div className="incidents-list">
        {incidents.map((incident, index) => (
          <AnimatedIncidentCard
            key={incident.id}
            incident={incident}
            index={index}
          />
        ))}
      </div>
      
      <style jsx>{`
        .incidents-section {
          margin: 2rem 0;
        }
        
        .incidents-header {
          margin-bottom: 1.5rem;
        }
        
        .incidents-title {
          font-size: 1.5rem;
          font-weight: 700;
          color: #111827;
          margin-bottom: 0.5rem;
        }
        
        .incidents-subtitle {
          font-size: 1rem;
          color: #6b7280;
        }
        
        .incidents-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        
        [data-theme="dark"] .incidents-title {
          color: #f1f5f9;
        }
        
        [data-theme="dark"] .incidents-subtitle {
          color: #94a3b8;
        }
      `}</style>
    </div>
  );
};
