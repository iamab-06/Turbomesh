# Frontend UI Preview - Deep Forensic Image Similarity

## Visual Layout

When a user completes an image similarity job, they'll see this rich, interactive UI:

---

### 1. **Verdict Header** (Top Banner)
```
┌─────────────────────────────────────────────────────────────────┐
│  CLASSIFICATION                              OVERALL SIMILARITY  │
│  ┌────────────────────────────────────┐           ┌───────┐     │
│  │ SAME_SUBJECT_DIFFERENT_POSE_AND_   │           │  78%  │     │
│  │ LIGHTING                           │           └───────┘     │
│  └────────────────────────────────────┘      Confidence: 94%    │
│                                                                  │
│  "The images show same subject different pose and lighting.     │
│   Deep semantic similarity is 0.92, while structural SSIM       │
│   is 0.26."                                                      │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- Color-coded classification badge (blue for same subject, yellow for related, red for unrelated)
- Large similarity percentage display
- Executive summary in readable prose

---

### 2. **Input Images Metadata** (Side-by-Side Cards)
```
┌──────────────────────────┐  ┌──────────────────────────┐
│ 📷 Image 1               │  │ 📷 Image 2               │
│ abhi1.jpg                │  │ abhi2.jpg                │
│ 1080x1920 • 9:16         │  │ 1080x1920 • 9:16         │
│ Colors: █ █ █            │  │ Colors: █ █ █            │
└──────────────────────────┘  └──────────────────────────┘
```

**Features:**
- Filename, resolution, and aspect ratio
- Dominant color swatches (actual hex colors rendered as small squares)

---

### 3. **Quantitative Metrics Grid** (6 Metric Cards)
```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ ResNet50    │ │ CLIP ViT    │ │ SSIM Score  │
│ Cosine      │ │ B/32        │ │             │
│   91.6%     │ │   94.1%     │ │   25.6%     │
└─────────────┘ └─────────────┘ └─────────────┘

┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ pHash       │ │ Color       │ │ ORB Inliers │
│ Similarity  │ │ Histogram   │ │             │
│   62.5%     │ │   81.2%     │ │     64      │
└─────────────┘ └─────────────┘ └─────────────┘
```

**Features:**
- Color-coded cards (blue for ResNet, purple for CLIP, green for SSIM, etc.)
- Large bold percentage or count display
- Responsive grid layout

---

### 4. **Visual Artifacts Gallery** (3 Side-by-Side Images)
```
┌─────────────────────────────────────────────────────────────────┐
│ 🔥 Grad-CAM Attention Heatmap                                   │
│ [Image: Two side-by-side activation heatmaps]                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 🌡️ SSIM Difference Heatmap                                      │
│ [Image: Color-mapped structural differences]                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 🔗 ORB Keypoint Matches                                         │
│ [Image: Green lines connecting matching keypoints]              │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- Full-width images with rounded corners
- Automatic scaling to fit viewport
- Descriptive titles with emoji icons

---

### 5. **Forensic Breakdown** (Two-Column Layout)
```
┌──────────────────────────────┐  ┌──────────────────────────────┐
│ ✅ What is Similar           │  │ ⚠️ What is Different         │
├──────────────────────────────┤  ├──────────────────────────────┤
│ Subject Identity (97%)       │  │ Pose / Angle (HIGH)          │
│ Deep semantic features       │  │ Significant structural       │
│ indicate the same subject.   │  │ difference detected.         │
│                              │  │                              │
│ Visual Structure (78%)       │  │ Lighting/Exposure (MEDIUM)   │
│ Perceptual hash shows        │  │ Notable lighting changes     │
│ similar patterns.            │  │ between images.              │
└──────────────────────────────┘  └──────────────────────────────┘
```

**Features:**
- Green-bordered cards for "Similar" (success color)
- Yellow-bordered cards for "Different" (warning color)
- Severity badges (HIGH/MEDIUM/LOW) on differences
- Confidence percentages on similarities

---

### 6. **Entity Diff Table** (Object Detection Integration)
```
┌─────────────────────────────────────────────────────────────────┐
│ 🔍 Detected Objects Comparison                                  │
├────────────────┬────────────────┬────────────────┐              │
│ Shared Objects │ Only in Image 1│ Only in Image 2│              │
├────────────────┼────────────────┼────────────────┤              │
│ [person (1)]   │ [gym_bag (1)]  │ [smartphone(1)]│              │
└────────────────┴────────────────┴────────────────┘              │
```

**Features:**
- Three-column comparison
- Color-coded object badges (green for shared, blue/purple for unique)
- Counts in parentheses

---

