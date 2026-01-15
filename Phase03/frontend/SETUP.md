# Quick Setup Guide

## Prerequisites

- Backend API must be running at `http://localhost:8000`
- Node.js 20+ installed

## Setup Steps

1. **Install dependencies** (already done):
   ```bash
   npm install
   ```

2. **Environment variables** (already configured in `.env.local`):
   - `NEXT_PUBLIC_API_URL=http://localhost:8000`
   - Mock authentication is configured

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Open in browser**:
   - Navigate to: http://localhost:3000
   - Click "Start Chatting"

## Testing the Chat

Try these example messages:

1. **Add a task**:
   - "Add a task to buy groceries"
   - "Create a task: finish homework"

2. **List tasks**:
   - "Show me my tasks"
   - "List all tasks"

3. **Update a task**:
   - "Update task 1 to 'Buy organic groceries'"
   - "Change the first task"

4. **Complete a task**:
   - "Mark task 1 as complete"
   - "Complete the first task"

5. **Delete a task**:
   - "Delete task 2"
   - "Remove the second task"

## Project Structure

```
frontend/
├── app/
│   ├── chat/page.tsx          # Main chat interface
│   ├── page.tsx               # Homepage
│   ├── layout.tsx             # Root layout
│   └── globals.css            # Tailwind styles
├── components/
│   ├── ChatInput.tsx          # Message input
│   ├── ChatList.tsx           # Message list
│   ├── ChatMessage.tsx        # Individual messages
│   └── ToolCallBadge.tsx      # Tool usage badges
├── lib/
│   ├── api.ts                 # API client
│   └── types.ts               # TypeScript types
└── .env.local                 # Environment config
```

## Features

- Real-time chat interface
- Tool call visualization (shows when AI uses tools)
- Auto-scroll to latest message
- Loading states
- Error handling
- Responsive design (mobile-friendly)
- Accessibility (ARIA labels, keyboard navigation)

## Build for Production

```bash
npm run build
npm start
```

## Common Issues

### Backend not running
- Error: "Failed to fetch" or "Network error"
- Solution: Start the backend at `http://localhost:8000`

### Port 3000 in use
```bash
npx kill-port 3000
# or
PORT=3001 npm run dev
```

### TypeScript errors
```bash
# Clear cache and rebuild
rm -rf .next
npm run build
```

## Next Steps

1. Test the chat interface with various messages
2. Verify tool calls display correctly
3. Check responsive design on mobile
4. Test error handling (stop backend and try sending message)
5. Review accessibility features

## Authentication Note

Currently using **mock authentication**:
- User ID: `demo-user`
- JWT Token: Mock token for development

For production, integrate with Better Auth for real authentication.

## Code Quality

- TypeScript strict mode enabled
- Full type coverage (no `any` types)
- ESLint configured
- Accessible components
- Error boundaries
- Loading states

## Need Help?

See `README.md` for detailed documentation.
