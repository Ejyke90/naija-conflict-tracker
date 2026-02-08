# Design Specification: Modernize Dashboard UI

## Design System

### Color Palette

```typescript
// Primary Colors (Blue - Main actions, data points)
primary: {
  50:  '#eff6ff',  // Lightest - backgrounds
  100: '#dbeafe',  // Light - hover states
  200: '#bfdbfe',
  300: '#93c5fd',
  400: '#60a5fa',
  500: '#3b82f6',  // Base - primary actions
  600: '#2563eb',  // Dark - active states
  700: '#1d4ed8',
  800: '#1e40af',
  900: '#1e3a8a',  // Darkest - text on light
}

// Destructive/High Risk (Red)
destructive: {
  50:  '#fef2f2',
  500: '#ef4444',  // Fatalities, critical risk
  600: '#dc2626',
  700: '#b91c1c',
}

// Warning/Medium Risk (Amber)
warning: {
  50:  '#fffbeb',
  500: '#f59e0b',  // Medium risk
  600: '#d97706',
}

// Success/Improvement (Green)
success: {
  50:  '#f0fdf4',
  500: '#22c55e',  // Decreasing trends
  600: '#16a34a',
}

// Neutral (Slate - Backgrounds, borders, text)
slate: {
  50:  '#f8fafc',  // Card backgrounds
  100: '#f1f5f9',  // Alternating rows
  200: '#e2e8f0',  // Borders
  300: '#cbd5e1',
  400: '#94a3b8',
  500: '#64748b',  // Secondary text
  600: '#475569',
  700: '#334155',
  800: '#1e293b',
  900: '#0f172a',  // Primary text
}
```

### Typography Scale

```css
/* Display (Hero text) */
.text-display {
  font-size: 3rem;      /* 48px */
  line-height: 1.2;
  font-weight: 800;
  letter-spacing: -0.02em;
}

/* Heading 1 (Page titles) */
.text-h1 {
  font-size: 2.25rem;   /* 36px */
  line-height: 1.25;
  font-weight: 700;
}

/* Heading 2 (Section titles) */
.text-h2 {
  font-size: 1.875rem;  /* 30px */
  line-height: 1.3;
  font-weight: 600;
}

/* Heading 3 (Card titles) */
.text-h3 {
  font-size: 1.5rem;    /* 24px */
  line-height: 1.35;
  font-weight: 600;
}

/* Body Large (Important content) */
.text-body-lg {
  font-size: 1.125rem;  /* 18px */
  line-height: 1.6;
  font-weight: 400;
}

/* Body (Default text) */
.text-body {
  font-size: 1rem;      /* 16px */
  line-height: 1.6;
  font-weight: 400;
}

/* Body Small (Supporting text) */
.text-body-sm {
  font-size: 0.875rem;  /* 14px */
  line-height: 1.5;
  font-weight: 400;
}

/* Caption (Hints, labels) */
.text-caption {
  font-size: 0.75rem;   /* 12px */
  line-height: 1.4;
  font-weight: 400;
  color: theme('colors.slate.500');
}
```

### Spacing Scale

Use Tailwind's spacing scale consistently:
- `space-1`: 4px - Tight spacing (icon-text gap)
- `space-2`: 8px - Compact spacing (button padding)
- `space-3`: 12px - Default spacing (card padding-x)
- `space-4`: 16px - Comfortable spacing (card padding-y)
- `space-6`: 24px - Generous spacing (section gaps)
- `space-8`: 32px - Large spacing (component gaps)
- `space-12`: 48px - Extra large (page sections)

### Shadows

```css
/* Elevation 1 - Subtle lift */
shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);

/* Elevation 2 - Card default */
shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);

/* Elevation 3 - Card hover */
shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);

/* Elevation 4 - Dropdown, modal */
shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);

/* Elevation 5 - Overlay */
shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
```

### Border Radius

```css
rounded-sm: 0.125rem;   /* 2px - Small elements */
rounded:    0.25rem;    /* 4px - Buttons, badges */
rounded-md: 0.375rem;   /* 6px - Inputs */
rounded-lg: 0.5rem;     /* 8px - Cards */
rounded-xl: 0.75rem;    /* 12px - Feature cards */
rounded-2xl: 1rem;      /* 16px - Hero cards */
```

