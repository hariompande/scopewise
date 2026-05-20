# ScopeAI Design System

## Overview

The ScopeAI design system is an enterprise-grade component library built for a B2B SaaS project scoping tool. The design direction is **Enterprise/Corporate — Neutral, Professional**, with a refined utilitarian aesthetic inspired by Figma, Linear, and professional law firm portals.

**Design Philosophy:**
- Precision over decoration
- Trust and authority
- No playful, colorful, or consumer-app aesthetics
- No purple gradients
- Conservative border radius (max 6px)
- Subtle elevation only

---

## 1. Design Tokens

### Color Palette

#### Primary Colors (Professional Navy Blue)
- `--color-primary-50` to `--color-primary-900`
- Primary brand color: `--color-primary-500` (#486581)

#### Neutral Grays
- `--color-gray-50` to `--color-gray-900`
- Professional scale for backgrounds, borders, text

#### Semantic Colors
- **Success**: `--color-success-50` to `--color-success-900`
- **Warning**: `--color-warning-50` to `--color-warning-900`
- **Error**: `--color-error-50` to `--color-error-900`
- **Info**: `--color-info-50` to `--color-info-900`

### Typography Scale

#### Font Families (Premium Google Fonts)
- **Display**: Plus Jakarta Sans, Inter, SF Pro Display, system-ui, sans-serif
- **Heading**: Syne, Plus Jakarta Sans, system-ui, sans-serif  
- **Body**: Plus Jakarta Sans, Inter, SF Pro Text, system-ui, sans-serif
- **Mono**: JetBrains Mono, Fira Code, SF Mono, Consolas, monospace

**Why these fonts:**
- **Plus Jakarta Sans**: Commissioned by Google as their next-gen geometric sans. More distinctive than Inter with superior legibility at all sizes. The new premium SaaS standard.
- **Syne**: European avant-garde sans-serif with bold, architectural letterforms. Creates distinctive brand presence and authoritative B2B positioning. Perfect for headings that demand attention.
- **JetBrains Mono**: Purpose-built for developers with clear character distinction (0/O, 1/l/I). Excellent for code snippets and technical content.

#### Font Weights
- Light: 300
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700

#### Font Sizes
- **Display**: 40px, 48px, 60px, 72px, 96px
- **Heading**: 14px, 16px, 20px, 24px, 30px, 36px, 48px
- **Body**: 12px, 14px, 16px, 18px, 20px
- **Mono**: 12px, 14px, 16px, 18px

#### Line Heights
- Tight: 1.25
- Normal: 1.5
- Relaxed: 1.75
- Loose: 2.0

#### Letter Spacing
- Tight: -0.025em
- Normal: 0
- Wide: 0.025em
- Wider: 0.05em
- Widest: 0.1em

### Spacing Scale

4px base grid system:
- `--space-0`: 0
- `--space-1`: 4px
- `--space-2`: 8px
- `--space-3`: 12px
- `--space-4`: 16px
- `--space-5`: 20px
- `--space-6`: 24px
- `--space-8`: 32px
- `--space-10`: 40px
- `--space-12`: 48px
- `--space-16`: 64px
- `--space-20`: 80px
- `--space-24`: 96px
- `--space-32`: 128px

**T-shirt sizes:**
- xs: 8px
- sm: 16px
- md: 24px
- lg: 32px
- xl: 48px
- 2xl: 64px

### Border Radius

Conservative approach:
- `--radius-sm`: 2px
- `--radius-md`: 4px (inputs, buttons)
- `--radius-lg`: 6px (cards)
- `--radius-full`: 9999px (avatars, badges)

### Shadow Levels

Subtle elevation only (3 levels max):
- `--shadow-xs`: 0 1px 2px 0 rgba(0, 0, 0, 0.05)
- `--shadow-sm`: 0 1px 3px 0 rgba(0, 0, 0, 0.1)
- `--shadow-md`: 0 4px 6px -1px rgba(0, 0, 0, 0.1)
- `--shadow-lg`: 0 10px 15px -3px rgba(0, 0, 0, 0.1)
- `--shadow-focus`: 0 0 0 3px rgba(72, 101, 129, 0.3)

### Transition Timing

#### Duration
- Instant: 100ms
- Fast: 150ms
- Normal: 200ms
- Slow: 300ms
- Slower: 500ms

#### Easing
- In: cubic-bezier(0.4, 0, 1, 1)
- Out: cubic-bezier(0, 0, 0.2, 1)
- In-Out: cubic-bezier(0.4, 0, 0.2, 1)

#### Standard Transitions
- Fast: 150ms ease-out
- Normal: 200ms ease-in-out
- Slow: 300ms ease-in-out

### Z-Index Scale

- Dropdown: 1000
- Sticky: 1020
- Fixed: 1030
- Modal Backdrop: 1040
- Modal: 1050
- Popover: 1060
- Tooltip: 1070
- Toast: 1080

---

## 2. Component Inventory

### Client Form Components

#### StepIndicator
**Purpose:** Visual progress indicator for multi-step forms

**Props:**
- `steps: Step[]` - Array of step objects with id, label, completed, current

**States:**
- Completed (checkmark)
- Current (highlighted)
- Pending (number)

**Design Notes:**
- Horizontal track line
- Circular indicators
- Smooth transitions between states

#### FormSection
**Purpose:** Groups related form fields with label and optional helper text

**Props:**
- `label?: string`
- `helper?: string`
- `required?: boolean`

**Design Notes:**
- Optional asterisk for required fields
- Helper text in smaller, muted color

#### TextInput
**Purpose:** Standard text input field

**Props:**
- `modelValue: string`
- `type?: 'text' | 'email' | 'tel' | 'url' | 'password'`
- `placeholder?: string`
- `disabled?: boolean`
- `readonly?: boolean`
- `error?: string`
- `id?: string`
- `name?: string`

**States:**
- Default
- Hover
- Focus (with focus ring)
- Error (red border + error message)
- Disabled

#### FormTextarea
**Purpose:** Multi-line text input

**Props:**
- `modelValue: string`
- `placeholder?: string`
- `disabled?: boolean`
- `readonly?: boolean`
- `error?: string`
- `rows?: number`
- `resize?: 'none' | 'vertical' | 'horizontal' | 'both'`

**States:** Same as TextInput

#### SelectDropdown
**Purpose:** Dropdown selection with custom arrow

**Props:**
- `modelValue: string`
- `options: Option[]`
- `placeholder?: string`
- `disabled?: boolean`
- `error?: string`

**Design Notes:**
- Custom dropdown arrow icon
- Placeholder styling

#### MultiSelectChip
**Purpose:** Select multiple options as chips

**Props:**
- `modelValue: string[]`
- `options: Option[]`
- `disabled?: boolean`
- `error?: string`

**States:**
- Unselected (outline)
- Selected (filled with primary color + remove icon)

#### BudgetRangeSelector
**Purpose:** Visual budget range selection (not a raw slider)

**Props:**
- `modelValue: string`
- `options: RangeOption[]`
- `disabled?: boolean`
- `error?: string`

**Design Notes:**
- Card-style options
- Grid layout
- Selected state with checkmark

#### RadioCardGroup
**Purpose:** Card-style radio selection for project types

**Props:**
- `modelValue: string`
- `options: CardOption[]`
- `disabled?: boolean`
- `error?: string`

**Design Notes:**
- Large cards with icon, title, description
- Selected state with checkmark
- Not traditional radio dots

#### FormNavigator
**Purpose:** Back/Continue/Submit navigation for multi-step forms

**Props:**
- `currentStep: number`
- `totalSteps: number`
- `canGoBack: boolean`
- `canContinue: boolean`
- `isSubmitting?: boolean`
- `submitLabel?: string`

**States:**
- Loading spinner on submit button
- Disabled states for back/continue

### PM Dashboard Components

#### SidebarNav
**Purpose:** Collapsible sidebar navigation

**Props:**
- `items: NavItem[]`
- `collapsed?: boolean`

**Design Notes:**
- Fixed position
- Toggle button
- Badge support
- Active state highlighting

#### ScopeRequestCard
**Purpose:** List item for scope requests

**Props:**
- `id: string`
- `clientName: string`
- `projectName: string`
- `status: 'new' | 'in-review' | 'approved' | 'sent'`
- `date: string`
- `riskLevel?: 'low' | 'medium' | 'high'`

**Design Notes:**
- Card with hover effect
- Status badge
- Risk flag
- Clickable

#### StatusBadge
**Purpose:** Display request status

**Props:**
- `status: 'new' | 'in-review' | 'approved' | 'sent'`

**States:**
- New (blue)
- In Review (yellow)
- Approved (green)
- Sent (primary)

#### RiskFlag
**Purpose:** Inline warning chip for risk levels

**Props:**
- `level: 'low' | 'medium' | 'high'`

**States:**
- Low (green with checkmark)
- Medium (yellow with exclamation)
- High (red with warning symbol)

#### ScopeSectionBlock
**Purpose:** Editable card for AI-generated scope sections

**Props:**
- `title: string`
- `content: string`
- `editable?: boolean`
- `isStreaming?: boolean`

**Design Notes:**
- Edit button
- Streaming text support
- Inline edit mode

#### StreamingTextBlock
**Purpose:** Shows AI text streaming with typing animation

**Props:**
- `content: string`
- `streamingSpeed?: number`

**Design Notes:**
- Character-by-character reveal
- Blinking cursor
- Configurable speed

#### InlineEditField
**Purpose:** Click-to-edit text field

**Props:**
- `modelValue: string`

**Design Notes:**
- Display mode with edit button
- Edit mode with textarea
- Save/Cancel buttons
- Keyboard shortcuts (Cmd/Ctrl+S to save, Esc to cancel)

#### PricingPanel
**Purpose:** Sidebar panel for pricing calculations

**Props:**
- `lineItems: LineItem[]`
- `margin?: number`
- `currency?: string`
- `editable?: boolean`

**Design Notes:**
- Line items list
- Subtotal, margin, total
- Editable margin input
- Sticky positioning
- Currency formatting

#### ApproveAndSendButton
**Purpose:** Primary CTA with confirmation modal

**Props:**
- `disabled?: boolean`
- `loading?: boolean`

**Design Notes:**
- Success color
- Loading spinner
- Confirmation modal trigger

#### ConfirmationModal
**Purpose:** Modal for confirming destructive actions

**Props:**
- `title: string`
- `message: string`
- `confirmLabel?: string`
- `cancelLabel?: string`
- `loading?: boolean`

**Design Notes:**
- Teleport to body
- Backdrop click to cancel
- Escape key to cancel
- Loading state on confirm button

### Shared/Global Components

#### TopBar
**Purpose:** Fixed top navigation bar

**Props:**
- `logo?: string`
- `userName?: string`
- `userAvatar?: string`
- `notificationCount?: number`

**Design Notes:**
- Logo on left
- Theme toggle, notifications, avatar on right
- Notification badge
- Avatar with initials fallback

#### PageHeader
**Purpose:** Page title with optional actions

**Props:**
- `title: string`
- `subtitle?: string`
- `actions?: boolean`

**Design Notes:**
- Heading font family
- Actions slot on right
- Bottom border

#### AppDivider
**Purpose:** Horizontal or vertical divider

**Props:**
- `label?: string`
- `orientation?: 'horizontal' | 'vertical'`

**Design Notes:**
- Optional centered label
- ARIA separator role

#### EmptyState
**Purpose:** Empty state with icon, message, and optional CTA

**Props:**
- `icon?: string`
- `title: string`
- `message: string`
- `actionLabel?: string`

**Design Notes:**
- Default icon provided
- Action button emits event

#### AppToast
**Purpose:** Notification toast

**Props:**
- `type?: 'success' | 'error' | 'warning' | 'info'`
- `title?: string`
- `message: string`
- `duration?: number`
- `closable?: boolean`

**States:**
- Success (green)
- Error (red)
- Warning (yellow)
- Info (blue)

**Design Notes:**
- Auto-dismiss after duration
- Slide in animation
- Close button

#### LoadingSpinner
**Purpose:** Loading indicator

**Props:**
- `size?: 'sm' | 'md' | 'lg'`
- `color?: 'primary' | 'secondary'`

**Design Notes:**
- SVG animation
- Multiple sizes

#### SkeletonBlock
**Purpose:** Content placeholder while loading

**Props:**
- `width?: string | number`
- `height?: string | number`
- `variant?: 'text' | 'rectangular' | 'circular'`
- `animation?: 'pulse' | 'wave' | 'none'`

**Design Notes:**
- Pulse or wave animation
- Multiple variants

#### AppTooltip
**Purpose:** Tooltip on hover/focus

**Props:**
- `content: string`
- `position?: 'top' | 'bottom' | 'left' | 'right'`
- `delay?: number`

**Design Notes:**
- Delayed appearance
- Four positions
- Fade animation

#### AppAvatar
**Purpose:** User avatar with initials fallback

**Props:**
- `src?: string`
- `alt?: string`
- `name?: string`
- `size?: 'sm' | 'md' | 'lg' | 'xl'`

**Design Notes:**
- Image or initials
- Placeholder icon
- Multiple sizes

### Layout Components

#### DashboardLayout
**Purpose:** Main dashboard layout with sidebar

**Props:**
- `sidebarItems: NavItem[]`
- `sidebarCollapsed?: boolean`
- `userName?: string`
- `userAvatar?: string`
- `notificationCount?: number`

**Design Notes:**
- Fixed TopBar
- Fixed SidebarNav
- Main content area
- Responsive sidebar collapse

#### FormLayout
**Purpose:** Centered single-column form layout

**Props:**
- `maxWidth?: string`

**Design Notes:**
- Centered container
- Max-width constraint (default 640px)
- Card-style container

#### ScopeReviewLayout
**Purpose:** Two-column scope review layout

**Props:**
- `showPricingPanel?: boolean`

**Design Notes:**
- Scope sections: 65%
- Pricing panel: 35%
- Responsive: stacks on mobile

---

## 3. Layout Specifications

### Max Content Width
- `--max-content-width`: 1280px
- `--max-form-width`: 640px
- `--max-narrow-width`: 768px

### Page Grid
- Columns: 12
- Gutter: 32px (--space-8)

### Client Form Layout
- Centered single-column
- Max-width: 640px
- Step-by-step progression
- One section visible at a time
- Card-style container with shadow

### PM Dashboard Layout
- Fixed sidebar: 240px (--sidebar-width)
- Collapsed sidebar: 64px (--sidebar-collapsed-width)
- Top bar: 56px (--topbar-height) fixed
- Main content: fluid width with padding

### Scope Review Layout
- Two-column grid:
  - Scope sections: 65% width
  - Pricing panel: 35% width
- Responsive: stacks to single column on mobile
- Pricing panel: sticky positioning

---

## 4. Interaction & Motion Principles

### Form Step Transitions
- **Type:** Fade transition
- **Direction:** None (fade in/out)
- **Duration:** 200ms
- **Easing:** ease-in-out
- **Implementation:** Vue Transition with fade mode

### SSE Streaming Text Reveal
- **Type:** Character-by-character typing
- **Animation:** Blinking cursor
- **Speed:** Configurable (default 20ms per character)
- **Implementation:** setInterval with cursor CSS animation

### Hover/Focus States
- **Hover:**
  - Background color change (lighter shade)
  - Border color darken
  - Transition: 150ms ease-out
- **Focus:**
  - Focus ring: 0 0 0 2px bg-color, 0 0 0 4px primary-500
  - Border color change to primary-500
  - Transition: 150ms ease-out

### Loading States
- **Skeleton:**
  - Use for content loading (lists, cards)
  - Pulse or wave animation
  - Match content shape
- **Spinner:**
  - Use for button actions, async operations
  - Small inline spinner
  - SVG animation

### Error States
- **Inline:**
  - Form field validation errors
  - Display below field
  - Red text with icon
- **Toast:**
  - Global errors, success messages
  - Top-right position
  - Auto-dismiss

---

## 5. Accessibility Baseline

### Contrast Ratios
- **Target:** WCAG AA minimum (4.5:1 for normal text, 3:1 for large text)
- **Primary text:** 4.5:1 or higher
- **Secondary text:** 4.5:1 or higher
- **Interactive elements:** 3:1 or higher
- **Status badges:** 3:1 or higher

### Focus Ring Style
- **Style:** Double ring
- **Inner:** 2px background color
- **Outer:** 4px primary-500
- **Offset:** 0px from element
- **Implementation:** CSS variable `--focus-ring`

### Form Field Label Association
- **Required:** All form inputs must have associated labels
- **Method:** `for` attribute on label matches input `id`
- **Aria:** `aria-describedby` for error messages
- **Validation:** `aria-invalid="true"` on error state

### ARIA Roles for Streaming Content
- **Live Regions:** `aria-live="polite"` for streaming text
- **Assertive:** `aria-live="assertive"` for error messages
- **Status:** `role="status"` for loading states
- **Progress:** `role="progressbar"` for step indicators

### Keyboard Navigation
- **Tab:** Logical tab order through interactive elements
- **Enter/Space:** Activate buttons, links
- **Escape:** Close modals, cancel operations
- **Arrow keys:** Navigate within components (dropdowns, radios)
- **Cmd/Ctrl+S:** Save in inline edit
- **Cmd/Ctrl+Enter:** Submit forms

---

## 6. Dark/Light Theme

### Theme Switching
- **Implementation:** CSS custom properties with data-theme attribute
- **Default:** System preference (prefers-color-scheme)
- **Persistence:** localStorage key 'scopeai-theme'
- **Toggle:** Button in TopBar

### Light Theme Variables
- Backgrounds: White to light gray
- Text: Dark gray to black
- Borders: Light gray
- Shadows: Black with low opacity

### Dark Theme Variables
- Backgrounds: Dark blue/gray spectrum
- Text: Light gray to white
- Borders: Medium gray
- Shadows: Black with higher opacity

### Semantic Color Adaptation
- Status colors adjust opacity in dark mode
- Primary color shifts to lighter shade
- All components support both themes seamlessly

---

## 7. Component Usage Examples

### Using the Theme Store
```typescript
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

// Initialize on app mount
themeStore.initializeTheme()

// Toggle theme
themeStore.toggleTheme()

// Set specific theme
themeStore.setTheme(true) // dark
themeStore.setTheme(false) // light
```

### Client Form Example
```vue
<template>
  <FormLayout>
    <StepIndicator :steps="steps" />
    
    <FormSection label="Project Name" required>
      TextInput v-model="projectName" placeholder="Enter project name" />
    </FormSection>
    
    <FormSection label="Project Type" required>
      <RadioCardGroup
        v-model="projectType"
        :options="projectTypes"
      />
    </FormSection>
    
    <FormNavigator
      :current-step="currentStep"
      :total-steps="totalSteps"
      :can-go-back="currentStep > 1"
      :can-continue="isValid"
      :is-submitting="isSubmitting"
      @back="handleBack"
      @continue="handleContinue"
      @submit="handleSubmit"
    />
  </FormLayout>
</template>
```

### Dashboard Example
```vue
<template>
  <DashboardLayout
    :sidebar-items="navItems"
    :user-name="userName"
    :notification-count="notifications"
    @sidebar-navigate="handleNavigate"
  >
    <PageHeader
      title="Scope Requests"
      subtitle="Review and manage incoming project scopes"
    >
      <template #actions>
        <button>Filter</button>
      </template>
    </PageHeader>
    
    <div class="scope-list">
      <ScopeRequestCard
        v-for="request in requests"
        :key="request.id"
        v-bind="request"
        @click="handleViewRequest"
      />
    </div>
  </DashboardLayout>
</template>
```

### Scope Review Example
```vue
<template>
  <ScopeReviewLayout>
    <template #sections>
      <ScopeSectionBlock
        v-for="section in scopeSections"
        :key="section.id"
        v-bind="section"
        :editable="true"
        :is-streaming="isStreaming"
        @save="handleSaveSection"
      />
    </template>
    
    <template #pricing>
      <PricingPanel
        :line-items="lineItems"
        :margin="margin"
        :editable="true"
        @update:margin="handleMarginChange"
      />
      
      <ApproveAndSendButton
        :disabled="!isValid"
        :loading="isSending"
        @click="handleApproveAndSend"
      />
    </template>
  </ScopeReviewLayout>
</template>
```

---

## 8. File Structure

```
src/
├── assets/
│   ├── design-tokens.css      # All CSS custom properties
│   └── main.css               # Imports design tokens + Tailwind
├── components/
│   ├── shared/                # Global components
│   │   ├── TopBar.vue
│   │   ├── PageHeader.vue
│   │   ├── AppDivider.vue
│   │   ├── EmptyState.vue
│   │   ├── AppToast.vue
│   │   ├── LoadingSpinner.vue
│   │   ├── SkeletonBlock.vue
│   │   ├── AppTooltip.vue
│   │   └── AppAvatar.vue
│   ├── form/                  # Client form components
│   │   ├── StepIndicator.vue
│   │   ├── FormSection.vue
│   │   ├── TextInput.vue
│   │   ├── FormTextarea.vue
│   │   ├── SelectDropdown.vue
│   │   ├── MultiSelectChip.vue
│   │   ├── BudgetRangeSelector.vue
│   │   ├── RadioCardGroup.vue
│   │   └── FormNavigator.vue
│   ├── dashboard/             # PM dashboard components
│   │   ├── SidebarNav.vue
│   │   ├── ScopeRequestCard.vue
│   │   ├── StatusBadge.vue
│   │   ├── RiskFlag.vue
│   │   ├── ScopeSectionBlock.vue
│   │   ├── StreamingTextBlock.vue
│   │   ├── InlineEditField.vue
│   │   ├── PricingPanel.vue
│   │   ├── ApproveAndSendButton.vue
│   │   └── ConfirmationModal.vue
│   └── layout/                # Layout components
│       ├── DashboardLayout.vue
│       ├── FormLayout.vue
│       └── ScopeReviewLayout.vue
├── composables/
│   └── useTheme.ts            # Theme composable
└── stores/
    └── theme.ts               # Theme Pinia store
```

---

## 9. Tailwind Configuration

The Tailwind config is extended to use CSS custom properties defined in `design-tokens.css`. This allows for:
- Seamless theme switching
- Design token consistency
- Dark mode support via class strategy

Key extensions:
- Colors: primary, gray, success, warning, error, info
- Font families: display, heading, body, mono
- Font sizes: display-xs through display-xl
- Spacing: xs through 2xl (t-shirt sizes)
- Border radius: sm, md, lg
- Box shadow: xs, sm, md, lg, focus
- Transition duration: instant, fast, slow, slower
- Transition timing: in, out, in-out, bounce
- Z-index: dropdown, sticky, fixed, modal-backdrop, modal, popover, tooltip, toast

---

## 10. Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS custom properties (CSS variables)
- CSS Grid and Flexbox
- ES6+ JavaScript features

---

## 11. Future Enhancements

- [ ] Add Storybook for component documentation
- [ ] Add unit tests for components
- [ ] Add E2E tests for critical user flows
- [ ] Add more animation variants
- [ ] Add additional layout patterns
- [ ] Add date/time picker components
- [ ] Add file upload component
- [ ] Add data table component
- [ ] Add pagination component
- [ ] Add search/filter components
