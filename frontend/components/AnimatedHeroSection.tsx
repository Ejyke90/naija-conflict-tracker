import { motion } from 'framer-motion';
import { Zap } from 'lucide-react';

interface HeroSectionProps {
  title?: string;
  subtitle?: string;
  isLive?: boolean;
  riskLevel?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export const AnimatedHeroSection = ({
  title = "Nextier Nigeria Conflict Tracker",
  subtitle = "AI-powered real-time monitoring and predictive analysis of conflicts across Nigeria",
  isLive = true,
  riskLevel = "HIGH"
}: HeroSectionProps) => {
  
  // Get risk level color
  const getRiskColor = () => {
    const colors = {
      LOW: 'text-green-600 bg-green-100 border-green-300',
      MEDIUM: 'text-yellow-600 bg-yellow-100 border-yellow-300',
      HIGH: 'text-orange-600 bg-orange-100 border-orange-300',
      CRITICAL: 'text-red-600 bg-red-100 border-red-300',
    };
    return colors[riskLevel] || colors.HIGH;
  };
  
  return (
    <section className="hero-section">
      {/* Animated gradient background */}
      <div className="hero-background" />
      
      {/* Grid pattern overlay */}
      <div className="hero-grid-pattern" />
      
      {/* Content */}
      <div className="hero-content-wrapper">
        <motion.div
          className="hero-content"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1.0] }}
        >
          {/* Title */}
          <motion.h1
            className="hero-title"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            {title}
          </motion.h1>
          
          {/* Subtitle */}
          <motion.p
            className="hero-subtitle"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            {subtitle}
          </motion.p>
          
          {/* Badges */}
          <motion.div
            className="hero-badges"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.6 }}
          >
            {/* Live badge with pulse */}
            {isLive && (
              <motion.div
                className="badge badge-live"
                animate={{ 
                  scale: [1, 1.05, 1] 
                }}
                transition={{ 
                  repeat: Infinity, 
                  duration: 2,
                  ease: "easeInOut"
                }}
              >
                <span className="badge-dot" />
                <span className="badge-text">Live</span>
              </motion.div>
            )}
            
            {/* AI Prediction Engine badge */}
            <div className="badge badge-feature">
              <Zap className="w-4 h-4" />
              <span className="badge-text">AI Prediction Engine Active</span>
            </div>
            
            {/* Risk level badge */}
            <div className={`badge badge-risk ${getRiskColor()}`}>
              <span className="badge-text">Risk Level: <strong>{riskLevel}</strong></span>
            </div>
          </motion.div>
        </motion.div>
      </div>
      
      <style jsx>{`
        .hero-section {
          position: relative;
          padding: 4rem 2rem;
          overflow: hidden;
          min-height: 300px;
        }
        
        .hero-background {
          position: absolute;
          inset: 0;
          background: linear-gradient(
            135deg,
            rgba(59, 130, 246, 0.08) 0%,
            rgba(139, 92, 246, 0.04) 50%,
            rgba(236, 72, 153, 0.08) 100%
          );
          background-size: 400% 400%;
          animation: gradient-shift 15s ease infinite;
        }
        
        @keyframes gradient-shift {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        
        .hero-grid-pattern {
          position: absolute;
          inset: 0;
          background-image: 
            linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
          background-size: 50px 50px;
          opacity: 0.5;
        }
        
        .hero-content-wrapper {
          position: relative;
          z-index: 10;
          max-width: 1200px;
          margin: 0 auto;
        }
        
        .hero-content {
          text-align: center;
        }
        
        .hero-title {
          font-size: clamp(2.25rem, 5vw, 3.5rem);
          font-weight: 800;
          color: #111827;
          margin-bottom: 1rem;
          line-height: 1.1;
          letter-spacing: -0.02em;
        }
        
        .hero-subtitle {
          font-size: clamp(1.125rem, 2vw, 1.5rem);
          color: #4b5563;
          margin-bottom: 2rem;
          max-width: 800px;
          margin-left: auto;
          margin-right: auto;
          line-height: 1.5;
        }
        
        .hero-badges {
          display: flex;
          gap: 1rem;
          justify-content: center;
          flex-wrap: wrap;
        }
        
        .badge {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          border-radius: 9999px;
          font-size: 0.875rem;
          font-weight: 500;
          transition: all 0.2s ease;
        }
        
        .badge-live {
          background: linear-gradient(135deg, #10b981, #059669);
          color: white;
          box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }
        
        .badge-dot {
          width: 8px;
          height: 8px;
          background: white;
          border-radius: 50%;
          animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
        
        .badge-feature {
          background: linear-gradient(135deg, #3b82f6, #2563eb);
          color: white;
          box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
        
        .badge-risk {
          border: 2px solid;
          font-weight: 600;
        }
        
        .badge-text {
          font-weight: 500;
        }
        
        .badge strong {
          font-weight: 700;
        }
        
        /* Dark mode */
        [data-theme="dark"] .hero-title {
          color: #f1f5f9;
        }
        
        [data-theme="dark"] .hero-subtitle {
          color: #cbd5e1;
        }
        
        [data-theme="dark"] .hero-background {
          background: linear-gradient(
            135deg,
            rgba(59, 130, 246, 0.15) 0%,
            rgba(139, 92, 246, 0.08) 50%,
            rgba(236, 72, 153, 0.15) 100%
          );
        }
        
        /* Responsive */
        @media (max-width: 768px) {
          .hero-section {
            padding: 3rem 1.5rem;
          }
          
          .hero-badges {
            flex-direction: column;
            align-items: center;
          }
          
          .badge {
            width: 100%;
            max-width: 300px;
            justify-content: center;
          }
        }
      `}</style>
    </section>
  );
};