## Component Specifications

### StatCard Component

**Visual Design:**
```
┌────────────────────────────────────┐
│ 🎯 Title                    ↑ 12%  │  ← Icon + Title + Trend
│                                    │
│ 1,234                              │  ← Large Metric
│ incidents                          │  ← Unit/Label
│                                    │
│ [Mini Sparkline Chart]             │  ← Optional Visualization
│                                    │
│ Last 3 months                      │  ← Caption
└────────────────────────────────────┘
```

**Props:**
```typescript
interface StatCardProps {
  title: string;
  value: number | string;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  trendPercent?: number;
  icon?: LucideIcon;
  color?: 'blue' | 'red' | 'amber' | 'green' | 'slate';
  sparklineData?: number[];
  caption?: string;
  loading?: boolean;
}
```

**Styling:**
- Background: `bg-white`
- Border: `border border-slate-200`
- Padding: `p-6`
- Rounded: `rounded-lg`
- Shadow: `shadow-sm hover:shadow-md`
- Transition: `transition-all duration-200`

**States:**
- Default: As above
- Hover: `shadow-md`, `translate-y-[-2px]`
- Loading: Skeleton with shimmer animation
- Error: Red border, error icon

### Forecast Card Component

**Visual Design:**
```
┌────────────────────────────────────┐
│ 🔥 KADUNA                          │  ← State name + emoji/icon
│                                    │
│ 67 predicted incidents             │  ← Main prediction
│ ████████████████░░░░ 75%           │  ← Confidence bar
│                                    │
│ Range: 45-89 incidents             │  ← Confidence interval
│ Next 30 days                       │  ← Time period
└────────────────────────────────────┘
```

**Styling:**
- Background: Gradient `from-blue-500 via-blue-600 to-indigo-700`
- Text: `text-white`
- Padding: `p-6`
- Rounded: `rounded-2xl`
- Shadow: `shadow-xl`
- Hover: `hover:shadow-2xl hover:scale-[1.02]`
- Animation: Stagger (delay i * 0.1s)

### Chart Specifications

**Bar Chart (Incidents/Fatalities):**
```typescript
<BarChart data={data} height={340}>
  <CartesianGrid 
    strokeDasharray="3 3" 
    stroke="#e2e8f0" 
    opacity={0.3}
  />
  <XAxis 
    dataKey="state" 
    tick={{ fill: '#64748b', fontSize: 12 }}
    axisLine={{ stroke: '#cbd5e1' }}
  />
  <YAxis 
    tick={{ fill: '#64748b', fontSize: 12 }}
    axisLine={{ stroke: '#cbd5e1' }}
  />
  <Tooltip 
    contentStyle={{
      backgroundColor: 'white',
      border: '1px solid #e2e8f0',
      borderRadius: '8px',
      padding: '12px',
      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
    }}
  />
  <Bar 
    dataKey="incidents" 
    fill="#3b82f6" 
    radius={[4, 4, 0, 0]}
    animationDuration={800}
  />
  <Bar 
    dataKey="fatalities" 
    fill="#ef4444" 
    radius={[4, 4, 0, 0]}
    animationDuration={800}
  />
</BarChart>
```

**Line Chart (Trends):**
- Line stroke: `#3b82f6` (blue)
- Line width: `2px`
- Dot size: `6px`
- Gradient fill: `url(#gradientBlue)`
- Animation: Smooth drawing (800ms)

**Gradient Definition:**
```tsx
<defs>
  <linearGradient id="gradientBlue" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3} />
    <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
  </linearGradient>
</defs>
```

### Table Specifications

**Structure:**
```tsx
<Card>
  <CardHeader>
    <CardTitle>State Statistics Overview</CardTitle>
  </CardHeader>
  <CardContent className="p-0">
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-slate-50 border-b border-slate-200">
          <tr>
            <th className="text-left px-6 py-4 text-sm font-semibold text-slate-700">
              State
            </th>
            {/* More headers */}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr 
              key={row.state}
              className="border-b border-slate-100 hover:bg-slate-50 transition-colors"
            >
              <td className="px-6 py-5 text-sm font-medium text-slate-900">
                {row.state}
              </td>
              {/* More cells */}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </CardContent>
</Card>
```

