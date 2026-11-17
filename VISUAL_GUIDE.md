# TurboMesh - Visual Design Guide

## 🎨 Design System

### Color Palette Reference

#### Primary Colors
```
Primary Blue      #3b82f6  ████  Main actions, links, primary CTA
Accent Purple     #8b5cf6  ████  Highlights, secondary accents
Success Green     #10b981  ████  Approved, positive, success states
Warning Amber     #f59e0b  ████  Pending, attention, warnings
Danger Red        #ef4444  ████  Errors, destructive, danger
```

#### Background Colors
```
Dark Background   #0f172a  ████  Page background (darkest)
Card Background   #1e293b  ████  Card/container background
Border Color      #334155  ████  Subtle borders and dividers
Input Background  rgba(59,130,246,0.05) - Input field background
```

#### Text Colors
```
Primary Text      #f1f5f9  ████  Main content text
Secondary Text    #cbd5e1  ████  Secondary content
Muted Text        #94a3b8  ████  Labels, hints, disabled
```

---

## 📐 Typography System

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
             'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
```

### Font Sizes
```
Tiny     0.75rem  (12px)   - Labels, hints, small text
XSmall   0.8125rem (13px)  - Small labels, badges
Small    0.875rem  (14px)  - Secondary text, form labels
Base     0.95rem   (15px)  - Body text, inputs
Normal   1rem      (16px)  - Normal text
Large    1.0625rem (17px)  - Value text
XLarge   1.125rem  (18px)  - Subheadings
2XL      1.25rem   (20px)  - Card titles
3XL      1.75rem   (28px)  - Section titles
4XL      2.25rem   (36px)  - Page titles
```

### Font Weights
```
Regular  400  - Body text
Medium   500  - Secondary labels
SemiBold 600  - Card titles, buttons, strong text
Bold     700  - Headers, prominent text
```

### Line Height
```
1.6  - Normal reading (main content)
1.5  - Compact (labels, UI)
1.2  - Headings
```

### Letter Spacing
```
Normal    0      - Body text
Relaxed   0.5px  - Labels, buttons
Wide      8px    - Pairing code display
```

---

## 📏 Spacing Grid

Base unit: **8px**

### Common Sizes
```
4px    - Micro spacing (rarely used)
8px    - XSmall (button padding)
12px   - Small (form gaps)
16px   - Normal (standard padding)
20px   - Medium (card padding)
24px   - Large (section padding)
32px   - XLarge (major spacing)
40px   - XXLarge (header spacing)
```

### Application
```
Card Padding      16px - 24px
Button Padding    10px - 20px (vertical) × 16px - 20px (horizontal)
Input Padding     12px × 14px
Gap Between       12px - 24px
Margin Bottom     12px - 40px
```

---

## 🎯 Component Styles

### Buttons

#### Primary Button
```css
Background:    var(--primary) #3b82f6
Color:         white
Padding:       12px 20px
Border-radius: 8px
Font-weight:   600
Font-size:     0.875rem
Letter-spacing: 0.5px
Cursor:        pointer
Transition:    all 0.2s ease

/* Hover State */
Background:    var(--primary-hover) #2563eb
Box-shadow:    0 4px 12px rgba(59, 130, 246, 0.4)

/* Active State */
Transform:     scale(0.98)

/* Disabled State */
Background:    #475569
Opacity:       0.6
Cursor:        not-allowed
```

#### Danger Button
```css
Background:    rgba(239, 68, 68, 0.1)
Color:         #fca5a5
Border:        1px solid rgba(239, 68, 68, 0.3)

/* Hover State */
Background:    rgba(239, 68, 68, 0.2)
Border-color:  var(--danger) #ef4444
```

### Form Inputs

#### Text Input / Select
```css
Background:    rgba(59, 130, 246, 0.05)
Color:         var(--text-primary)
Border:        1px solid var(--border-color)
Padding:       12px 14px
Border-radius: 8px
Font-size:     0.95rem
Transition:    all 0.2s ease

/* Focus State */
Outline:       none
Border-color:  var(--primary)
Background:    rgba(59, 130, 246, 0.08)
Box-shadow:    0 0 0 3px rgba(59, 130, 246, 0.1)
```

#### File Input
```css
Border:        2px dashed var(--border-color)
Padding:       12px 14px
Background:    rgba(59, 130, 246, 0.05)

/* Hover State */
Border-color:  var(--primary)
Background:    rgba(59, 130, 246, 0.08)
```

### Cards

#### Basic Card
```css
Background:       var(--card-bg) #1e293b
Border:           1px solid var(--border-color)
Border-radius:    12px
Padding:          24px
Box-shadow:       0 1px 3px rgba(0, 0, 0, 0.1)
Transition:       all 0.3s ease