### 7. **Region-Level Scores** (Progress Bars)
```
┌─────────────────────────────────────────────────────────────────┐
│ 🎯 Region-Level Similarity Scores                               │
│                                                                  │
│ Foreground Subject Similarity               93.4%               │
│ ███████████████████████████████████████░░░░░                    │
│                                                                  │
│ Background Environment Similarity           61.2%               │
│ ████████████████████████░░░░░░░░░░░░░░░░░░░                    │
│                                                                  │
│ Lighting Consistency                        54.0%               │
│ ███████████████████░░░░░░░░░░░░░░░░░░░░░░░░                    │
│                                                                  │
│ Color Palette Match                         81.2%               │
│ ██████████████████████████████████░░░░░░░░░                     │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- Animated gradient progress bars (blue to purple)
- Percentage labels on the right
- Title-cased metric names

---

### 8. **P2P Telemetry Panel** (4-Metric Grid + Expandable Details)
```
┌─────────────────────────────────────────────────────────────────┐
│ ⚡ P2P GPU Telemetry                                            │
├───────────────┬───────────────┬───────────────┬─────────────────┤
│ Worker Node   │ GPU Hardware  │ Total GPU Time│ Speedup vs CPU  │
│ peer_0x94a8c1 │ RTX 4060 8GB  │ 650ms         │ 18.6x           │
└───────────────┴───────────────┴───────────────┴─────────────────┘
│                                                                  │
│ ▶ View Models Executed & Verification Hash                      │
│   Models: ResNet50-FeatureExtractor, OpenCV-ORB-RANSAC         │
│   Verification: sha256:a06946e727ab1668...                      │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- Compact 4-metric grid for key telemetry
- Expandable `<details>` section for models + verification hash
- Monospace font for hash values

---

### 9. **Raw JSON Viewer** (Collapsible)
```
┌─────────────────────────────────────────────────────────────────┐
│ ▶ View Raw JSON Response                                        │
│ {                                                                │
│   "job_id": "job_sim_99482a",                                   │
│   "operation": "deep_image_similarity",                          │
│   "inputs": { ... },                                             │
│   "verdict": { ... },                                            │
│   ...                                                            │
│ }                                                                │
└─────────────────────────────────────────────────────────────────┘
```

**Features:**
- Collapsed by default (click to expand)
- Syntax-highlighted JSON in monospace font
- Scrollable with max-height

---

## Color Palette

| Element | Color | Usage |
|---------|-------|-------|
| Near Duplicate | `#10b981` (Green) | High similarity classification |
| Same Subject | `#3b82f6` (Blue) | Moderate similarity |
| Related Scenes | `#f59e0b` (Yellow) | Low similarity |
| Unrelated | `#ef4444` (Red) | No similarity |
| Success | `#10b981` | Positive metrics, similarities |
| Warning | `#f59e0b` | Differences, alerts |
| Accent | `#8b5cf6` (Purple) | Highlights, secondary actions |

---

## Responsive Behavior

- **Desktop (>768px)**: Side-by-side layouts, full metric grids
- **Mobile (<768px)**: Stacked layouts, scrollable cards
- **Tablet (768px-1024px)**: Adaptive grid (2-column → 1-column)

---

## Interaction States

1. **Hover**: Metric cards lift with subtle shadow
2. **Expand**: Details sections slide open smoothly
3. **Load**: Smooth fade-in animation on result render
4. **Error**: Red border + error message for missing data

---

## Accessibility

- Semantic HTML (`<details>`, `<summary>`, proper headings)
- ARIA labels on progress bars
- High contrast text (WCAG AA compliant)
- Keyboard navigation support

---

## Example Screenshots

### Desktop View
```
┌───────────────────────────────────────────────────────────┐
│ TurboMesh User                                            │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  📊 Results                                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ [VERDICT HEADER - Full Width]                       │ │
│  ├────────────────┬────────────────────────────────────┤ │
│  │ [Image 1 Meta] │ [Image 2 Meta]                     │ │
│  ├────────────────┴────────────────────────────────────┤ │
│  │ [6-Metric Grid]                                     │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │ [Visual Artifacts - 3 images side-by-side]         │ │
│  ├────────────────┬────────────────────────────────────┤ │
│  │ [Similar Items]│ [Different Items]                  │ │
│  ├────────────────┴────────────────────────────────────┤ │
│  │ [Entity Diff Table]                                 │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │ [Region-Level Scores with Progress Bars]           │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │ [P2P Telemetry Panel]                              │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │ [Raw JSON - Collapsed]                             │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

### Mobile View
```
┌─────────────────────────┐
│ TurboMesh User          │
├─────────────────────────┤
│                         │
│ 📊 Results              │
│ ┌─────────────────────┐ │
│ │ [Verdict Header]    │ │
│ ├─────────────────────┤ │
│ │ [Image 1 Meta]      │ │
│ ├─────────────────────┤ │
│ │ [Image 2 Meta]      │ │
│ ├─────────────────────┤ │
│ │ [Metric 1]          │ │
│ │ [Metric 2]          │ │
│ │ [Metric 3]          │ │
│ │ ...                 │ │
│ ├─────────────────────┤ │
│ │ [Artifact 1]        │ │
│ │ [Artifact 2]        │ │
│ │ [Artifact 3]        │ │
│ ├─────────────────────┤ │
│ │ [Similar Items]     │ │
│ ├─────────────────────┤ │
│ │ [Different Items]   │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

---

## Performance

- **Initial Render**: <100ms (client-side only, no backend calls)
- **Image Loading**: Progressive (lazy load on scroll)
- **Animations**: 60fps CSS transitions
- **Bundle Size**: +12KB (custom renderer function)

---

## Browser Compatibility

✅ Chrome 90+  
✅ Firefox 88+  
✅ Safari 14+  
✅ Edge 90+  

⚠️ IE11 not supported (uses modern CSS Grid, flexbox, and ES6+)

---

**This UI provides a professional, information-dense, yet highly readable interface for forensic image analysis results.**
