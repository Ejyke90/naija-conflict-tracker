# Dashboard Component Guide

## Overview
This guide documents the reusable UI components built with **shadcn/ui** and **Framer Motion** for the Nigeria Conflict Tracker dashboard.

---

## Reusable Components

### 1. StatCard

**Location:** `src/components/ui/stat-card.tsx`

**Purpose:** Display key metrics with optional trends, sparklines, and icons.

**Props:**
```typescript
interface StatCardProps {
  title: string;                    // Card title
  value: number | string;           // Main value to display
  subtitle?: string;                // Optional subtitle
  icon?: LucideIcon;                // Icon component
  trend?: {
    direction: 'up' | 'down' | 'stable';
    percentage: number;
    label?: string;
  };
  sparklineData?: SparklineData[];  // Mini chart data
  variant?: 'default' | 'primary' | 'destructive' | 'success';
  className?: string;
}
```

**Usage Example:**
```tsx
import { StatCard } from '@/components/ui/stat-card';
import { TrendingUp } from 'lucide-react';

<StatCard
  title="Total Incidents"
  value={1234}
  subtitle="Last 30 days"
  icon={TrendingUp}
  variant="primary"
  trend={{
    direction: 'up',
    percentage: 12.5,
    label: 'vs last month'
  }}
  sparklineData={[
    { value: 10 },
    { value: 15 },
    { value: 12 },
    { value: 20 }
  ]}
/>
```

**Features:**
- ✅ Animated count-up on mount
- ✅ Color-coded trend badges (red=up, green=down, gray=stable)
- ✅ Optional sparkline chart
- ✅ Hover shadow effect
- ✅ Border variant highlighting

---

### 2. MetricDisplay

**Location:** `src/components/ui/metric-display.tsx`

**Purpose:** Animated number counter for large metrics.

**Props:**
```typescript
interface MetricDisplayProps {
  value: number;           // Number to display
  duration?: number;       // Animation duration (ms)
  suffix?: string;         // e.g., "%", "K"
  prefix?: string;         // e.g., "$", "#"
  formatLarge?: boolean;   // Convert 1000 → 1K, 1M
  decimals?: number;       // Decimal places
  colorByValue?: {
    threshold: number;
    above: string;         // CSS class if above threshold
    below: string;         // CSS class if below threshold
  };
}
```

**Usage Example:**
```tsx
import { MetricDisplay } from '@/components/ui/metric-display';

<MetricDisplay
  value={1500000}
  formatLarge={true}
  suffix=" people"
  duration={1500}
  colorByValue={{
    threshold: 1000000,
    above: 'text-red-600',
    below: 'text-green-600'
  }}
/>
// Displays: "1.5M people" in red
```

**Features:**
- ✅ Smooth count-up animation with ease-out curve
- ✅ Large number formatting (1K, 1M)
- ✅ Conditional color coding
- ✅ Tabular-nums for alignment

---

### 3. TrendBadge

**Location:** `src/components/ui/trend-badge.tsx`

**Purpose:** Color-coded trend indicator with arrows.

**Props:**
```typescript
interface TrendBadgeProps {
  direction: 'up' | 'down' | 'stable';
  value?: number;                  // Percentage or number
  label?: string;                  // e.g., "vs last month"
  variant?: 'default' | 'outline' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  showPercentage?: boolean;
  invertColors?: boolean;          // For cases where down is good
}
```

**Usage Example:**
```tsx
import { TrendBadge } from '@/components/ui/trend-badge';

// Standard usage (up=red, down=green)
<TrendBadge
  direction="up"
  value={15.2}
  label="this month"
  size="md"
/>

// Inverted (down=bad for fatalities)
<TrendBadge
  direction="down"
  value={-8.3}
  invertColors={true}
  size="lg"
/>
```

**Features:**
- ✅ TrendingUp/Down icons
- ✅ Auto color-coding (red/green/gray)
- ✅ Invert colors for metrics where down=good
- ✅ Responsive sizing

---

## Updated Dashboard Components

### StateAnalysis
**Location:** `src/components/dashboard/StateAnalysis.tsx`

**Improvements:**
- ✅ Card components for all sections
- ✅ Select dropdown for state selection
- ✅ Badge for risk levels (destructive variant)
- ✅ Skeleton loading states
- ✅ Staggered animations (0.1s, 0.2s, 0.3s, 0.4s delays)
- ✅ Hover effects on forecast cards

---

### MonthlyTrendsChart
**Location:** `components/charts/MonthlyTrendsChart.tsx`

