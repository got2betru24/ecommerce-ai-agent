# E-Commerce AI Agent

A full-stack customer service AI agent built with Claude, FastAPI, React, and MySQL. Customers can look up their orders and check product availability through a natural language chat interface.

## Overview

This project demonstrates how to build a production-close AI agent using Anthropic's Claude API with tool use, streaming responses, and persistent conversation history. The agent can look up customer orders by name, retrieve product information by name or ID, and maintain context across a multi-turn conversation.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Browser                          │
│              React + MUI Chat Interface                 │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP (port 80)
┌───────────────────────▼─────────────────────────────────┐
│                    Traefik                              │
│              Reverse Proxy / Router                     │
│   /api/* → backend     /  → frontend                   │
└──────────┬────────────────────────┬─────────────────────┘
           │                        │
┌──────────▼──────────┐  ┌──────────▼──────────┐
│   FastAPI Backend   │  │   Vite/React        │
│   (port 8000)       │  │   Frontend          │
│                     │  │   (port 5173)       │
│  - /api/chat (SSE)  │  └─────────────────────┘
│  - /api/health      │
│  - Agent loop       │
│  - Tool execution   │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│     MySQL 8.0       │
│   (port 3306)       │
│                     │
│  - Customer         │
│  - Orders           │
│  - Product          │
│  - Conversation     │
│    History          │
└─────────────────────┘
```

## Tech Stack

**Backend**
- Python 3.13
- FastAPI with Server-Sent Events (SSE) streaming
- Anthropic Claude API (claude-haiku-4-5) with tool use
- MySQL Connector/Python
- Uvicorn

**Frontend**
- React 18 + Vite
- Material UI (MUI)
- SSE stream reader for real-time responses

**Infrastructure**
- Docker + Docker Compose
- Traefik v3 reverse proxy
- MySQL 8.0

## Project Structure

```
eCommerceAssistant_fullstack/
├── .devcontainer/
│   └── devcontainer.json       # VS Code Dev Container config
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── main.py             # FastAPI app, routes, SSE streaming
│       ├── agent.py            # Claude agent loop, tool orchestration
│       ├── tools.py            # Tool definitions and implementations
│       ├── database.py         # MySQL data access layer
│       └── utils.py            # JSON serializer, input validators
├── frontend/
│   └── src/
│       └── App.jsx             # Chat UI with streaming support
├── sql/
│   ├── 01_schema.sql           # Database schema
│   └── 02_seed.sql             # Seed data
├── Dockerfile                  # Multi-stage: backend-dev, frontend-dev
├── compose.yaml                # All services: traefik, mysql, backend, frontend
├── .env.example                # Environment variable template
└── README.md
```

## How the Agent Works

The agent uses Claude's tool use capability to answer customer questions. Rather than hardcoding specific query paths, Claude decides at runtime which tools to call based on the customer's message.

**Available tools:**
- `get_order(order_id)` — look up a single order by ID
- `get_orders(last_name, first_name?)` — find all orders for a customer by name
- `get_product_by_id(product_id)` — retrieve product details by ID
- `get_product_by_name(product_name)` — fuzzy search products by name

**Agent loop:**
1. User message is saved to conversation history
2. Full history is loaded and sent to Claude with tool definitions
3. If Claude calls a tool, the result is appended to history and Claude is called again
4. When Claude produces a final text response, it is streamed chunk by chunk to the frontend via SSE
5. The complete response is saved to conversation history

**Conversation persistence:** Each session has a UUID that the frontend stores and sends with every message. History is stored in MySQL and expires after 3 days.

## Streaming

Responses stream from Claude to the browser in real time using Server-Sent Events. Each SSE event is a JSON payload:

```
data: {"type": "chunk", "text": "Hello!"}
data: {"type": "done", "session_id": "uuid-here"}
```

The frontend appends chunks to a placeholder message as they arrive, showing a blinking cursor while streaming is in progress.

## Security

- Parameterized SQL queries throughout — no SQL injection possible
- Input validation on all tool parameters (name format, ID format, product search)
- Claude's system prompt enforces privacy — order details are never shared without a matching customer lookup
- API keys and database credentials stored in environment variables, never in code
- Non-root MySQL user with scoped permissions

## Getting Started

### Prerequisites

- Docker Desktop
- Anthropic API key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/got2betru24/ecommerce-ai-agent.git
cd ecommerce-ai-agent
```

2. Create your environment file:
```bash
cp .env.example .env
```

3. Fill in your `.env`:
```
ANTHROPIC_API_KEY=your_key_here
DB_NAME=eCommerce
DB_USER=ecommerce_user
DB_PASSWORD=your_password
DB_ROOT_PASSWORD=your_root_password
```

4. Start the stack:
```bash
docker compose up --build
```

5. Open the app at `http://localhost`

API docs are available at `http://localhost/api/docs`.

### Development

This project uses VS Code Dev Containers. With the Dev Containers extension installed:

1. Start the stack with `docker compose up`
2. Open Command Palette → `Dev Containers: Reopen in Container`
3. Select the backend configuration

The backend supports hot-reload — changes to Python files reflect immediately without restarting.

## Example Conversations

```
User: Do you have any ski jackets in stock?
Agent: Yes! We have several alpine jackets available...

User: What did John Smith order most recently?
Agent: I found one customer with that name. Their most recent order was...

User: Can you check order #1042?
Agent: Order #1042 is currently shipped. It contains...
```

## Key Design Decisions

**Tool use over hardcoded endpoints** — Claude decides which tools to call and how to chain them. When an order contains a product ID, Claude automatically calls `get_product_by_id` to enrich the response with product details, without any explicit orchestration code.

**Streaming over batch responses** — SSE streaming starts showing Claude's response immediately rather than waiting for the full response. This is critical for user experience when Claude is reasoning through multiple tool calls before responding.

**Lazy database connection** — The MySQL connection is established on first use, not at import time. This prevents startup crashes when the database container is still initializing.

**Defense in depth** — Security is applied at multiple layers: input validation in tool functions, parameterized queries in the database layer, and behavioral guardrails in Claude's system prompt.