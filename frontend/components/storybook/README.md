# Storybook WebUI Implementation

A magical, hand-drawn storybook experience with delightful animations and guided wonder.

## 🎨 Design Philosophy

**Core Principle: Guided Wonder**
- The user is not "configuring an AI tool" — they are embarking on a creative journey
- Every screen feels like turning a page in a book
- Pacing is slow, intentional, and delightful
- Negative space is your most important design element

## 📁 Project Structure

```
frontend/
├── components/storybook/
│   ├── LandingPage.tsx          # Page 0: Wonder & invitation
│   ├── StyleConfigPage.tsx      # Page 1: Playful exploration
│   ├── BriefInputPage.tsx       # Page 2: Focused creativity
│   ├── GenerationLoading.tsx    # Loading: Magic happening
│   ├── CharacterApproval.tsx    # Page 3: The big reveal
│   ├── StoryReader.tsx          # Page 4: Immersive reading
│   ├── StorybookFlow.tsx        # Main orchestrator
│   ├── FloatingDecorations.tsx  # Reusable floating elements
│   ├── ProgressIndicator.tsx    # Progress dots component
│   ├── WobblyButton.tsx         # Styled button component
│   └── index.ts                 # Exports
├── hooks/
│   └── useReducedMotion.ts      # Accessibility hook
├── lib/
│   └── animations.ts            # Animation constants
└── styles/
    └── storybook-animations.css # CSS animations
```

## 🎭 Pages & Flow

### Page 0: Landing
- **Purpose**: First impression, emotional hook
- **Animations**: Sequential entrance (cloud → hero → stars → text → CTA)
- **Duration**: ~3s entrance + infinite floating
- **Assets**: hero1.jpeg, cloud.png, stars.png, swirl.png, magic_wand.png

### Page 1: Style Configuration
- **Purpose**: User selects storytelling style
- **Animations**: Card placement, content fade-up, breathing dots
- **Duration**: ~1.5s entrance
- **Assets**: paintbrush.png, microphone.png, music-notes.png, dots.png

### Page 2: Brief Input
- **Purpose**: User writes story details
- **Animations**: Typing placeholder, twinkling stars when valid
- **Duration**: ~1.2s entrance
- **Assets**: pencil.png, swirl.png, stars.png, magic_wand.png

### Loading Screen
- **Purpose**: Magical waiting experience
- **Animations**: Moon rocking, stars twinkling, swirl rotating, cycling messages
- **Duration**: Infinite loop
- **Assets**: moon.png, stars.png, swirl.png, dots.png

### Page 3: Character Approval
- **Purpose**: Review generated character
- **Animations**: Frame draw, character materialize, stars burst, glow pulse
- **Duration**: ~2s reveal
- **Assets**: checkmark.png, refresh_arrows.png, heart.png, flower.png, stars.png

### Page 4: Story Reader
- **Purpose**: Immersive story reading
- **Animations**: Page turns with 3D rotation, header fade, confetti celebration
- **Duration**: 0.5s per turn
- **Assets**: home.png, right_arrow.png, open_book.png, confetti.png

## 🎨 Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Cream | #F5F1E8 | Background, always |
| Dusty Blue | #6B8FA3 | Primary buttons, trust |
| Mustard Yellow | #D4A03D | Highlights, warmth |
| Sage Green | #7B9E89 | Secondary accents, nature |
| Soft Coral | #C17C74 | Hearts, celebration |
| Brown | #8B7355 | Outlines, text |

## 🎬 Animation Libraries

- **GSAP**: Complex timeline animations, floating effects
- **Framer Motion**: Page transitions, hover states, micro-interactions
- **CSS Keyframes**: Simple loops (wobble-float, twinkle, pulse)

## 🚀 Usage

### Basic Implementation

```tsx
import { StorybookFlow } from '@/components/storybook';

export default function Page() {
  return <StorybookFlow />;
}
```

### Individual Components

```tsx
import { LandingPage, WobblyButton } from '@/components/storybook';

function MyPage() {
  return (
    <div>
      <LandingPage onBegin={() => console.log('Started!')} />
      <WobblyButton variant="primary">Click me</WobblyButton>
    </div>
  );
}
```

## 🎯 Key Features

### 1. Sequential Entrance Animations
Every page has a carefully choreographed entrance sequence using GSAP timelines.

### 2. Floating Decorations
Decorative elements (stars, clouds, swirls) float gently using infinite loops.

### 3. Page Transitions
Smooth page turns with blur and 3D rotation effects using Framer Motion.

### 4. Loading States
Delightful loading screens with cycling messages and animated elements.

### 5. Celebration Moments
Confetti bursts and star explosions at key milestones.

### 6. Accessibility
Respects `prefers-reduced-motion` setting via useReducedMotion hook.

## 📦 Assets Used

All assets are located in `/public/icons/`:

- **Characters**: hero1.jpeg, hero2.jpeg
- **Icons**: magic_wand.png, paintbrush.png, pencil.png, microphone.png, checkmark.png, refresh_arrows.png, heart.png, home.png, right_arrow.png, open_book.png
- **Decorations**: stars.png, cloud.png, moon.png, swirl.png, flower.png, dots.png, music-notes.png, confetti.png

## 🎨 Customization

### Changing Colors

Edit the color values in components or create a theme file:

```tsx
const theme = {
  cream: '#F5F1E8',
  dustyBlue: '#6B8FA3',
  mustard: '#D4A03D',
  sage: '#7B9E89',
  coral: '#C17C74',
  brown: '#8B7355'
};
```

### Adjusting Animation Speed

Modify durations in `lib/animations.ts`:

```tsx
export const storybookEase = "power2.out";
export const animationDuration = 0.5; // Adjust this
```

### Adding New Pages

1. Create component in `components/storybook/`
2. Add to `StorybookFlow.tsx` state machine
3. Export from `index.ts`

## 🐛 Troubleshooting

### Images not loading
- Ensure all assets are in `/public/icons/`
- Check Next.js image optimization settings

### Animations not working
- Verify GSAP is installed: `npm install gsap`
- Check browser console for errors
- Ensure `storybook-animations.css` is imported

### Performance issues
- Reduce number of floating elements
- Disable animations on mobile
- Use `useReducedMotion` hook

## 📝 Notes

- All animations respect the "Guided Wonder" philosophy
- Durations are intentionally slow (0.4s-0.8s) for a magical feel
- Negative space is crucial - resist the urge to fill empty areas
- Every element should feel hand-drawn and cohesive

## 🎓 Best Practices

1. **Never rush animations** - slow and intentional is the goal
2. **Use staggered timelines** - never animate everything at once
3. **Add breathing room** - generous padding and margins
4. **Test on mobile** - ensure touch interactions work well
5. **Respect accessibility** - always implement reduced motion support

## 🔗 Related Documentation

- [Design Guide](../../docs/frontend/how_to_use_asset.md)
- [Animation Design](../../docs/frontend/animations_design.md)

---

Built with ❤️ using Next.js, GSAP, and Framer Motion