**Styling:**
- Header background: `bg-slate-50`
- Header text: `text-sm font-semibold text-slate-700`
- Row padding: `px-6 py-5`
- Hover: `hover:bg-slate-50 transition-colors`
- Border: `border-slate-100`

### Badge Component (Risk Levels)

**Variants:**
```tsx
// Critical Risk
<Badge variant="destructive" className="animate-pulse">
  <AlertTriangle className="w-3 h-3 mr-1" />
  Critical
</Badge>

// High Risk
<Badge className="bg-red-100 text-red-700 hover:bg-red-200">
  High
</Badge>

// Medium Risk
<Badge className="bg-amber-100 text-amber-700 hover:bg-amber-200">
  Medium
</Badge>

// Low Risk
<Badge className="bg-green-100 text-green-700 hover:bg-green-200">
  Low
</Badge>
```

## Animation Specifications

### Page Load Animation

```tsx
import { motion } from 'framer-motion';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  },
};

<motion.div
  variants={containerVariants}
  initial="hidden"
  animate="visible"
>
  <motion.div variants={itemVariants}>
    {/* Component 1 */}
  </motion.div>
  <motion.div variants={itemVariants}>
    {/* Component 2 */}
  </motion.div>
</motion.div>
```

### Hover Animations

```tsx
// Card Lift
<motion.div
  whileHover={{ y: -4, boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
  transition={{ duration: 0.2 }}
>
  {/* Card content */}
</motion.div>

// Scale
<motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
>
  Click me
</motion.button>
```

### Loading Skeleton

```tsx
<div className="animate-pulse space-y-4">
  <div className="h-4 bg-slate-200 rounded w-3/4"></div>
  <div className="h-8 bg-slate-200 rounded"></div>
  <div className="h-4 bg-slate-200 rounded w-5/6"></div>
</div>
```

## Responsive Breakpoints

```css
/* Mobile First Approach */
sm: 640px   /* Small tablets */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large displays */
```

**Layout Adjustments:**
- Mobile (<640px): 1 column, stacked cards
- Tablet (640-1024px): 2 columns for stat cards
- Desktop (1024px+): 3-4 columns for stat cards

**Grid Example:**
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  {/* Cards */}
</div>
```

## Accessibility Guidelines

### Color Contrast
- Text on white: `#0f172a` (slate-900) - 15.68:1 ratio ✅
- Secondary text: `#64748b` (slate-500) - 4.58:1 ratio ✅
- Links: `#2563eb` (blue-600) - 6.14:1 ratio ✅

### Keyboard Navigation
- All interactive elements focusable
- Focus ring: `focus:ring-2 focus:ring-blue-500 focus:ring-offset-2`
- Skip links for screen readers
- Logical tab order

### ARIA Labels
```tsx
<button aria-label="Sort by incidents">
  <TrendingUp className="w-4 h-4" />
</button>

<div role="status" aria-live="polite">
  Loading data...
</div>

<Badge aria-label={`Risk level: ${riskLevel}`}>
  {riskLevel}
</Badge>
```

## Performance Considerations

### Code Splitting
```tsx
// Lazy load Framer Motion
const MotionDiv = dynamic(() => 
  import('framer-motion').then(mod => mod.motion.div),
  { ssr: false }
);

// Lazy load charts
const RechartsChart = dynamic(() => import('./charts/RechartsChart'), {
  loading: () => <ChartSkeleton />,
});
```

### Bundle Optimization
- Use named imports: `import { Card } from '@/components/ui/card'`
- Tree-shake unused Lucide icons
- Minimize Framer Motion animations (use CSS when possible)
- Lazy load non-critical components

### Image Optimization
- Use Next.js Image component
- WebP format with fallbacks
- Proper sizing and lazy loading
- Placeholder blur for large images

## Testing Checklist

### Visual Regression
- [ ] Compare screenshots before/after
- [ ] Test all color variants
- [ ] Test all component states
- [ ] Test responsive breakpoints

### Functionality
- [ ] All Quick Win features work
- [ ] Sorting functions correctly
- [ ] Filters apply properly
- [ ] Charts render data accurately
- [ ] Loading states display

### Performance
- [ ] Lighthouse score > 85
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3s
- [ ] Bundle size increase < 50KB

### Accessibility
- [ ] Lighthouse accessibility > 90
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast passes WCAG AA
