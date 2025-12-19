# Ask Franklin - Landing Page

Landing page for [askfranklin.io](https://askfranklin.io) - introducing Franklin, your personal private banker.

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui patterns
- **Animations**: Motion (Framer Motion)
- **Typography**: Cormorant Garamond, Playfair Display, Crimson Text, DM Sans

## Design Aesthetic

**Luxury Private Banking** - Old money sophistication meets modern fintech.

- **Colors**: Deep forest green (#0B3D2E), warm ivory (#FAF8F5), gold accents (#C9A962)
- **Typography**: Classical serifs for elegance, sans-serif for UI
- **Texture**: Subtle grain overlays, elegant borders
- **Animations**: Refined fade-ins, floating elements, smooth scrolling

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Structure

```
website/
├── app/
│   ├── globals.css      # Global styles, Tailwind config
│   ├── layout.tsx       # Root layout with metadata
│   └── page.tsx         # Landing page
├── components/
│   └── ui/              # shadcn-style components
├── lib/
│   └── utils.ts         # Utility functions (cn)
├── public/              # Static assets
├── tailwind.config.ts   # Tailwind configuration
└── package.json
```

## Sections

1. **Hero** - Introduce Franklin with elegant quote
2. **Expertise** - Alternative investments, crypto, pre-IPO, fixed income
3. **How It Works** - 3-step process
4. **Channels** - WhatsApp, Voice, Email options
5. **Trust** - Stats and testimonial
6. **CTA** - Final call to action
7. **Footer** - Links and disclaimer

## Deployment

Deploy to Vercel, Netlify, or any static hosting:

```bash
npm run build
# Output in .next/ directory
```

For static export:
```bash
# Add to next.config.js: output: 'export'
npm run build
# Output in out/ directory
```