**Improvements:**
- ✅ Card wrapper for chart
- ✅ Button for view mode toggle
- ✅ StatCard for summary metrics
- ✅ TrendBadge for trend direction
- ✅ Badge for forecast confidence levels
- ✅ Skeleton loading (4 metric placeholders + chart)
- ✅ Motion wrapper with fade-in

---

### PipelineMonitor
**Location:** `src/components/dashboard/PipelineMonitor.tsx`

**Improvements:**
- ✅ StatCard for overview metrics
- ✅ Card for pipeline steps with badges
- ✅ Progress component for success rates
- ✅ Badge for system health statuses
- ✅ Animated pulse on running steps
- ✅ Staggered step animations (0.1s per step)

---

## Animation Patterns

### Fade-in (Default)
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.4 }}
>
```

### Stagger Children
```tsx
{items.map((item, idx) => (
  <motion.div
    key={idx}
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay: idx * 0.1 }}
  >
))}
```

### Hover Effect
```tsx
<motion.div
  whileHover={{ scale: 1.02, y: -2 }}
  transition={{ duration: 0.2 }}
>
```

### Count-up Animation
```tsx
// Built into MetricDisplay component
<MetricDisplay value={1500} duration={1000} />
```

---

## Color Scheme

### shadcn/ui Design Tokens
```css
--primary: Neutral 900
--destructive: Red 500
--success: Green 500
--muted-foreground: Neutral 500

Light mode: Uses neutral grays
Dark mode: (To be implemented)
```

### Semantic Colors
- **Incidents:** Blue (#3b82f6)
- **Fatalities:** Red (#ef4444)
- **Success:** Green (#22c55e)
- **Warning:** Yellow (#eab308)
- **Neutral:** Gray (#6b7280)

---

## Responsive Breakpoints

```
Mobile:  < 768px  (1 column)
Tablet:  768px+   (2 columns)
Desktop: 1280px+  (3-4 columns)
```

**Grid Examples:**
```tsx
// 1 col mobile, 2 col tablet, 4 col desktop
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

// 1 col mobile, 3 col desktop
<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
```

---

## Accessibility

### ARIA Labels
All interactive components include proper ARIA labels:
```tsx
<Button aria-label="Filter by incidents">
<Badge aria-label="Risk level: High">
```

### Keyboard Navigation
- All buttons: `Tab` / `Shift+Tab`
- Select dropdowns: Arrow keys
- Cards: Focusable for screen readers

### Color Contrast
- Meets WCAG AA (4.5:1 for text)
- Badge variants use tested color combinations

---

## Performance

### Bundle Impact
```
StatCard:       ~2KB
MetricDisplay:  ~1KB
TrendBadge:     ~1KB
Total:          ~4KB gzipped
```

### Animation Performance
- Uses CSS transforms (GPU-accelerated)
- `framer-motion` tree-shaking enabled
- No layout thrashing

---

## Best Practices

### ✅ DO:
- Use StatCard for key metrics
- Use TrendBadge for comparisons
- Apply stagger delays (0.1s increments)
- Use Skeleton for loading states
- Apply hover effects on interactive cards

### ❌ DON'T:
- Nest motion.div > 3 levels deep (performance)
- Use inline styles for colors (use Tailwind)
- Hardcode breakpoints (use Tailwind responsive classes)
- Skip ARIA labels on custom components

---

## Migration Checklist

When converting a component to shadcn/ui:

- [ ] Replace `<div className="bg-white rounded-lg shadow">` with `<Card>`
- [ ] Replace `<h3>` with `<CardTitle>`
- [ ] Replace `<p className="text-gray-500">` with `<CardDescription>`
- [ ] Replace `<select>` with `<Select>` component
- [ ] Replace custom badges with `<Badge>`
- [ ] Wrap in `<motion.div>` for animations
- [ ] Add Skeleton for loading states
- [ ] Test keyboard navigation
- [ ] Check mobile responsiveness

---

## Future Enhancements

### Planned Features:
1. **Dark mode support** - Add dark mode toggle and theming
2. **Chart components** - Wrap Recharts in reusable Card components
3. **DataTable component** - Sortable, filterable tables with pagination
4. **Toast notifications** - Success/error feedback
5. **Dialog modals** - Conflict detail views
6. **Command palette** - Quick navigation (Cmd+K)

---

## Support

**Questions?** Check the [shadcn/ui docs](https://ui.shadcn.com)

**Found a bug?** Create an issue in the GitHub repo

**Component requests?** Discuss in team meetings
