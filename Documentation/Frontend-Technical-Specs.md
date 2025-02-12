# React Frontend Technical Specifications

## Business Goal

Prototype modern web interface for language learning portal that provides:
- A dashboard to track learning progress
- Access to vocabulary lists and study groups
- Integration with various learning activities
- Study session management and progress tracking

## Technical Requirements

- Frontend Framework: React 18 with TypeScript
- Build Tool: Vite
- UI Framework: Tailwind CSS + shadcn/ui
- Routing: React Router DOM
- Development Environment: Node.js 18+

## Directory Structure

```text
frontend-react/
├── src/
│   ├── components/      # Reusable React components
│   │   ├── ui/         # shadcn/ui components
│   │   └── layout/     # Layout components
│   ├── hooks/          # Custom React hooks
│   ├── lib/            # Utility functions and constants
│   ├── pages/          # Page components
│   ├── App.tsx         # Root component
│   ├── index.css       # Global styles
│   └── main.tsx        # Entry point
├── public/             # Static assets
│   ├── assets/
│   │   └── study_activities/
│   │       └── typing-tutor.png
│   ├── apple-touch-icon.png
│   ├── favicon.ico
│   ├── favicon-96x96.png
│   ├── index.html          # HTML entry point
│   ├── components.json     # shadcn/ui configuration
│   ├── tailwind.config.js  # Tailwind CSS configuration
│   ├── postcss.config.js   # PostCSS configuration
│   ├── tsconfig.json       # TypeScript configuration
│   └── package.json        # Dependencies and scripts
└── vite.config.ts      # Vite configuration
```

## Key Dependencies

- **React**: ^18.3.1
- **React Router DOM**: ^6.26.2
- **Radix UI**: Various components for accessible UI
- **Tailwind CSS**: ^3.4.13
- **TypeScript**: ^5.5.3
- **Vite**: ^5.4.1

## Component Architecture

### Layout Components
- Navigation menu
- Page layouts
- Common UI elements

### Feature Components
- Dashboard widgets
- Word lists
- Study session interfaces
- Progress tracking displays

### UI Components (shadcn/ui)
- Buttons
- Dialogs
- Dropdowns
- Navigation menus
- Labels
- Tooltips

## Routing Structure

- `/` - Dashboard
- `/words` - Word list and management
- `/groups` - Study groups
- `/study-sessions` - Study session history and management
- `/study/:activityId` - Study activity interface

## Development Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint
```

## Code Style and Conventions

- TypeScript for type safety
- ESLint for code quality
- Tailwind CSS for styling
- Component-first architecture
- Hooks for state management and side effects

## Asset Management

Static assets are organized in the `public` directory:
- Study activity images in `assets/study_activities/`
- Favicon and touch icons in root
- Other static assets as needed