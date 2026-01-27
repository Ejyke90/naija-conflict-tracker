# UI/Frontend Wireframe - Technical Design

**Created:** 2026-01-27  
**Status:** Draft  
**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS, Mapbox GL JS

---

## Context

The Nextier Nigeria Conflict Tracker already has a functional Next.js Pages Router frontend with TypeScript, Tailwind CSS, and various visualization libraries. This design document outlines technical decisions for implementing the comprehensive UI wireframe proposal while leveraging existing infrastructure.

---

## Goals

1. **Implement wireframes from proposal.md** - Build 15+ pages matching ASCII wireframes
2. **Leverage existing components** - Reuse StatsCard, TrendChart, ConflictMap, etc.
3. **Maintain consistency** - Follow existing patterns and conventions
4. **Optimize performance** - Code splitting, lazy loading, caching
5. **Ensure accessibility** - WCAG 2.1 AA compliance
6. **Support role-based access** - Viewer/Analyst/Admin permissions

---

## Non-Goals

- ❌ Migrating to App Router (stick with Pages Router)
- ❌ Complete design system overhaul (incremental improvements)
- ❌ Backend changes (frontend-only implementation)
- ❌ Mobile apps (responsive web only)

---

## Technical Decisions

### 1. Routing Architecture

**Decision:** Use Next.js Pages Router (existing)

**Structure:**
```
pages/
├── index.tsx                    # Landing page (public)
├── about.tsx                    # About page (public)
├── methodology.tsx              # Methodology (public)
├── login.tsx                    # Login
├── register.tsx                 # Register
├── forgot-password.tsx          # Password reset
├── dashboard/
│   ├── index.tsx               # Overview (Viewer+)
│   ├── map.tsx                 # Interactive map (Viewer+)
│   ├── analytics/
│   │   ├── hotspots.tsx        # Hotspots (Viewer+)
│   │   ├── trends.tsx          # Trends (Viewer+)
│   │   ├── correlations.tsx    # Correlations (Viewer+)
│   │   └── archetypes.tsx      # Archetypes (Viewer+)
│   ├── forecasts.tsx           # Forecasting (Analyst+)
│   ├── incidents.tsx           # Incidents table (Viewer+)
│   ├── reports.tsx             # Reports (Viewer+)
│   ├── monitoring.tsx          # System monitoring (Admin)
│   ├── admin.tsx               # User management (Admin)
│   └── profile.tsx             # User profile (All)
└── _app.tsx                     # App wrapper with auth
```

**Rationale:**
- Existing Pages Router setup
- Clear public/protected separation
- Nested routing for analytics
- No migration overhead

---

### 2. State Management

**Decision:** React Query (@tanstack/react-query) + Context API

**Architecture:**
- **Server state:** React Query for API data fetching, caching
- **Auth state:** AuthContext (existing)
- **UI state:** Component-level useState/useReducer
- **Filter state:** URL search params (Next.js router.query)

**Data Fetching Pattern:**
```typescript
// hooks/useConflicts.ts
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useConflicts(filters: ConflictFilters) {
  return useQuery({
    queryKey: ['conflicts', filters],
    queryFn: () => api.conflicts.list(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}
```

**Rationale:**
- React Query already installed
- Automatic caching, refetching
- Optimistic updates
- Loading/error states

---

### 3. Component Architecture

**Decision:** Atomic design with composition

**Hierarchy:**
```
components/
├── ui/                      # Atoms (Radix UI + shadcn/ui)
│   ├── button.tsx
│   ├── card.tsx
│   ├── badge.tsx
│   ├── tabs.tsx
│   └── ...
├── shared/                  # Molecules
│   ├── FilterPanel.tsx
│   ├── DetailPanel.tsx
│   ├── EmptyState.tsx
│   ├── LoadingSkeleton.tsx
│   └── ...
├── dashboard/               # Organisms (existing)
│   ├── StatsCard.tsx
│   ├── TrendChart.tsx
│   ├── RecentIncidents.tsx
│   └── ...
├── maps/                    # Map components
│   ├── ConflictMap.tsx      # Existing
│   ├── ClusterMarkers.tsx   # New
│   ├── HeatMapLayer.tsx     # New
│   └── MapControls.tsx      # New
├── layouts/                 # Templates
│   ├── DashboardLayout.tsx  # Existing (enhance)
│   ├── PublicLayout.tsx     # New
│   └── Sidebar.tsx          # New
└── ...
```

