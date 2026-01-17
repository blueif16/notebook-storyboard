Storybook WebUI Design Guide
Design Philosophy
Core Principle: Guided Wonder
The user is not "configuring an AI tool" — they are embarking on a creative journey. Every screen should feel like turning a page in a book, not clicking through a software wizard. The UI should feel like it was drawn by the same hand that will illustrate their story.
Pacing: Slow, intentional, delightful. Resist the urge to cram. Each page does one thing and does it with care.
Negative Space: Your most important design element. Let things breathe. The cream background is not "empty" — it's the paper of your storybook.

The Emotional Arc
StageFeelingVisual DensityLandingWonder, invitationRich but balancedConfig 1 (Style)Playful explorationMediumConfig 2 (Brief)Focused creativityMinimalConfig 3 (Approval)Anticipation, delightCharacter-forwardReadingImmersion, warmthContent-focused, chrome fades

Page-by-Page Flow

Page 0: Landing
Purpose: First impression. Emotional hook. "This is going to be special."
Layout Concept:
The page is almost entirely the hero illustration, floating in generous cream space. No navigation bar competing for attention. The illustration lives in the upper two-thirds, breathing. Below it, a single hand-lettered headline and one pill-shaped CTA button.
Asset Placement:
AssetPositionNotesHero 1 (character on books)Center-upper, ~60% of viewport heightThe star of the showStars clusterUpper right, floating near the book's magicSubtle, small scaleCloudUpper left corner, partially croppedCreates asymmetry, dreamySwirlNear the CTA button, suggesting movementDraws eye downward
Typography:
Hand-lettered headline in the wobbly mixed-case style. Something like:
"Let's make a story together"
Small subtext below in a clean sans-serif (contrast creates hierarchy).
CTA Button:
Pill-shaped, dusty blue fill, wobbly outline. Uses the Magic Wand icon inside.
Text: "Begin" or "Start the magic"
Interaction Concept:
When the page loads, elements fade in sequentially — first the character, then the floating shapes drift upward gently, then the text, then the button. Not fast. Like a book opening.
What's NOT here:

No header navigation
No feature lists
No pricing
No screenshots

Just wonder.

Page 1: Record Style
Purpose: User selects or records their preferred storytelling style. This might involve voice input or selecting from presets.
Layout Concept:
A centered card or container, soft rounded corners (hand-drawn wobbly border), floating on the cream canvas. The card is not full-width — it feels like a page torn from a notebook, intimate.
Visual Metaphor: Choosing your crayons before drawing
Asset Placement:
AssetPositionNotesMicrophone iconProminent, center of card if voice is primary inputLarge enough to feel tappable/clickablePaintbrush iconSection header or tab for "style selection"Indicates creative choiceMusical notesNear the recording interfaceSuggests rhythm, voice, playfulnessDots clusterBackground, lower-right of cardSubtle texture, not distracting
Progress Indicator:
Top of page, three simple circles (or building blocks). First one filled with mustard yellow, others outlined only. The wobbly line style. No numbers, no "Step 1 of 3" text — visual only.
Navigation:
LeftRightHome icon (small, muted)Right arrow icon in pill button
The "next" button is disabled/greyed until input is complete. When active, it has the dusty blue fill.
Micro-detail:
If using voice recording, the microphone icon could have small animated sound waves (the decorative dots, pulsing gently). Not flashy — subtle, like breathing.
Mood: Playful, exploratory. User is making creative choices, not filling out a form.

Page 2: Write Brief Content
Purpose: User inputs story details — characters, setting, theme, or narrative beats.
Layout Concept:
Even more minimal than Page 1. The focus is entirely on a text input area. The card/container is slightly larger to accommodate writing, but still not full-width. It feels like a journal page.
Visual Metaphor: Writing in your diary
Asset Placement:
AssetPositionNotesPencil iconTop-left of the text area, or as a subtle header iconSignals "this is where you write"SwirlBottom corner of the card, very smallAdds life without distractionStars clusterNear the submit/next buttonHint of magic to come
The Text Area:
Large, comfortable. Placeholder text in a lighter gray, hand-lettered style:
"Once upon a time..."
or
"Tell me about your story..."
No rigid form fields. One open space for creativity. If you need structured input (character name, setting, etc.), use gentle inline prompts that feel conversational, not like form labels.
Progress Indicator:
Second circle now filled (sage green). Visual continuity.
Navigation:
Same pattern. Back arrow (left), Next arrow (right). The next button might say "Create" or show the Magic Wand icon since this triggers generation.
Mood: Focused, calm, intimate. The cream space and minimal decoration let the user's words take center stage.
What's NOT here:

No decorative clutter
No example stories competing for attention
Minimal instruction text — trust the user


