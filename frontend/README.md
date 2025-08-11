# Warehouse Copilot Frontend

React-based frontend application for the Warehouse Copilot platform.

## Features

- **Conversational Interface**: Chat with your data using natural language
- **Interactive Schema Explorer**: Visual graph of table relationships
- **SQL Editor**: Full-featured SQL editor with syntax highlighting
- **Results Visualization**: Tables, charts, and export capabilities
- **Query History**: Track and manage previous queries
- **Responsive Design**: Works on desktop and mobile devices

## Architecture

```
src/
├── components/       # Reusable UI components
│   ├── ui/          # Base UI components (buttons, inputs, etc.)
│   ├── schema/      # Schema explorer components
│   └── layout/      # Layout components
├── pages/           # Page components
├── services/        # API client and utilities
├── hooks/           # Custom React hooks
├── types/           # TypeScript type definitions
└── utils/           # Utility functions
```

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling framework
- **shadcn/ui** - UI component library
- **React Query** - Data fetching and caching
- **React Router** - Client-side routing
- **Recharts** - Data visualization
- **Cytoscape.js** - Graph visualization

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## Environment Variables

Create `.env.local` file:

```bash
REACT_APP_API_URL=http://localhost:8000
```

## Pages

### Dashboard (`/`)
- System health overview
- Recent query activity
- Quick action buttons
- Usage statistics

### Chat (`/chat`)
- Conversational interface
- Real-time responses via WebSocket
- Query suggestions and examples
- Message history

### Schema Explorer (`/schema`)
- Interactive table list
- Relationship graph visualization
- Table and column details
- Search and filtering

### SQL Editor (`/sql`)
- Syntax-highlighted editor
- Query validation and execution
- Results display and export
- Query history

### Query History (`/history`)
- Searchable query log
- Filter by success/failure
- Re-run previous queries
- Export capabilities

## Components

### UI Components
Based on shadcn/ui with custom styling:
- Button, Input, Card
- Dialog, Dropdown, Tabs
- Table, Tooltip, Toast

### Schema Graph
Interactive visualization using Cytoscape.js:
- Node-link diagram of tables and relationships
- Zoom, pan, and selection
- Search and filtering
- Responsive layout

### Chat Interface
Real-time messaging with:
- WebSocket connection
- Message formatting (Markdown support)
- Typing indicators
- Auto-scroll

## Styling

Using Tailwind CSS with custom design system:

```css
/* Custom CSS variables in index.css */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  /* ... */
}
```

## API Integration

Centralized API client in `services/api.ts`:

```typescript
import { apiClient } from '../services/api';

// Execute query
const result = await apiClient.executeQuery({
  query: "SELECT * FROM users LIMIT 10",
  query_type: "sql"
});

// Get schema
const schema = await apiClient.getSchema();
```

## State Management

Using React Query for server state and React hooks for local state:

```typescript
// Fetch and cache data
const { data, isLoading } = useQuery({
  queryKey: ['schema'],
  queryFn: () => apiClient.getSchema()
});
```

## Development

### Code Style
- TypeScript for type safety
- ESLint for code quality
- Prettier for formatting
- Husky for git hooks

### Testing
```bash
# Unit tests
npm test

# Coverage
npm run test:coverage

# E2E tests (if configured)
npm run test:e2e
```

### Build Optimization
- Tree shaking for smaller bundles
- Code splitting by route
- Asset optimization
- Progressive Web App features

## Deployment

### Development
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production
```bash
docker-compose up -d
```

The app will be available at `http://localhost:3000`

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Lazy loading for routes and components
- Virtual scrolling for large datasets
- Debounced search inputs
- Optimized re-renders with React.memo
- Service worker for caching (PWA)