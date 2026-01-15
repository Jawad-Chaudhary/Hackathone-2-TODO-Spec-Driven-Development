# AI Todo Chatbot Frontend

A modern Next.js 15 chat interface for the AI Todo Chatbot, featuring a clean UI with real-time messaging, tool call visualization, and responsive design.

## Features

- **Modern Chat Interface**: Clean, responsive design with user/assistant message differentiation
- **Real-time Messaging**: Instant message sending and receiving with loading states
- **Tool Call Badges**: Visual indicators when AI uses tools (add task, list tasks, etc.)
- **Auto-scroll**: Automatically scrolls to the latest message
- **Error Handling**: Graceful error messages with user-friendly alerts
- **Accessibility**: ARIA labels, keyboard navigation, and semantic HTML
- **Type Safety**: Full TypeScript coverage with strict type checking

## Tech Stack

- **Framework**: Next.js 15.1.4 (App Router)
- **Language**: TypeScript 5
- **UI**: React 19 with Tailwind CSS 3.4
- **Styling**: Tailwind CSS with custom design system
- **API Client**: Fetch-based with type-safe methods

## Project Structure

```
frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx          # Main chat page (Client Component)
│   ├── layout.tsx             # Root layout
│   ├── page.tsx               # Homepage with welcome screen
│   └── globals.css            # Global styles with Tailwind
├── components/
│   ├── ChatInput.tsx          # Message input component
│   ├── ChatList.tsx           # Scrollable message list
│   ├── ChatMessage.tsx        # Individual message component
│   └── ToolCallBadge.tsx      # Tool usage indicator
├── lib/
│   ├── api.ts                 # API client for backend communication
│   └── types.ts               # TypeScript type definitions
├── .env.local                 # Environment variables
├── package.json               # Dependencies
├── tailwind.config.ts         # Tailwind configuration
└── tsconfig.json              # TypeScript configuration
```

## Prerequisites

- Node.js 20+ and npm/yarn/pnpm
- Backend API running at `http://localhost:8000`
- Backend must be running before starting the frontend

## Installation

1. **Install dependencies:**

```bash
cd frontend
npm install
```

2. **Configure environment variables:**

The `.env.local` file is already configured with default values:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-chatkit-domain-key-here
BETTER_AUTH_SECRET=bee7a5b3961871ab10f8586395f2bd4f1b64ce320b165f611da9c19b8ddc376d
BETTER_AUTH_URL=http://localhost:8000/api/auth
```

For production, update these values accordingly.

3. **Start the development server:**

```bash
npm run dev
```

The app will be available at: [http://localhost:3000](http://localhost:3000)

## Usage

### Homepage

- Navigate to `http://localhost:3000`
- Click "Start Chatting" to begin

### Chat Interface

1. Type a message in the input field (max 2000 characters)
2. Press Enter to send (Shift+Enter for new line)
3. View AI responses with tool call indicators
4. Click "New Chat" to start a fresh conversation

### Example Messages

Try these messages to test the chatbot:

- "Add a task to buy groceries"
- "List all my tasks"
- "Mark the first task as complete"
- "Update task 1 to 'Buy organic groceries'"
- "Delete task 2"

## Component Architecture

### Server vs Client Components

- **Server Components**: `layout.tsx`, `ChatMessage.tsx`, `ToolCallBadge.tsx`
- **Client Components**: `page.tsx` (chat), `ChatInput.tsx`, `ChatList.tsx`

Client Components are only used where interactivity is required (state, effects, event handlers).

### Key Components

#### `ChatInput` (Client Component)
- Handles user input with validation
- Auto-expanding textarea
- Character count indicator
- Keyboard shortcuts (Enter to send)

#### `ChatList` (Client Component)
- Displays message history
- Auto-scrolls to latest message
- Empty state with instructions
- Loading animation with bouncing dots

#### `ChatMessage` (Server Component)
- Renders individual messages
- Different styling for user/assistant
- Displays tool calls with badges
- Timestamps for each message

#### `ToolCallBadge` (Server Component)
- Visual indicator for AI tool usage
- Maps tool names to user-friendly labels
- Icon and color coding

## API Client

The `ApiClient` class provides type-safe methods for backend communication:

```typescript
import { apiClient } from '@/lib/api';

// Send a message
const response = await apiClient.sendMessage(
  'demo-user',
  'Add a task to buy milk',
  conversationId
);

// Get conversations
const conversations = await apiClient.getConversations('demo-user');

// Get conversation history
const history = await apiClient.getConversationHistory('demo-user', 1);
```

## TypeScript Types

All API contracts are defined in `lib/types.ts`:

- `ChatRequest` - Request payload for sending messages
- `ChatResponse` - Response from backend
- `Message` - UI message representation
- `ToolCall` - AI tool invocation
- `Conversation` - Conversation metadata
- `ApiError` - Error responses

## Styling

The app uses Tailwind CSS with a custom design system:

- **Primary Color**: Blue (customizable in `tailwind.config.ts`)
- **Spacing**: Consistent spacing scale
- **Animations**: Smooth transitions and loading states
- **Responsive**: Mobile-first design approach

## Build for Production

```bash
# Create optimized production build
npm run build

# Start production server
npm start
```

The build will be output to `.next/` directory.

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Add environment variables:
   - `NEXT_PUBLIC_API_URL` - Production backend URL
   - `BETTER_AUTH_SECRET` - Auth secret (same as backend)
4. Deploy

### Other Platforms

For other platforms (Netlify, AWS, etc.), ensure:
- Node.js 20+ runtime
- Build command: `npm run build`
- Output directory: `.next`
- Environment variables configured

## Authentication

Currently using mock authentication with hardcoded user ID (`demo-user`) and a fake JWT token. In production:

1. Integrate with Better Auth
2. Add proper authentication flow
3. Store JWT tokens securely
4. Implement protected routes with middleware

## Error Handling

The app handles errors gracefully:

- **Network Errors**: Shows error banner with retry option
- **API Errors**: Displays error message in chat
- **Validation Errors**: Inline validation for message length
- **Loading States**: Loading indicators during API calls

## Accessibility

- **ARIA Labels**: All interactive elements labeled
- **Keyboard Navigation**: Full keyboard support
- **Semantic HTML**: Proper heading hierarchy
- **Focus Management**: Visible focus indicators
- **Screen Reader**: Announces new messages

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Development Notes

### Server/Client Component Guidelines

- Use Server Components by default
- Only use Client Components when needed:
  - State management (`useState`, `useReducer`)
  - Effects (`useEffect`)
  - Event handlers
  - Browser APIs

### Code Standards

- TypeScript strict mode enabled
- ESLint for code quality
- Full type coverage (no `any` types)
- Component-level error boundaries
- Async/await for all API calls

## Troubleshooting

### Port 3000 already in use

```bash
# Kill process on port 3000
npx kill-port 3000

# Or use a different port
PORT=3001 npm run dev
```

### Backend connection errors

1. Ensure backend is running at `http://localhost:8000`
2. Check CORS settings in backend
3. Verify `NEXT_PUBLIC_API_URL` in `.env.local`

### Tailwind styles not applying

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT License - see LICENSE file for details
