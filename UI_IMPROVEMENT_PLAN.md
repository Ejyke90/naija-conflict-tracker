# UI/UX Improvement Plan - Nextier Nigeria Conflict Tracker
**Date:** January 21, 2026  
**Goal:** Transform the conflict tracker to industry-standard data visualization platform with modern animations and professional aesthetics

---

## 📊 Current State Analysis

### Strengths ✅
- Clean, organized information architecture
- Good color coding for risk levels (red/yellow/green)
- Responsive layout with card-based design
- Interactive map integration
- Clear data hierarchy

### Areas for Improvement 🎯

#### 1. **Visual Design & Typography**
- Generic sans-serif fonts - lacks personality
- Inconsistent spacing and padding
- Plain white backgrounds - no depth or visual interest
- Limited use of shadows and elevation
- Stats cards feel flat and disconnected

#### 2. **Color Palette**
- Primary colors are too saturated (harsh reds)
- Lacks a cohesive brand color system
- No dark mode option
- Insufficient contrast in some areas
- Risk colors could be more sophisticated

#### 3. **Interactive Maps**
- Basic Leaflet/OpenStreetMap styling
- No custom map themes
- Markers lack visual hierarchy
- Missing hover states and micro-interactions
- No animated transitions when zooming/panning

#### 4. **Charts & Data Visualization**
- Simple line charts - could be more dynamic
- No gradient fills or area charts
- Missing interactive tooltips with animations
- Charts don't respond to hover states elegantly
- No loading skeletons

#### 5. **Animations & Transitions**
- **Currently:** Minimal to no animations
- Page loads feel instant but lifeless
- No entrance animations for cards
- No smooth scrolling effects
- Missing loading states and transitions

---

## 🎨 Design System Overhaul

### Color Palette (Modern & Professional)

```css
/* Brand Colors */
--primary-600: #1E40AF;      /* Deep blue - trust, stability */
--primary-500: #3B82F6;      /* Blue - primary actions */
--primary-400: #60A5FA;      /* Light blue - hover states */

/* Risk Level Colors (Sophisticated) */
--risk-critical: #DC2626;    /* Red - critical incidents */
--risk-high: #EA580C;        /* Orange-red - high risk */
--risk-medium: #F59E0B;      /* Amber - medium risk */
--risk-low: #10B981;         /* Emerald - low risk */
--risk-minimal: #6EE7B7;     /* Light green - minimal */

/* Neutral Palette */
--gray-900: #111827;         /* Dark text */
--gray-800: #1F2937;         /* Headers */
--gray-700: #374151;         /* Body text */
--gray-600: #4B5563;         /* Muted text */
--gray-500: #6B7280;         /* Disabled text */
--gray-400: #9CA3AF;         /* Borders */
--gray-300: #D1D5DB;         /* Dividers */
--gray-200: #E5E7EB;         /* Backgrounds */
--gray-100: #F3F4F6;         /* Light backgrounds */
--gray-50: #F9FAFB;          /* Subtle backgrounds */

/* Accent Colors */
--accent-purple: #8B5CF6;    /* Predictions, forecasts */
--accent-teal: #14B8A6;      /* Analytics */
--accent-pink: #EC4899;      /* Alerts, notifications */

/* Gradients */
--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--gradient-danger: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
--gradient-success: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
--gradient-dark: linear-gradient(135deg, #1f1c2c 0%, #928dab 100%);
```

### Typography System

```css
/* Font Families */
--font-display: 'Inter', 'SF Pro Display', -apple-system, sans-serif;
--font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Font Sizes (Fluid Typography) */
--text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
--text-sm: clamp(0.875rem, 0.8rem + 0.35vw, 1rem);
--text-base: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
--text-lg: clamp(1.125rem, 1.05rem + 0.35vw, 1.25rem);
--text-xl: clamp(1.25rem, 1.15rem + 0.5vw, 1.5rem);
--text-2xl: clamp(1.5rem, 1.35rem + 0.75vw, 2rem);
--text-3xl: clamp(1.875rem, 1.65rem + 1.125vw, 2.5rem);
--text-4xl: clamp(2.25rem, 1.95rem + 1.5vw, 3rem);

/* Font Weights */
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;
```

