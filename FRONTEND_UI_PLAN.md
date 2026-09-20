# Agents Network Frontend UI Plan

## Summary

Build a responsive React + Vite single-page application in `agents_network/frontend/` that consumes the existing FastAPI API. The application will provide registration, login, and a ChatGPT-inspired chat interface for the Engineer, Doctor, and Lawyer agents.

This first version supports one active conversation in the browser. It does not include a saved-conversation sidebar because the current API cannot list or reopen conversations.

## Scope

### Included

- Registration and login using the existing authentication API.
- In-memory JWT session handling.
- Chat interface for Engineer, Doctor, and Lawyer agents.
- New-chat and logout actions.
- Markdown assistant responses, including tables and code blocks.
- Responsive desktop and mobile layout.
- FastAPI CORS configuration for the separate frontend origin.

### Excluded

- Conversation-history listing, reopening, renaming, or deletion.
- User profile editing and password reset.
- Token refresh or persistent "remember me" login.
- Database migrations or changes to the existing auth/chat contract.

## Existing API Contract

The frontend will use `VITE_API_BASE_URL`, with the development default set to `http://127.0.0.1:8000/api`.

| Endpoint | Request | Result |
| --- | --- | --- |
| `POST /auth/register` | `{ email, password }` | `201` with user data; `409` when email is already registered |
| `POST /auth/login` | `{ email, password }` | JWT access token |
| `POST /auth/logout` | Bearer token | Revokes the active token |
| `POST /chat` | Bearer token plus `{ message, conversation_id, chatbot_type }` | Assistant response and conversation ID |

Supported `chatbot_type` values are `engineer`, `doctor`, and `lawyer`. A conversation cannot change type after creation, so changing agents must begin a new local chat.

## Frontend Implementation

### Project and dependencies

- Create a Vite React app under `agents_network/frontend/`.
- Use TypeScript.
- Add `react-markdown` and `remark-gfm` for assistant messages.
- Use CSS or CSS modules for styling; do not introduce a component-library dependency.
- Add `.env.example` containing:

  ```env
  VITE_API_BASE_URL=http://127.0.0.1:8000/api
  ```

- Include `dev`, `build`, `preview`, and `test` package scripts.

### Typed API client

Create a single API client module with these public types:

```ts
type ChatbotType = "engineer" | "doctor" | "lawyer";

interface TokenResponse {
  access_token: string;
  token_type: string;
}

interface UserResponse {
  id: number;
  email: string;
  created_at: string;
}

interface ChatResponse {
  error: boolean;
  conversation_id: number;
  chatbot_type: ChatbotType;
  response: string;
}

interface ApiError {
  status: number;
  message: string;
}
```

The client exposes `register`, `login`, `logout`, and `sendChatMessage`. It attaches the bearer token to protected requests and normalizes API error objects, FastAPI validation errors, invalid JSON, and network failures into `ApiError`.

### Authentication screen

- Display an unauthenticated landing page with the product name “Agents Network”.
- Provide Login and Register tabs.
- Both forms contain email and password fields and a show/hide-password control.
- Registration validates the current backend password policy before submitting:
  - minimum 8 characters;
  - one uppercase character;
  - one lowercase character;
  - one number;
  - one special character.
- On successful registration, show confirmation, switch to Login, and prefill the email field.
- On successful login, keep the token and email only in React state. Refreshing the page or closing the tab signs the user out.
- Display clear inline errors for invalid credentials, duplicate accounts, validation failures, and unavailable API requests.

### Chat screen

- Use a neutral, ChatGPT-inspired layout.
- Desktop layout:
  - left sidebar: product identity, New chat, agent selector, signed-in email, Logout;
  - main panel: selected-agent heading, message list, and bottom message composer.
- Mobile layout: collapse the sidebar into an accessible menu/drawer.
- Show a friendly empty state with agent-specific prompt suggestions.
- Map display options to API values:
  - Engineer -> `engineer`
  - Doctor -> `doctor`
  - Lawyer -> `lawyer`
- Render user messages as plain text and assistant messages through `react-markdown` with GFM support. Do not enable raw HTML rendering.
- Show medical and legal educational-use notices for the Doctor and Lawyer agents.

### Conversation behavior

- The first message sends `conversation_id: null`.
- Save the returned `conversation_id` and use it for every later message in the active chat.
- New chat clears local messages and resets `conversation_id` to `null`.
- Changing agent with an existing conversation displays a confirmation dialog. Confirming clears messages and starts a new conversation; cancelling preserves the existing agent and chat.
- Trim message input, reject empty values, and enforce the backend’s 10,000-character maximum.
- Optimistically display the user message, then display a loading assistant state while the request is active.
- Disable sending, New chat, and agent changes while a request is in progress to prevent duplicate or conflicting requests.
- If a request fails, retain the user message, show an inline error with Retry, and do not create a fake assistant answer.
- On a `401`, clear client state and return to Login with a “session expired” message.
- Logout should clear local client state even if the API request cannot complete.

## Backend CORS Change

The FastAPI service currently needs CORS middleware for a separately served Vite frontend.

- Add `cors_origins` to `Settings`, sourced from `APP_CORS_ORIGINS` as a comma-separated list.
- Configure `CORSMiddleware` in `src/app/main.py`.
- Development default origins:
  - `http://localhost:5173`
  - `http://127.0.0.1:5173`
- Allow the HTTP methods and headers needed by the frontend, specifically `Authorization` and `Content-Type`.
- Production configuration must set explicit frontend origins through `APP_CORS_ORIGINS`; do not use wildcard origins.

## Tests

### Frontend automated tests

- Registration validation and successful registration flow.
- Duplicate-email and backend-validation error states.
- Successful login and invalid-credentials error state.
- Bearer token inclusion on protected API calls.
- Page remount clears the in-memory session.
- First chat request uses `conversation_id: null`; later requests use the returned conversation ID.
- New chat clears message state.
- Agent switch confirmation behavior.
- Composer loading state prevents duplicate sends.
- Failure and retry behavior.
- `401` chat response returns the user to Login.
- Markdown/GFM renders correctly and raw HTML is not rendered.

### Backend automated tests

- Requests from allowed development origins return the correct CORS headers.
- Disallowed origins do not receive an allowed-origin response header.
- CORS preflight permits the `Authorization` header.

### Manual acceptance

1. Start FastAPI on port 8000 and Vite on port 5173.
2. Register an account using a policy-compliant password.
3. Log in and send multiple messages to each agent.
4. Start a new chat and confirm a new conversation ID is used.
5. Change agent, verify the discard confirmation, and verify a fresh chat starts after confirmation.
6. Log out, then confirm the chat cannot be accessed without logging in again.
7. Verify desktop and mobile layouts and confirm there are no browser CORS errors.

## Assumptions

- The FastAPI route implementations and Pydantic schemas are the source of truth. The checked-in root `openapi.json` is stale because it does not list the existing `/api/chat` endpoint.
- No branding assets are currently available, so the first version uses a neutral ChatGPT-inspired visual design.
- The login email is retained only for the current session so it can appear in the sidebar; a `/me` endpoint is not required.
- Saved chat history is deferred until the backend adds list and message-retrieval endpoints.