Page 3: Character Approval
Purpose: User reviews AI-generated character designs and approves or requests regeneration.
Layout Concept:
This is the big reveal. The generated character(s) should feel like they're being presented on a stage or in a frame. The UI chrome pulls back to let the artwork shine.
Visual Metaphor: The curtain rises
Asset Placement:
AssetPositionNotesHero 2 style frame conceptThe character sits within a hand-drawn "picture frame" or on a torn paper edgeCreates presentation momentHeart iconNear the approve actionEmotional, not clinicalCheckmark iconPrimary approve buttonClear actionRefresh iconSecondary "try again" buttonEncouraging, not punishingStars clusterScattered near the character, celebratingThey made it!FlowerSmall, near approve buttonPositive reinforcement
Layout Structure:
Character artwork is hero-sized, centered. Below it, two buttons side by side:
Left ButtonRight ButtonRefresh icon + "Try again"Checkmark icon + "Perfect!"
The "Perfect!" button is primary (filled), "Try again" is secondary (outlined only).
If Multiple Characters:
Horizontal scroll or gentle carousel. Each character in its own "frame." Dots below indicate pagination (using your decorative dots cluster style).
Interaction Concept:
When the character appears, it fades in with a subtle "pop" — maybe the stars animate outward like it just materialized. Magical arrival.
Progress Indicator:
Third circle filled (soft coral). Almost there.
Mood: Anticipation, delight, pride. The user is meeting someone they helped create.

Page 4: Story Reading Interface
Purpose: The destination. User reads their generated storybook.
Layout Concept:
The UI nearly disappears. This is full immersion. The story content (text + illustrations) fills the viewport. Navigation is minimal and tucked away. The frame is invisible until needed.
Visual Metaphor: You're inside the book now
Structure:
┌─────────────────────────────────────────┐
│  [Home]                        [1/12]   │  ← Minimal header, fades on scroll
│                                         │
│                                         │
│         ┌───────────────────┐           │
│         │                   │           │
│         │   [Story Image]   │           │
│         │                   │           │
│         └───────────────────┘           │
│                                         │
│     "Nessa looked at the house she      │
│      had built and smiled..."           │
│                                         │
│                                         │
│         ←  ○ ○ ● ○ ○  →                 │  ← Page dots + arrows
│                                         │
└─────────────────────────────────────────┘
Asset Placement:
AssetPositionNotesOpen book iconHeader, or as a subtle watermarkReminds user where they areHome iconTop-left, small and mutedEscape hatch, not prominentRight arrow / Left arrowBottom or sides, for page turnLarge enough for easy tapCloud, Moon, StarsSparse, in margins onlyDepends on story moodSwirlPage turn transition hintNear edges
Page Turn Navigation:
Two options, both valid:

Tap/click zones: Left third goes back, right third goes forward, center does nothing
Explicit arrows: Wobbly arrow icons on left and right edges

Consider supporting swipe gestures on mobile.
Story Frame:
The generated story illustration should have a subtle hand-drawn border — the same wobbly line quality. This ensures even if the AI-generated art varies slightly in style, the frame unifies it with your UI aesthetic.
Typography:
Story text in a readable serif or friendly sans-serif. NOT the wobbly hand-lettered style — that's for UI elements only. The story text should be comfortable for extended reading.
The Final Page:
When the story ends, a special layout:
AssetPositionConfetti burstCenter, celebratoryStars clusterScattered aroundFlowerAccent
Hand-lettered text: "The End"
Below it, soft CTAs:

"Read again" (Open book icon)
"Make another story" (Magic wand icon)
"Go home" (Home icon)

Mood: Warmth, immersion, accomplishment. The user disappears into the story.

Transitions & Micro-Moments
Page-to-Page Transitions
Not hard cuts. Each transition should feel like a page turn:

Fade + slight slide: Content fades while gently sliding left (like turning a page)
Duration: 300-400ms. Not rushed.
Easing: Soft ease-out. Nothing mechanical.

Loading / Generation State
When AI is generating (after Page 2, before Page 3):
Layout: Full screen, minimal. Centered content only.
Asset Placement:
AssetAnimation ConceptMoonGently rocking, like it's thinkingStars clusterTwinkling in sequenceSwirlSlowly rotatingDots clusterPulsing gently
Text: Hand-lettered, cycling through phrases:

"Dreaming up your story..."
"Drawing your characters..."
"Almost there..."

Duration Perception:
If generation takes 10+ seconds, this loading state must be delightful, not frustrating. The animation and cycling text make the wait feel intentional, like something magical is happening behind the curtain.
Success Moment
When characters are ready (arriving at Page 3):
Brief celebratory flash:

Confetti burst animates outward
Stars twinkle
Then settles into the approval screen

Keep it under 1 second. Delightful, not obnoxious.

Responsive Considerations
Mobile:

Hero illustrations scale down but maintain prominence
Cards become full-width with padding
Navigation arrows become bottom-fixed bar
Decorative elements reduce in quantity (keep stars, lose some clouds)

Tablet:

Sweet spot for this design — book-like proportions
Consider landscape orientation for reading interface (two-page spread feeling)

Desktop:

Constrain max-width (~900px for content)
Let cream background extend to edges
Decorative elements can be more generous in margins


Color Usage Summary
ColorPrimary UseCreamBackground, alwaysDusty BluePrimary buttons, main character, trustMustard YellowHighlights, first progress dot, warmthSage GreenSecondary accents, growth, natureSoft CoralHearts, celebration, emotionBlackOutlines only, never fills
Never use pure white. Never use pure black fills. Stay in the muted, warm family.

Final Principle
Every element should feel like it was drawn by the same friendly hand.
The icons, the decorations, the buttons, the frames — they all share DNA. When a user moves through your flow, they should never feel like they've left the storybook world. The UI is not a container for the experience; the UI is the experience.