### Spacing System

```css
/* Consistent spacing scale (8px base) */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
```

### Elevation System (Shadows)

```css
/* Subtle depth hierarchy */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
--shadow-inner: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);

/* Colored shadows for emphasis */
--shadow-primary: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
--shadow-danger: 0 10px 25px -5px rgba(220, 38, 38, 0.3);
--shadow-success: 0 10px 25px -5px rgba(16, 185, 129, 0.3);
```

---

## 🎬 Animation Strategy

### 1. **Page Load Animations**

#### Hero Section
```typescript
// Staggered fade-in with slide-up
const heroAnimation = {
  initial: { opacity: 0, y: 20 },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: 0.6,
      ease: [0.25, 0.1, 0.25, 1.0] // Custom easing
    }
  }
}

// Stats cards cascade
const statsCardVariants = {
  hidden: { opacity: 0, scale: 0.8, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      delay: i * 0.1,
      duration: 0.5,
      ease: "easeOut"
    }
  })
}
```

#### Stats Cards Entrance
- **Stagger delay:** 100ms between each card
- **Motion:** Fade in + scale (0.8 → 1.0) + slide up
- **Duration:** 500ms per card
- **Easing:** easeOut cubic-bezier

### 2. **Number Counter Animations**

```typescript
// Animated counting for incident numbers
const CountUp = ({ end, duration = 2000 }) => {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    let startTime: number;
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = (currentTime - startTime) / duration;
      
      if (progress < 1) {
        setCount(Math.floor(end * easeOutQuart(progress)));
        requestAnimationFrame(animate);
      } else {
        setCount(end);
      }
    };
    requestAnimationFrame(animate);
  }, [end, duration]);
  
  return <span>{count.toLocaleString()}</span>;
};

// Easing function for smooth deceleration
const easeOutQuart = (t: number) => 1 - (--t) * t * t * t;
```

### 3. **Map Animations**

#### Marker Pulse Effect
```css
@keyframes pulse-marker {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.15);
    opacity: 0.8;
  }
}

.conflict-marker {
  animation: pulse-marker 2s ease-in-out infinite;
}

.conflict-marker.high-risk {
  animation-duration: 1.5s; /* Faster pulse for urgent */
}
```

#### Heat Map Fade-in
```typescript
// Animated heat map intensity
const heatmapAnimation = {
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: {
      duration: 1.5,
      ease: "easeInOut"
    }
  }
}
```

#### Smooth Zoom & Pan
```javascript
// Leaflet map with smooth transitions
map.flyTo([lat, lng], zoom, {
  animate: true,
  duration: 1.5,
  easeLinearity: 0.25
});
```

### 4. **Chart Animations**

#### Line Chart Drawing Effect
```typescript
// Recharts with animated path drawing
<Line
  type="monotone"
  dataKey="incidents"
  stroke="#3B82F6"
  strokeWidth={3}
  animationDuration={2000}
  animationEasing="ease-in-out"
  isAnimationActive={true}
/>

// Custom SVG path animation
const pathVariants = {
  hidden: { 
    pathLength: 0,
    opacity: 0
  },
  visible: {
    pathLength: 1,
    opacity: 1,
    transition: {
      pathLength: { 
        duration: 2,
        ease: "easeInOut" 
      },
      opacity: { 
        duration: 0.5 
      }
    }
  }
}
```

#### Bar Chart Grow-In
```css
@keyframes bar-grow {
  from {
    transform: scaleY(0);
    transform-origin: bottom;
  }
  to {
    transform: scaleY(1);
  }
}

.chart-bar {
  animation: bar-grow 0.8s ease-out forwards;
}

.chart-bar:nth-child(1) { animation-delay: 0.1s; }
.chart-bar:nth-child(2) { animation-delay: 0.2s; }
.chart-bar:nth-child(3) { animation-delay: 0.3s; }
```