/* Hover State */
Border-color:     var(--primary)
Box-shadow:       0 4px 20px rgba(59, 130, 246, 0.1)
```

### Status Badges

#### Success Badge
```css
Background:    rgba(16, 185, 129, 0.1)
Border:        1px solid rgba(16, 185, 129, 0.3)
Color:         #86efac
Padding:       8px 16px
Border-radius: 8px
Font-size:     0.875rem
```

#### Warning Badge
```css
Background:    rgba(245, 158, 11, 0.1)
Border:        1px solid rgba(245, 158, 11, 0.3)
Color:         #fcd34d
```

#### Error Badge
```css
Background:    rgba(239, 68, 68, 0.1)
Border:        1px solid rgba(239, 68, 68, 0.3)
Color:         #fca5a5
```

### Progress Bar

#### Container
```css
Width:         100%
Height:        6px
Background:    rgba(59, 130, 246, 0.1)
Border-radius: 3px
Overflow:      hidden
```

#### Fill
```css
Height:        100%
Background:    linear-gradient(90deg, var(--primary), var(--accent))
Width:         0% (0-100% animated)
Transition:    width 0.3s ease
Border-radius: 3px
```

---

## 🎬 Animation & Transitions

### Duration Standards
```
Micro    150ms - Hover state changes
Short    200ms - Button feedback
Normal   300ms - Card transitions
Long     500ms - Modal animations
```

### Easing
```
Default         ease
Fast In/Out     ease-in-out
Smooth          cubic-bezier(0.4, 0, 0.2, 1)
Linear          linear
```

### Common Animations

#### Hover Effects
```css
transition: all 0.2s ease;
```

#### Pulse Animation
```css
animation: pulse 2s infinite;

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

#### Scale On Active
```css
transform: scale(0.98);
```

---

## 📱 Responsive Design

### Breakpoints
```
Mobile:  < 768px    - Single column, optimized
Tablet:  768px-1199px - Flexible 2-column
Desktop: 1200px+    - Full multi-column
```

### Mobile Optimizations
```
Font Size (body):  Minimum 14px
Line Height:       1.6 for readability
Button Height:     Minimum 44px (touch target)
Padding:           16px (edges)
Column Gap:        12px
Touch Padding:     8px around interactive elements
```

### Container Queries
```css
/* Desktop */
max-width: 1200px
margin: 0 auto
padding: 24px

/* Tablet */
@media (max-width: 1023px) {
  grid-template-columns: 1fr;
  max-width: 100%;
  padding: 16px;
}

/* Mobile */
@media (max-width: 767px) {
  padding: 12px;
  font-size: 0.875rem;
}
```

---

## ♿ Accessibility Features

### Color Contrast Ratios
```
WCAG AA: 4.5:1 minimum for text
Large text (18pt+): 3:1 minimum
UI components: 3:1 minimum
```

### Focus Indicators
```css
focus {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Or with box-shadow */
focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
  border-color: var(--primary);
}
```

### Text Sizing
```
Never fixed width (no px units for body)
Use rem for scalable text
Minimum 14px on mobile
Support 200% zoom
Allow text reflow
```

---

## 🎨 Special Effects

### Gradient Text
```css
background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;
```

### Glass Morphism (Subtle)
```css
background: rgba(255, 255, 255, 0.05);
backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.1);
```

### Shadow Hierarchy
```
Small:    0 1px 3px rgba(0, 0, 0, 0.1)
Medium:   0 4px 6px rgba(0, 0, 0, 0.1)
Large:    0 4px 20px rgba(59, 130, 246, 0.1)
XLarge:   0 10px 40px rgba(0, 0, 0, 0.2)
```

---

## 🔍 Visual Hierarchy Examples

### Primary Information
```
Font Size:     1.75rem - 2.25rem
Font Weight:   700 (Bold)
Color:         var(--text-primary) #f1f5f9
Spacing:       40px margin
```

### Secondary Information
```
Font Size:     1rem - 1.125rem
Font Weight:   600 (SemiBold)
Color:         var(--text-primary)
Spacing:       24px margin
```

### Tertiary Information
```
Font Size:     0.875rem - 0.95rem
Font Weight:   500 (Medium)
Color:         var(--text-muted)
Spacing:       12px margin
```

### Meta/Labels
```
Font Size:     0.75rem - 0.8125rem
Font Weight:   600 (SemiBold)
Color:         var(--text-muted)
Transform:     uppercase
Letter-spacing: 0.5px
Spacing:       8px margin
```

---

## 📋 Implementation Checklist

When implementing new components:

- [ ] Use CSS variables for colors
- [ ] Apply consistent spacing (8px grid)
- [ ] Include hover/active/focus states
- [ ] Ensure 4.5:1 contrast ratio
- [ ] Add smooth transitions (0.2s-0.3s)
- [ ] Mobile-first responsive design
- [ ] Accessible focus indicators
- [ ] Touch-friendly sizing (44px min)
- [ ] Proper semantic HTML
- [ ] Clear visual hierarchy

---

## 🎯 Quick Reference

### Color Quick Pick
- **Call to Action** → #3b82f6 (Primary Blue)
- **Highlights** → #8b5cf6 (Accent Purple)
- **Success/Approve** → #10b981 (Green)
- **Warnings/Pending** → #f59e0b (Amber)
- **Errors/Delete** → #ef4444 (Red)

### Spacing Quick Pick
- **Compact** → 8px, 12px
- **Normal** → 16px, 20px
- **Generous** → 24px, 32px

### Typography Quick Pick
- **Labels** → 0.75rem, 600 weight, uppercase
- **Body** → 0.95rem, 400 weight
- **Headings** → 1.25rem+, 600-700 weight
- **Accents** → 1.75rem+, 700 weight

---

## 📚 Design References

This design system follows:
- Material Design 3 principles
- Apple Human Interface Guidelines
- WCAG 2.1 AA Accessibility Standards
- Modern Web Design Best Practices