**Rationale:**
- Clear separation of concerns
- Reusable components
- Easy to test
- Consistent with existing structure

---

### 4. Styling System

**Decision:** Tailwind CSS + CSS Modules for complex components

**Design Tokens (tailwind.config.js):**
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        // Nigeria-themed palette
        primary: {
          50: '#f0fdf4',
          500: '#10b981',  // Green
          700: '#047857',
        },
        danger: {
          50: '#fef2f2',
          500: '#ef4444',  // Red
          700: '#b91c1c',
        },
        warning: {
          500: '#f59e0b',  // Orange
        },
        // Conflict risk levels
        risk: {
          critical: '#dc2626',
          high: '#ea580c',
          moderate: '#f59e0b',
          low: '#84cc16',
        },
      },
      spacing: {
        // Consistent spacing scale
        18: '4.5rem',
        88: '22rem',
      },
    },
  },
};
```

**Rationale:**
- Tailwind already configured
- Nigeria flag colors (green/white)
- Risk-level semantic colors
- Consistent spacing

---

### 5. Map Implementation

**Decision:** Mapbox GL JS with custom layers

**Architecture:**
```typescript
// components/maps/ConflictMap.tsx
import mapboxgl from 'mapbox-gl';
import { useEffect, useRef } from 'react';

export function ConflictMap({ incidents, filters }) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    if (!mapContainer.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/light-v11',
      center: [8.6753, 9.0820], // Nigeria center
      zoom: 6,
    });

    // Add cluster layer
    map.current.addLayer({
      id: 'clusters',
      type: 'circle',
      source: 'incidents',
      filter: ['has', 'point_count'],
      paint: {
        'circle-color': [
          'step',
          ['get', 'point_count'],
          '#51bbd6', 100,
          '#f1f075', 750,
          '#f28cb1'
        ],
        'circle-radius': [
          'step',
          ['get', 'point_count'],
          20, 100,
          30, 750,
          40
        ]
      }
    });

    // Add heat map layer
    map.current.addLayer({
      id: 'heatmap',
      type: 'heatmap',
      source: 'incidents',
      paint: {
        'heatmap-weight': [
          'interpolate',
          ['linear'],
          ['get', 'fatalities'],
          0, 0,
          10, 1
        ],
        'heatmap-intensity': 1,
        'heatmap-color': [
          'interpolate',
          ['linear'],
          ['heatmap-density'],
          0, 'rgba(0, 0, 255, 0)',
          0.2, 'royalblue',
          0.4, 'cyan',
          0.6, 'lime',
          0.8, 'yellow',
          1, 'red'
        ],
        'heatmap-radius': 20,
      }
    });

    return () => map.current?.remove();
  }, []);

  // Update data when filters change
  useEffect(() => {
    if (!map.current) return;
    map.current.getSource('incidents')?.setData(
      createGeoJSON(incidents)
    );
  }, [incidents]);

  return <div ref={mapContainer} className="h-full w-full" />;
}
```

**Features:**
- Cluster markers for performance
- Heat map overlay
- State boundaries (GeoJSON)
- Custom popup on marker click
- Zoom/pan controls

**Rationale:**
- Mapbox already used in existing ConflictMap
- Superior performance for large datasets
- Rich styling capabilities
- Nigeria-optimized tiles

---

### 6. Data Visualization

**Decision:** Recharts + D3.js for complex visualizations

**Chart Library Selection:**
| Chart Type | Library | Rationale |
|-----------|---------|-----------|
| Line charts | Recharts | Simple, responsive, already used |
| Bar charts | Recharts | Consistent with line charts |
| Scatter plots | D3.js | More control for correlations |
| Heat maps | Mapbox | Geospatial data |
| KPI cards | Custom | Lightweight, no library needed |

**Example - Trend Chart:**
```typescript
// components/dashboard/TrendChart.tsx (enhance existing)
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export function TrendChart({ data, period }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <XAxis 
          dataKey="date" 
          tickFormatter={(date) => formatDate(date, period)}
        />
        <YAxis />
        <Tooltip 
          labelFormatter={(date) => formatDate(date, period)}
          formatter={(value) => [`${value} incidents`, '']}
        />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="incidents" 
          stroke="#10b981" 
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

**Rationale:**
- Recharts simple for standard charts
- D3.js for custom visualizations
- Consistent styling across charts
- Responsive by default

---

### 7. Authentication & Authorization

**Decision:** JWT with httpOnly cookies + role-based guards

**Architecture:**
```typescript
// contexts/AuthContext.tsx (enhance existing)
export const AuthContext = createContext<AuthContextType>({});

export function AuthProvider({ children }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    api.auth.me().then(setUser).catch(() => setUser(null)).finally(() => setLoading(false));
  }, []);

  const login = async (email: string, password: string) => {
    const { access_token, user } = await api.auth.login(email, password);
    // Store token in httpOnly cookie (set by backend)
    setUser(user);
  };

  const logout = async () => {
    await api.auth.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// components/auth/RoleGuard.tsx (new)
export function RoleGuard({ children, allowedRoles }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  if (loading) return <LoadingSkeleton />;
  if (!user) {
    router.push('/login');
    return null;
  }
  if (!allowedRoles.includes(user.role)) {
    return <AccessDenied />;
  }

  return <>{children}</>;
}
```

**Page Protection:**
```typescript
// pages/dashboard/forecasts.tsx
export default function ForecastsPage() {
  return (
    <RoleGuard allowedRoles={['analyst', 'admin']}>
      <DashboardLayout>
        <ForecastsDashboard />
      </DashboardLayout>
    </RoleGuard>
  );
}
```

**Rationale:**
- httpOnly cookies prevent XSS
- Role-based guards enforce permissions
- Consistent with backend RBAC
- Simple to implement

---

### 8. Performance Optimization

**Decision:** Multi-layered optimization strategy

**Code Splitting:**
```typescript
// pages/dashboard/map.tsx
import dynamic from 'next/dynamic';

const ConflictMap = dynamic(
  () => import('@/components/maps/ConflictMap'),
  { 
    ssr: false, // Mapbox doesn't support SSR
    loading: () => <MapSkeleton />
  }
);
```

**Image Optimization:**
```typescript
import Image from 'next/image';

<Image 
  src="/nigeria-flag.png" 
  alt="Nigeria Flag"
  width={100}
  height={67}
  priority // For above-fold images
/>
```

**Caching Strategy:**
```typescript
// lib/api.ts
export const api = {
  conflicts: {
    list: (filters) => 
      fetch('/api/v1/conflicts', { 
        next: { revalidate: 300 } // 5 min cache
      }),
  },
  analytics: {
    dashboardSummary: () =>
      fetch('/api/v1/analytics/dashboard-summary', {
        next: { revalidate: 60 } // 1 min cache
      }),
  },
};
```

**Bundle Analysis:**
```json
// package.json
{
  "scripts": {
    "analyze": "ANALYZE=true next build"
  }
}
```

**Rationale:**
- Dynamic imports reduce initial bundle
- Next.js Image optimizes images
- Aggressive caching for analytics
- Monitor bundle size

---

### 9. Accessibility

**Decision:** WCAG 2.1 AA compliance

**Implementation:**
- **Keyboard navigation:** All interactive elements focusable
- **Screen reader support:** Proper ARIA labels
- **Color contrast:** 4.5:1 for text, 3:1 for UI components
- **Focus indicators:** Visible focus rings
- **Semantic HTML:** Proper heading hierarchy

**Example:**
```typescript
// components/shared/FilterPanel.tsx
export function FilterPanel({ onFilterChange }) {
  return (
    <aside 
      aria-label="Conflict filters"
      className="border-r bg-white p-4"
    >
      <h2 className="text-lg font-semibold">Filters</h2>
      
      <div className="mt-4">
        <label htmlFor="date-range" className="block text-sm font-medium">
          Date Range
        </label>
        <select 
          id="date-range"
          aria-describedby="date-range-help"
          className="mt-1 block w-full rounded-md border-gray-300"
        >
          <option>Last 30 days</option>
          <option>Last 90 days</option>
        </select>
        <p id="date-range-help" className="text-xs text-gray-500">
          Filter incidents by date
        </p>
      </div>
    </aside>
  );
}
```

**Testing:**
- Lighthouse accessibility audits
- axe DevTools
- Screen reader testing (NVDA, VoiceOver)
- Keyboard-only navigation

**Rationale:**
- Legal compliance
- Better UX for all users
- SEO benefits

---

### 10. Error Handling

**Decision:** Centralized error boundaries + user-friendly messages

**Architecture:**
```typescript
// components/ErrorBoundary.tsx
export class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
    // Send to monitoring service (e.g., Sentry)
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}

// components/ErrorFallback.tsx
export function ErrorFallback({ error }) {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold">Something went wrong</h1>
        <p className="mt-2 text-gray-600">
          {error.message || 'An unexpected error occurred'}
        </p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-4 rounded bg-primary-500 px-4 py-2 text-white"
        >
          Reload Page
        </button>
      </div>
    </div>
  );
}
```

**API Error Handling:**
```typescript
// lib/api.ts
export async function apiCall(endpoint, options) {
  try {
    const response = await fetch(endpoint, options);
    
    if (!response.ok) {
      const error = await response.json();
      throw new APIError(error.detail, response.status);
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      // Handle known API errors
      toast.error(error.message);
    } else {
      // Handle network errors
      toast.error('Network error. Please try again.');
    }
    throw error;
  }
}
```

**Rationale:**
- Graceful degradation
- User-friendly error messages
- Centralized error logging
- Easy debugging

---

## Data Flow

```
User Interaction
      ↓
Component State Update
      ↓
React Query (check cache)
      ↓
API Call (if cache miss)
      ↓
FastAPI Backend
      ↓
PostgreSQL / Redis
      ↓
Response
      ↓
React Query (update cache)
      ↓
Component Re-render
      ↓
UI Update
```

---

## Security Considerations

### XSS Prevention
- Use React's built-in escaping
- Sanitize user-generated content
- Content Security Policy (CSP)

### CSRF Protection
- httpOnly cookies for tokens
- SameSite cookie attribute
- CSRF tokens for state-changing requests

### API Security
- CORS configured on backend
- Rate limiting on frontend (debounce)
- Validate all inputs

---

## Migration Plan

**Phase 1:** Foundation (Week 1-2)
- Setup design tokens
- Enhance DashboardLayout
- Create shared components

**Phase 2:** Public Pages (Week 2)
- Landing page
- About/Methodology
- Authentication pages

**Phase 3:** Protected Pages (Week 3-8)
- Dashboard overview
- Interactive map
- Analytics dashboards
- Forecasting
- Incidents management

**Phase 4:** Admin & Polish (Week 9-10)
- Monitoring dashboard
- Admin panel
- Accessibility audit
- Performance optimization
- Testing

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Mapbox API costs | High | Implement client-side clustering, cache tiles |
| Large bundle size | Medium | Code splitting, tree shaking, analyze bundle |
| API rate limits | Medium | Implement caching, debounce requests |
| Browser compatibility | Low | Use polyfills, test on major browsers |
| Performance on mobile | Medium | Responsive images, lazy loading, reduce JS |

---

## Open Questions

1. **Map tile caching strategy?** - Use Mapbox's built-in caching or implement custom?
2. **Real-time updates?** - WebSockets for live incident updates or polling?
3. **Offline support?** - Progressive Web App (PWA) for offline access?
4. **i18n support?** - Multilingual UI (English, Hausa, Yoruba, Igbo)?

---

## Success Metrics

**Performance:**
- First Contentful Paint (FCP) < 1.5s
- Time to Interactive (TTI) < 3.0s
- Lighthouse score > 90
- Bundle size < 500KB gzipped

**Accessibility:**
- WCAG 2.1 AA compliance
- Lighthouse accessibility score > 95
- Keyboard navigation 100% functional

**User Experience:**
- Page load time < 2s
- API response time < 500ms
- Zero critical errors in production

---

## Conclusion

This design leverages existing Next.js infrastructure while implementing comprehensive wireframes. By reusing components, following established patterns, and prioritizing performance and accessibility, we can deliver a production-ready UI in 10 weeks.
