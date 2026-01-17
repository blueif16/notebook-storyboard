# Storybook Component Architecture

## Component Tree

```
StorybookFlow (Main Orchestrator)
│
├── AnimatePresence (Framer Motion)
│   │
│   ├── LandingPage
│   │   ├── FloatingDecorations
│   │   │   ├── Cloud (icons/cloud.png)
│   │   │   └── Stars (icons/stars.png x3)
│   │   ├── Hero Image (hero1.jpeg)
│   │   ├── Headline (GSAP char animation)
│   │   ├── Subtext
│   │   └── WobblyButton
│   │       └── Magic Wand (icons/magic_wand.png)
│   │
│   ├── StyleConfigPage
│   │   ├── ProgressIndicator (step 1)
│   │   ├── Config Card
│   │   │   ├── Paintbrush Icon (icons/paintbrush.png)
│   │   │   ├── Style Options (4 buttons)
│   │   │   ├── Voice Recording
│   │   │   │   ├── Microphone (icons/microphone.png)
│   │   │   │   └── Sound Waves (animated)
│   │   │   └── Musical Notes (icons/music-notes.png)
│   │   └── Navigation
│   │       ├── Home Button (icons/home.png)
│   │       └── Next Button (icons/right_arrow.png)
│   │
│   ├── BriefInputPage
│   │   ├── ProgressIndicator (step 2)
│   │   ├── Brief Card
│   │   │   ├── Pencil Icon (icons/pencil.png)
│   │   │   ├── Textarea (typing placeholder)
│   │   │   └── Swirl Decoration (icons/swirl.png)
│   │   ├── Submit Area
│   │   │   ├── Stars (icons/stars.png x3, twinkling)
│   │   │   └── WobblyButton
│   │   │       └── Magic Wand (icons/magic_wand.png)
│   │   └── Navigation
│   │       └── Back Button (icons/home.png)
│   │
│   ├── GenerationLoading
│   │   ├── Moon (icons/moon.png, rocking)
│   │   ├── Stars Cluster (icons/stars.png x5, twinkling)
│   │   ├── Swirl (icons/swirl.png, rotating)
│   │   ├── Dots Cluster (4 dots, pulsing)
│   │   └── Loading Message (cycling text)
│   │
│   ├── CharacterApproval
│   │   ├── ProgressIndicator (step 3)
│   │   ├── Character Stage
│   │   │   ├── Glow Effect (pulsing)
│   │   │   ├── Character Frame
│   │   │   │   └── Character Image (hero2.jpeg)
│   │   │   ├── Burst Stars (icons/stars.png x5)
│   │   │   └── Flower Accent (icons/flower.png)
│   │   └── Action Buttons
│   │       ├── Try Again Button
│   │       │   └── Refresh Icon (icons/refresh_arrows.png)
│   │       └── Approve Button (WobblyButton)
│   │           ├── Checkmark (icons/checkmark.png)
│   │           └── Heart (icons/heart.png)
│   │
│   └── StoryReader
│       ├── Header (fading)
│       │   ├── Home Button (icons/home.png)
│       │   └── Page Counter
│       ├── Story Stage (AnimatePresence)
│       │   └── Story Page (3D rotation)
│       │       ├── Illustration Frame
│       │       │   └── Story Image (hero1/hero2.jpeg)
│       │       └── Story Text Container
│       │           └── Story Text
│       ├── Navigation
│       │   ├── Previous Arrow (icons/right_arrow.png rotated)
│       │   ├── Page Dots (dynamic)
│       │   └── Next Arrow (icons/right_arrow.png)
│       └── TheEndCelebration (conditional)
│           ├── Confetti Container (30 pieces)
│           ├── Stars (icons/stars.png x3)
│           ├── "The End" Text
│           ├── Flower (icons/flower.png)
│           └── End Actions
│               ├── Read Again (icons/open_book.png)
│               ├── Make Another (icons/magic_wand.png)
│               └── Go Home (icons/home.png)
```

## State Flow

```
[Landing]
    ↓ onBegin()
[Style Config]
    ↓ onNext(style)
[Brief Input]
    ↓ onNext(brief)
[Loading] (3s)
    ↓ auto
[Character Approval]
    ├─→ onRegenerate() → [Loading] → [Character Approval]
    └─→ onApprove() → [Loading] (3s) → [Story Reader]
[Story Reader]
    └─→ onHome() → [Landing]
```

## Animation Layers

### GSAP Animations (Timeline-based)
- Character-by-character text reveals
- Sequential entrance animations
- Floating decorations (infinite loops)
- Loading screen elements
- Character reveal sequence
- Confetti burst and fall

### Framer Motion Animations (Declarative)
- Page transitions
- Button hover states
- Card entrance/exit
- Page turn effects
- Micro-interactions

### CSS Keyframes (Simple loops)
- Wobble-float
- Gentle pulse
- Twinkle
- Breathing effects

## Data Flow

```
StorybookFlow State:
├── currentPage: 'landing' | 'style' | 'brief' | 'loading' | 'approval' | 'reading'
└── storyData:
    ├── style: string
    ├── brief: string
    ├── character: { imageUrl, name } | null
    └── pages: Array<{ imageUrl, text }>
```

## Asset Usage Map

| Asset | Used In | Animation |
|-------|---------|-----------|
| hero1.jpeg | Landing, Story Reader | Scale entrance, page turns |
| hero2.jpeg | Character Approval, Story Reader | Blur materialize, page turns |
| cloud.png | Landing | Drift in, floating loop |
| stars.png | Landing, Brief, Approval, Reader | Twinkle, burst, scatter |
| swirl.png | Landing, Brief, Loading | Draw in, rotation |
| moon.png | Loading | Gentle rocking |
| dots.png | Style Config | Breathing pulse |
| flower.png | Approval, Reader End | Bloom animation |
| confetti.png | Reader End | Burst and fall |
| magic_wand.png | Landing, Brief, Reader End | Button icon |
| paintbrush.png | Style Config | Section header |
| pencil.png | Brief Input | Section header |
| microphone.png | Style Config | Voice recording |
| music-notes.png | Style Config | Decoration |
| checkmark.png | Approval | Approve button |
| refresh_arrows.png | Approval | Regenerate button |
| heart.png | Approval | Approve button accent |
| home.png | All pages | Navigation |
| right_arrow.png | Style, Reader | Navigation |
| open_book.png | Reader End | Read again button |

## Performance Optimizations

1. **GSAP Context Cleanup** - All animations cleaned up on unmount
2. **Next.js Image Optimization** - All images use Next/Image
3. **Lazy Loading** - Components load on demand
4. **Reduced Motion** - Respects user preferences
5. **Animation Throttling** - Floating animations use efficient loops
6. **Conditional Rendering** - Only active page is rendered

## Accessibility Features

- ✅ Reduced motion support via `useReducedMotion` hook
- ✅ Keyboard navigation on all interactive elements
- ✅ Alt text on all images
- ✅ Focus states on buttons
- ✅ Semantic HTML structure
- ✅ ARIA labels where needed