### 5. **Hover Micro-Interactions**

```css
/* Card hover effect */
.stat-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: var(--shadow-xl);
}

/* Button ripple effect */
@keyframes ripple {
  to {
    transform: scale(4);
    opacity: 0;
  }
}

.button-ripple::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  animation: ripple 0.6s ease-out;
}

/* Tooltip smooth appear */
.tooltip {
  animation: tooltip-appear 0.2s ease-out;
}

@keyframes tooltip-appear {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### 6. **Loading States**

#### Skeleton Screens
```typescript
const SkeletonCard = () => (
  <div className="skeleton-card">
    <div className="skeleton-line skeleton-animate" />
    <div className="skeleton-line skeleton-animate" style={{ width: '60%' }} />
  </div>
);

// CSS
@keyframes skeleton-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.skeleton-animate {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
```

#### Spinner
```tsx
const Spinner = () => (
  <div className="spinner">
    <div className="spinner-ring" />
  </div>
);

// CSS
@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner-ring {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3B82F6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
```

### 7. **Scroll-Triggered Animations**

```typescript
// Using Framer Motion + Intersection Observer
const FadeInWhenVisible = ({ children }) => {
  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-100px" }}
      variants={{
        hidden: { opacity: 0, y: 50 },
        visible: {
          opacity: 1,
          y: 0,
          transition: {
            duration: 0.6,
            ease: "easeOut"
          }
        }
      }}
    >
      {children}
    </motion.div>
  );
};
```

### 8. **Background Animations**

#### Gradient Mesh (Subtle)
```css
.hero-background {
  background: linear-gradient(
    135deg,
    rgba(59, 130, 246, 0.1) 0%,
    rgba(139, 92, 246, 0.05) 50%,
    rgba(236, 72, 153, 0.1) 100%
  );
  background-size: 400% 400%;
  animation: gradient-shift 15s ease infinite;
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

#### Floating Particles (Optional)
```typescript
// Canvas-based particle system for hero section
const ParticleBackground = () => {
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const particles: Particle[] = [];
    
    // Create floating particles
    for (let i = 0; i < 50; i++) {
      particles.push(new Particle(canvas.width, canvas.height));
    }
    
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach(p => {
        p.update();
        p.draw(ctx);
      });
      requestAnimationFrame(animate);
    };
    
    animate();
  }, []);
};
```

---

## 🗺️ Interactive Map Improvements

### Custom Map Styling (Mapbox GL JS)

```javascript
// Replace OpenStreetMap with custom Mapbox style
const mapStyle = {
  version: 8,
  sources: {
    'mapbox': {
      type: 'vector',
      url: 'mapbox://mapbox.mapbox-streets-v8'
    }
  },
  layers: [
    {
      id: 'background',
      type: 'background',
      paint: {
        'background-color': '#1a1a2e' // Dark theme
      }
    },
    {
      id: 'water',
      type: 'fill',
      source: 'mapbox',
      'source-layer': 'water',
      paint: {
        'fill-color': '#16213e'
      }
    },
    {
      id: 'land',
      type: 'fill',
      source: 'mapbox',
      'source-layer': 'landuse',
      paint: {
        'fill-color': '#0f3460',
        'fill-opacity': 0.4
      }
    },
    {
      id: 'borders',
      type: 'line',
      source: 'mapbox',
      'source-layer': 'admin',
      paint: {
        'line-color': '#e94560',
        'line-width': 2,
        'line-opacity': 0.5
      }
    }
  ]
};
```

### Heat Map Layer

```javascript
map.addLayer({
  id: 'conflict-heatmap',
  type: 'heatmap',
  source: 'conflicts',
  paint: {
    // Increase weight as incident count increases
    'heatmap-weight': [
      'interpolate',
      ['linear'],
      ['get', 'fatalities'],
      0, 0,
      100, 1
    ],
    // Color ramp: blue -> yellow -> red
    'heatmap-color': [
      'interpolate',
      ['linear'],
      ['heatmap-density'],
      0, 'rgba(33, 102, 172, 0)',
      0.2, 'rgb(103, 169, 207)',
      0.4, 'rgb(209, 229, 240)',
      0.6, 'rgb(253, 219, 199)',
      0.8, 'rgb(239, 138, 98)',
      1, 'rgb(178, 24, 43)'
    ],
    'heatmap-radius': [
      'interpolate',
      ['linear'],
      ['zoom'],
      0, 2,
      9, 20
    ],
    'heatmap-opacity': 0.8
  }
});
```

### Cluster Markers with Numbers

```javascript
// Cluster configuration
map.addSource('conflicts', {
  type: 'geojson',
  data: conflictData,
  cluster: true,
  clusterMaxZoom: 14,
  clusterRadius: 50
});

// Cluster circles
map.addLayer({
  id: 'clusters',
  type: 'circle',
  source: 'conflicts',
  filter: ['has', 'point_count'],
  paint: {
    'circle-color': [
      'step',
      ['get', 'point_count'],
      '#10B981', 10,  // Green for < 10
      '#F59E0B', 25,  // Yellow for 10-25
      '#EF4444'       // Red for > 25
    ],
    'circle-radius': [
      'step',
      ['get', 'point_count'],
      20, 10,
      30, 25,
      40
    ],
    'circle-stroke-width': 2,
    'circle-stroke-color': '#fff'
  }
});

// Cluster count labels
map.addLayer({
  id: 'cluster-count',
  type: 'symbol',
  source: 'conflicts',
  filter: ['has', 'point_count'],
  layout: {
    'text-field': '{point_count_abbreviated}',
    'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
    'text-size': 12
  },
  paint: {
    'text-color': '#ffffff'
  }
});
```

### Interactive Popup on Hover

```typescript
const ConflictPopup = ({ incident }: { incident: Conflict }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    className="conflict-popup"
  >
    <div className="popup-header">
      <span className={`risk-badge ${incident.riskLevel}`}>
        {incident.riskLevel}
      </span>
      <span className="popup-date">{incident.date}</span>
    </div>
    <h3 className="popup-title">{incident.title}</h3>
    <p className="popup-location">📍 {incident.location}</p>
    <div className="popup-stats">
      <div className="stat">
        <span className="stat-icon">👥</span>
        <span className="stat-value">{incident.fatalities} fatalities</span>
      </div>
      <div className="stat">
        <span className="stat-icon">🔫</span>
        <span className="stat-value">{incident.type}</span>
      </div>
    </div>
    <button className="popup-cta">View Details →</button>
  </motion.div>
);
```

---

## 📈 Chart Enhancements

### 1. **Gradient Area Charts**

```typescript
<AreaChart data={monthlyData}>
  <defs>
    <linearGradient id="incidentGradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
      <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
    </linearGradient>
  </defs>
  <Area
    type="monotone"
    dataKey="incidents"
    stroke="#3B82F6"
    strokeWidth={3}
    fill="url(#incidentGradient)"
    animationDuration={2000}
  />
</AreaChart>
```

### 2. **Interactive Tooltips**

```typescript
const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="custom-tooltip"
    >
      <div className="tooltip-header">
        {payload[0].payload.month}
      </div>
      <div className="tooltip-content">
        <div className="tooltip-row">
          <span className="tooltip-label">Incidents:</span>
          <span className="tooltip-value">{payload[0].value}</span>
        </div>
        <div className="tooltip-row">
          <span className="tooltip-label">Trend:</span>
          <span className="tooltip-trend">
            {payload[0].payload.trend > 0 ? '↗️ +' : '↘️ '}
            {payload[0].payload.trend}%
          </span>
        </div>
      </div>
    </motion.div>
  );
};
```

### 3. **Sparklines for Stats Cards**

```typescript
const SparklineChart = ({ data }: { data: number[] }) => (
  <svg width="100" height="30" className="sparkline">
    <motion.path
      d={generateSparklinePath(data)}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{ duration: 1.5 }}
    />
  </svg>
);
```

---

## 🎭 Component-Specific Improvements

### 1. **Hero Section Redesign**

```tsx
<section className="hero-section">
  {/* Animated background gradient */}
  <div className="hero-background" />
  
  {/* Floating particles (optional) */}
  <ParticleBackground />
  
  <motion.div
    className="hero-content"
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.8 }}
  >
    <h1 className="hero-title">
      Nextier Nigeria Conflict Tracker
    </h1>
    <p className="hero-subtitle">
      AI-powered real-time monitoring and predictive analysis of conflicts across Nigeria
    </p>
    
    <div className="hero-badges">
      <motion.div
        className="badge badge-live"
        animate={{ scale: [1, 1.05, 1] }}
        transition={{ repeat: Infinity, duration: 2 }}
      >
        <span className="badge-dot" /> Live
      </motion.div>
      <div className="badge badge-risk">
        Risk Level: <strong>HIGH</strong>
      </div>
    </div>
  </motion.div>
</section>
```

### 2. **Stats Cards Enhanced**

```tsx
const StatCard = ({ icon, label, value, change, color, index }) => (
  <motion.div
    className={`stat-card stat-card-${color}`}
    custom={index}
    initial="hidden"
    animate="visible"
    variants={statsCardVariants}
    whileHover={{ 
      y: -8,
      boxShadow: "0 20px 40px rgba(0,0,0,0.15)"
    }}
  >
    {/* Icon with subtle animation */}
    <motion.div
      className="stat-icon"
      whileHover={{ rotate: 5, scale: 1.1 }}
    >
      {icon}
    </motion.div>
    
    {/* Label */}
    <span className="stat-label">{label}</span>
    
    {/* Animated counter */}
    <div className="stat-value">
      <CountUp end={value} duration={2000} />
    </div>
    
    {/* Mini sparkline */}
    <SparklineChart data={historicalData} />
    
    {/* Change indicator */}
    <div className={`stat-change ${change > 0 ? 'positive' : 'negative'}`}>
      {change > 0 ? '↗' : '↘'} {Math.abs(change)}%
      <span className="stat-period">vs previous period</span>
    </div>
  </motion.div>
);
```

### 3. **Risk Assessment Panel**

```tsx
const RiskAssessment = () => (
  <div className="risk-assessment-panel">
    <h2 className="section-title">Risk Assessment</h2>
    
    {riskZones.map((zone, i) => (
      <motion.div
        key={zone.id}
        className={`risk-zone risk-${zone.level}`}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: i * 0.1 }}
      >
        <div className="risk-header">
          <span className="risk-icon">{zone.icon}</span>
          <span className="risk-name">{zone.name}</span>
        </div>
        <div className="risk-region">{zone.region}</div>
        
        {/* Animated progress bar */}
        <div className="risk-bar-container">
          <motion.div
            className="risk-bar"
            initial={{ width: 0 }}
            animate={{ width: `${zone.percentage}%` }}
            transition={{ duration: 1, delay: i * 0.1 + 0.3 }}
          />
        </div>
        <div className="risk-percentage">{zone.percentage}%</div>
      </motion.div>
    ))}
  </div>
);
```

### 4. **Recent Incidents List**

```tsx
const IncidentCard = ({ incident, index }) => (
  <motion.div
    className="incident-card"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: index * 0.05 }}
    whileHover={{ scale: 1.02, x: 4 }}
  >
    <div className="incident-icon-container">
      <motion.div
        className={`incident-icon ${incident.type}`}
        animate={{ rotate: [0, 5, -5, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        {getIconForType(incident.type)}
      </motion.div>
    </div>
    
    <div className="incident-content">
      <div className="incident-header">
        <h3 className="incident-title">{incident.title}</h3>
        <span className={`incident-badge ${incident.severity}`}>
          {incident.severity}
        </span>
      </div>
      
      <div className="incident-meta">
        <span className="incident-location">
          📍 {incident.location}
        </span>
        <span className="incident-date">
          🕒 {formatDate(incident.date)}
        </span>
      </div>
      
      {incident.fatalities > 0 && (
        <div className="incident-fatalities">
          <span className="fatality-icon">👥</span>
          <CountUp end={incident.fatalities} duration={1500} /> fatalities
        </div>
      )}
    </div>
  </motion.div>
);
```

---

## 🌙 Dark Mode Implementation

```css
/* Dark mode color scheme */
[data-theme="dark"] {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
  
  --text-primary: #f1f5f9;
  --text-secondary: #cbd5e1;
  --text-tertiary: #94a3b8;
  
  --border-color: #334155;
  
  /* Adjust shadows for dark mode */
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
}

/* Smooth theme transition */
* {
  transition: background-color 0.3s ease, color 0.3s ease;
}
```

---

## 📦 Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Install Framer Motion: `npm install framer-motion`
- [ ] Setup design tokens (CSS variables)
- [ ] Update typography (Inter font)
- [ ] Implement color system
- [ ] Add elevation/shadow system

### Phase 2: Core Animations (Week 1-2)
- [ ] Page load animations (hero, stats cards)
- [ ] Number counter animations
- [ ] Hover micro-interactions
- [ ] Loading states (skeletons, spinners)
- [ ] Scroll-triggered animations

### Phase 3: Map Enhancements (Week 2)
- [ ] Custom Mapbox style
- [ ] Heat map layer
- [ ] Cluster markers
- [ ] Animated popups
- [ ] Smooth zoom/pan transitions

### Phase 4: Chart Improvements (Week 2-3)
- [ ] Gradient area charts
- [ ] Animated tooltips
- [ ] Sparklines in stat cards
- [ ] Interactive legends
- [ ] Chart drawing animations

### Phase 5: Advanced Features (Week 3-4)
- [ ] Dark mode toggle
- [ ] Background animations (gradient mesh)
- [ ] Particle effects (optional)
- [ ] Enhanced risk assessment panel
- [ ] Improved incident cards

### Phase 6: Polish & Optimization (Week 4)
- [ ] Performance optimization (lazy loading)
- [ ] Reduce motion accessibility option
- [ ] Cross-browser testing
- [ ] Mobile responsiveness
- [ ] Animation performance profiling

---

## 🎯 Success Metrics

### User Experience
- **Page load time:** < 2 seconds
- **Time to interactive:** < 3 seconds
- **First contentful paint:** < 1 second
- **Animation frame rate:** 60 FPS
- **Accessibility score:** > 95

### Visual Appeal
- **Design consistency:** All components follow design system
- **Animation smoothness:** No jank or stuttering
- **Color accessibility:** WCAG AA compliance
- **Mobile responsiveness:** Works on all screen sizes

---

## 🛠️ Tools & Libraries

### Required
- **Framer Motion:** Advanced animations
- **Recharts:** Chart animations
- **Mapbox GL JS:** Custom map styling
- **Tailwind CSS:** Utility-first styling
- **Inter Font:** Modern typography

### Optional
- **GSAP:** Complex animation sequences
- **Three.js:** 3D background effects
- **Lottie:** Pre-made animations
- **React Spring:** Physics-based animations

---

## 📚 References & Inspiration

### Design Systems
- [Stripe Dashboard](https://stripe.com/dashboard)
- [Vercel Analytics](https://vercel.com/analytics)
- [Linear App](https://linear.app)
- [Notion](https://notion.so)

### Animation Examples
- [Apple Product Pages](https://apple.com)
- [Stripe.com](https://stripe.com)
- [Awwwards Winners](https://awwwards.com)

### Data Visualization
- [Observable HQ](https://observablehq.com)
- [Mapbox Gallery](https://mapbox.com/gallery)
- [D3.js Examples](https://observablehq.com/@d3/gallery)

---

**Next Step:** Begin implementation with Phase 1 (Foundation) to establish design system and core styling framework.
