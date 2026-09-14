# ResearchMate AI - Frontend

Modern editorial-style landing page for ResearchMate AI, featuring a paper-based visual metaphor and pastel color palette.

## Design Philosophy

- **Editorial & Academic**: Serif headings, clean sans-serif body text
- **Paper Metaphor**: Physical research papers as the core visual
- **Pastel Palette**: Cream, light blue, lavender, muted rose
- **Warm & Intelligent**: Not corporate, not futuristic - academic and approachable

## Tech Stack

- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Google Fonts** (Playfair Display, Inter)

## Getting Started

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the landing page.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx          # Home page
│   ├── layout.tsx        # Root layout with fonts
│   ├── globals.css       # Global styles
│   └── workspace/        # Placeholder workspace page
├── components/
│   ├── Navbar.tsx
│   ├── Hero.tsx
│   ├── PaperStack.tsx    # Animated paper cards
│   ├── ComparisonPreview.tsx
│   ├── ResearchGapCard.tsx
│   ├── FeatureCards.tsx
│   ├── HowItWorks.tsx
│   ├── ClosingSection.tsx
│   └── Footer.tsx
└── ...config files
```

## Features

### Current (Landing Page)
- ✅ Responsive navigation with mobile menu
- ✅ Editorial hero section with two-column layout
- ✅ Animated paper stack visualization
- ✅ Comparison table preview
- ✅ Research gap card with disclaimer
- ✅ Four feature cards
- ✅ How it works section with step-by-step flow
- ✅ Closing CTA with stacked books illustration
- ✅ Footer with links

### Coming Soon (Application)
- ⏳ PDF upload interface
- ⏳ Q&A workspace
- ⏳ Multi-paper comparison tool
- ⏳ Research gap analysis interface

## Design Tokens

### Colors
```css
cream: #FDF4D2
light-blue: #A9CBE6
lavender: #A594B8
muted-rose: #9C7070
```

### Typography
- **Headings**: Playfair Display (serif)
- **Body**: Inter (sans-serif)

## Accessibility

- Semantic HTML5
- Proper heading hierarchy
- Keyboard navigation support
- Focus states on all interactive elements
- `prefers-reduced-motion` support
- Alt text for decorative elements

## Backend Integration

The frontend is designed to connect to the FastAPI backend at `http://localhost:8000`.

Backend provides:
- `/api/papers/upload` - PDF upload
- `/api/papers/{id}/ask` - Q&A
- `/api/papers/compare` - Multi-paper comparison
- `/api/papers/gaps` - Research gap analysis

## License

Part of ResearchMate AI MVP project.
