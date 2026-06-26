# STOXLY.AI — Technical Specification Document
**Version:** 1.0  
**Status:** Draft  
**Last Updated:** 2026-06-26  
**Author:** Architecture Team  

---

## 1. SYSTEM ARCHITECTURE

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                        │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐  │
│  │  React SPA  │  │   Swagger   │  │  Mobile (Future)  │  │
│  │ localhost:3000│  │ localhost:8001│  │                   │  │
│  └──────┬──────┘  └──────┬──────┘  └────────┬──────────┘  │
└─────────┼────────────────┼──────────────────┼──────────────┘
          │                │                  │
          ├────────────────┼──────────────────┤
          ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      REVERSE PROXY                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Nginx (SSL Termination)                 │  │
│  │         /api/* → backend:8000                        │  │
│  │         /* → frontend:80 (static)                    │  │
│  │         /ws/* → backend:8000 (WebSocket)             │  │
│  └──────────────────────┬───────────────────────────────┘  │
└─────────────────────────┼──────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌──────────┐ ┌────────────────┐
│  FastAPI App    │ │  Redis   │ │  PostgreSQL    │
│  port 8000      │ │  port 6379│ │  port 5432     │
│  Uvicorn/Gunicorn│ └──────────┘ └────────────────┘
│  Workers: 4     │
└─────────────────┘
```

### 1.2 Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Monolith vs Microservices** | Monolith (modular) | Current scale (<100 users) doesn't justify microservices complexity. Modular monolith with clear service boundaries allows easy extraction later. |
| **Monolith Pattern** | Repository + Service + Route | Clear separation of concerns. Routes handle HTTP, Services handle business logic, Repositories handle data access. |
| **API Style** | RESTful | Simpler than GraphQL for this use case. WebSocket for real-time only. |
| **Auth Strategy** | JWT Bearer | Stateless, no server-side session storage needed. Refresh token rotation for security. |
| **Async vs Sync** | Hybrid (async routes, sync DB) | FastAPI async for I/O-bound operations, SQLAlchemy sync for DB (the sync driver is faster than async for SQLite). Switch to asyncpg with PostgreSQL. |
| **Caching** | Redis + In-memory | Redis for rate limiting (shared across workers). In-memory for paper trading/alerts (SIMPLICITY — will move to DB). |

### 1.3 Request Lifecycle

```
Request → Nginx → CORS Middleware → Security Headers Middleware → 
Rate Limit Middleware → Request Body Limit → Request ID Middleware → 
FastAPI Router → Auth Dependency → Route Handler → 
Service Layer → Repository Layer → Database
                                    ↓
Response ← Exception Handler ← Response Model
```

---

## 2. FOLDER STRUCTURE

```
stock-trading-platform/
├── backend/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py                    # Authentication routes
│   │       ├── stocks.py                  # Stock data routes
│   │       ├── portfolio.py               # Portfolio CRUD routes
│   │       ├── portfolio_optimizer_routes.py  # Portfolio optimization routes
│   │       ├── watchlist.py               # Watchlist routes
│   │       ├── screener.py                # Stock screener routes
│   │       ├── indian_stocks.py           # Indian stock routes
│   │       ├── chat.py                    # V1 chat routes
│   │       ├── chat_v2.py                 # V2 enhanced chat routes
│   │       ├── profile.py                 # Profile endpoints (included routes)
│   │       ├── recommendations.py         # AI recommendations routes
│   │       ├── technical_indicators.py    # Technical analysis routes
│   │       ├── stock_analysis.py          # AI analysis routes
│   │       ├── sector_performance.py      # Sector routes
│   │       ├── comparator.py              # Stock comparator routes
│   │       ├── price_alerts.py            # Price alert routes
│   │       ├── ipo_calendar.py            # IPO calendar routes
│   │       ├── paper_trading.py           # Paper trading routes
│   │       ├── dashboard.py               # Dashboard widget routes
│   │       ├── export_routes.py           # Export Routes
│   │       ├── search_route.py            # Smart search routes
│   │       └── i18n.py                    # Internationalization routes
│   ├── core/
│   │   ├── config.py                      # Environment config
│   │   ├── database.py                    # SQLAlchemy engine/session
│   │   ├── security.py                    # JWT, password hashing
│   │   ├── security_extras.py             # Brute force, password policy, sanitization
│   │   └── redis_client.py               # Redis connection manager
│   ├── middleware/
│   │   ├── error_handler.py               # Global exception handler
│   │   ├── rate_limiter.py                # Rate limiting middleware
│   │   └── security_headers.py            # Security headers middleware
│   ├── models.py                          # SQLAlchemy ORM models (20+ tables)
│   ├── schemas.py                         # Pydantic request/response models
│   ├── profile_schemas.py                 # Profile-specific schemas
│   ├── database.py                        # Legacy DB config (duplicate of core/database.py)
│   ├── auth.py                            # Legacy auth (re-exports from core/security)
│   ├── profile_endpoints.py               # Legacy profile routes
│   ├── comprehensive_indian_stocks.py     # Mock stock data provider (210 stocks)
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── portfolio_repository.py
│   │   ├── watchlist_repository.py
│   │   ├── profile_repository.py
│   │   ├── chat_repository.py
│   │   └── screener_repository.py
│   ├── services/
│   │   ├── ai_service.py                  # V1 AI chat service
│   │   ├── ai_analysis.py                 # Stock analysis & market brief
│   │   ├── technical_indicators.py        # RSI, MACD, Bollinger, etc.
│   │   ├── portfolio_optimizer.py         # MPT, Black-Litterman, VaR
│   │   ├── totp_service.py               # 2FA TOTP generation
│   │   ├── captcha_service.py             # reCAPTCHA verification
│   │   ├── email_service.py              # Email sending
│   │   ├── export_service.py             # CSV generation
│   │   ├── search_service.py             # Fuzzy search
│   │   └── report_service.py             # PDF/HTML report generation
│   ├── tests/
│   │   ├── test_auth.py                   # 2 auth tests
│   │   ├── test_health.py                 # 3 health tests
│   │   ├── test_stocks.py                 # 4 stock tests
│   │   ├── test_portfolio.py              # 4 portfolio tests
│   │   └── conftest.py                    # (missing)
│   ├── alembic/                           # (missing migrations)
│   ├── scripts/
│   │   └── gen-dev-cert.ps1              # SSL cert generator
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.development
│   ├── .env.production
│   └── main.py                           # Application entry point
│
├── frontend/
│   ├── src/
│   │   ├── pages/                         # Page components
│   │   │   ├── Home.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Profile.tsx
│   │   │   ├── StockSearch.tsx
│   │   │   ├── StockDetails.tsx
│   │   │   ├── Portfolio.tsx
│   │   │   ├── ManagePortfolio.tsx
│   │   │   ├── PortfolioHoldings.tsx
│   │   │   ├── Watchlist.tsx
│   │   │   ├── PortfolioOptimizer.tsx
│   │   │   ├── ChatBot.tsx
│   │   │   ├── IndianStockExplorer.tsx
│   │   │   ├── InvestmentProfileOnboarding.tsx
│   │   │   ├── Screener.tsx
│   │   │   └── Auth/ (Login.tsx, Register.tsx)
│   │   ├── features/                      # Feature-based modules
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── home/
│   │   │   ├── stocks/
│   │   │   ├── portfolio/
│   │   │   ├── watchlist/
│   │   │   ├── screener/
│   │   │   ├── profile/
│   │   │   └── chat/
│   │   ├── shared/ui/                     # Reusable UI components
│   │   │   ├── Button/
│   │   │   ├── Card/
│   │   │   ├── Input/
│   │   │   ├── Select/
│   │   │   ├── Modal/
│   │   │   ├── Badge/
│   │   │   ├── Spinner/
│   │   │   ├── ErrorBoundary/
│   │   │   └── Skeleton/
│   │   ├── store/                         # Redux store
│   │   ├── services/                      # API client
│   │   ├── types/                         # TypeScript type definitions
│   │   ├── hooks/                         # Custom hooks
│   │   └── components/                    # Layout components
│   ├── public/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── tsconfig.json
│
├── docs/
│   ├── PRD.md                             # Product Requirements
│   └── TECH_SPEC.md                       # This document
│
├── .github/workflows/
│   └── ci.yml                            # CI pipeline
├── docker-compose.yml
└── README.md
```

---

## 3. DATABASE ARCHITECTURE

### 3.1 Entity Relationship Diagram (Text)

```
users ──1:N── portfolios ──1:N── holdings
  │                                   
  ├──1:1── user_profiles              
  ├──1:1── investment_preferences     
  ├──1:1── notification_settings      
  ├──1:1── display_preferences        
  ├──1:1── investment_profile         
  ├──1:1── subscription               
  ├──1:1── user_activity              
  ├──1:N── transactions ──N:1── stocks
  ├──1:N── watchlists ──N:1── stocks  
  ├──1:N── chat_history               
  ├──1:N── login_history              
  ├──1:N── user_sessions              
  ├──1:N── payment_history            
  ├──1:N── user_recommendations       
  ├──1:N── password_history           
  ├──1:N── email_verification_tokens  
  └──1:N── user_screener_filters      

stocks ──1:N── company_financials
stocks ──1:N── stock_screener

sector_analysis (standalone — aggregated sector data)
indian_stocks (standalone — Indian market stock data)
```

### 3.2 Indexing Strategy

| Table | Indexes | Rationale |
|---|---|---|
| users | PK(id), UQ(username), UQ(email), IX(email) | Login and uniqueness checks |
| portfolios | PK(id), IX(user_id), IX(user_id, created_at) | User portfolio listing ordered by date |
| holdings | PK(id), IX(portfolio_id), IX(symbol), UQ(portfolio_id, symbol) | Portfolio holdings, symbol lookup, unique constraint |
| transactions | PK(id), IX(user_id), IX(user_id, created_at) | User transaction history |
| watchlists | PK(id), IX(user_id), IX(user_id, stock_id) | User watchlist |
| stocks | PK(id), UQ(symbol), IX(sector) | Symbol lookup, sector grouping |
| indian_stocks | PK(id), UQ(symbol), IX(sector), IX(market_cap_category) | Indian stock search and filtering |
| chat_history | PK(id), IX(user_id), IX(user_id, created_at) | User chat history |
| user_screener_filters | PK(id), IX(user_id) | User saved filters |
| stock_screener | PK(id), UQ(symbol), IX(sector), IX(market_cap_category) | Screener queries |
| company_financials | PK(id), IX(symbol), IX(symbol, year), UQ(symbol, year, quarter) | Financial data queries |

---

## 4. API DESIGN

### 4.1 API Conventions

- **Base URL:** `/api/v1/`
- **Format:** JSON (all requests and responses)
- **Auth:** `Authorization: Bearer <token>` header
- **Pagination:** `?page=1&limit=20` with response `{data: [], total: N, page: P, limit: L}`
- **Errors:** `{detail: "message"}` with appropriate HTTP status
- **Rate Limit:** 429 response with `Retry-After` header
- **Request ID:** `X-Request-ID` header on all responses

### 4.2 Response Envelope

```json
// Success
{
    "data": { ... },
    "meta": { "page": 1, "limit": 20, "total": 100 }
}

// Error
{
    "detail": "Human-readable error message",
    "request_id": "abc12345"
}
```

### 4.3 API Versioning Strategy

- URL-based versioning: `/api/v1/`, `/api/v2/`
- Current: v1
- v2 will include: real market data, WebSocket improvements, GraphQL option

---

## 5. SECURITY ARCHITECTURE

### 5.1 Authentication Flow

```
┌────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
│ Client │    │  FastAPI │    │  Security │    │ Database │
└───┬────┘    └────┬─────┘    └─────┬─────┘    └────┬─────┘
    │  POST /login │               │               │
    │──────────────▶│               │               │
    │               │  brute_force  │               │
    │               │────┬─────────▶│               │
    │               │    │ check    │               │
    │               │◄───┘         │               │
    │               │               │  SELECT user  │
    │               │───────────────┼──────────────▶│
    │               │               │◄──────────────│
    │               │  verify_pass  │               │
    │               │────┬─────────▶│               │
    │               │◄───┘         │               │
    │               │  reset_brute  │               │
    │               │────┬─────────▶│               │
    │               │◄───┘         │               │
    │  {access_token, refresh_token}                │
    │◄──────────────│               │               │
    │               │               │               │
    │  GET /api/v1/* (Bearer)       │               │
    │──────────────▶│               │               │
    │               │  verify_token │               │
    │               │────┬─────────▶│               │
    │               │◄───┘         │               │
    │               │  Process     │               │
    │    Response   │  Request     │               │
    │◄──────────────│               │               │
```

### 5.2 Token Structure

```json
// Access Token (30 min)
{
    "sub": "user@email.com",
    "exp": 1700000000,
    "iat": 1699998200,
    "type": "access"
}

// Refresh Token (7 days)
{
    "sub": "user@email.com", 
    "exp": 1700603000,
    "iat": 1699998200,
    "type": "refresh"
}
```

### 5.3 Security Layers (From Network to Application)

| Layer | Component | Protection |
|---|---|---|
| 1. Network | Nginx | TLS termination, rate limiting, IP blacklist |
| 2. Transport | HTTPS | TLS 1.3, HSTS |
| 3. Application | Security Headers Middleware | CSP, X-Frame-Options, X-XSS-Protection |
| 4. Auth | JWT + bcrypt | Token validation, password hashing |
| 5. Rate Limit | Redis middleware | 100 req/min general, 10/min auth |
| 6. Input | Pydantic validation + sanitization | Type/format validation, XSS strip |
| 7. Database | SQLAlchemy ORM | Parameterized queries (no SQL injection) |
| 8. Error | Global exception handler | No stack trace leakage |
| 9. Monitor | Sentry | Error tracking and alerting |

---

## 6. CACHING STRATEGY

| Data | Cache Strategy | TTL | Storage |
|---|---|---|---|
| Rate limits | sliding window | 60s | Redis |
| Stock prices | write-through | 5s (WebSocket) | In-memory broadcast |
| Sector performance | time-based | 5min | Application cache |
| IPO calendar | time-based | 1hr | Application cache |
| Static translations | cache forever | ∞ (bundle) | CDN / browser |
| API responses | ETag / Last-Modified | per-resource | Browser cache |
| Portfolio data | no-cache | real-time | Direct DB |

---

## 7. ERROR HANDLING STRATEGY

### Global Exception Handler

```python
@router.exception_handler(Exception)
async def global_exception_handler(request, exc):
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    if isinstance(exc, HTTPException):
        return JSONResponse(exc.status_code, {
            "detail": exc.detail,
            "request_id": request_id
        })
    
    # Log full traceback for 500s
    logger.error(f"Unhandled exception [{request_id}]: {exc}", exc_info=True)
    
    # Don't leak internal details
    return JSONResponse(500, {
        "detail": "Internal server error",
        "request_id": request_id
    })
```

---

## 8. LOGGING STRATEGY

| Log Type | Level | Output | Retention |
|---|---|---|---|
| Application | INFO | stdout (Docker) | 30 days |
| Errors | ERROR | stdout + Sentry | 90 days |
| Auth events | INFO | stdout | 1 year (compliance) |
| API access | INFO | stdout | 30 days |
| Database queries | DEBUG | stdout (dev only) | — |
| Rate limit violations | WARNING | stdout | 7 days |

---

## 9. DEPLOYMENT ARCHITECTURE

### 9.1 Docker Services

```yaml
version: '3.8'
services:
  redis:        # Cache + Rate limiting
  postgres:     # Primary database (future)
  backend:      # FastAPI uvicorn (4 workers)
  frontend:     # Nginx serving React build
  nginx:        # Reverse proxy (optional - frontend nginx handles it)
```

### 9.2 Environment Separation

| Environment | DB | Redis | SSL | Debug | Purpose |
|---|---|---|---|---|---|
| development | SQLite file | Optional (falls back) | Self-signed | True | Local dev |
| staging | PostgreSQL | Required | Let's Encrypt | False | Pre-prod testing |
| production | PostgreSQL (HA) | Required | Let's Encrypt | False | Live |

### 9.3 Scaling Strategy

```
Load → Nginx (round-robin) → Backend x4 workers → PostgreSQL (read replica optional)

Horizontal scaling:
1. Increase uvicorn workers (per machine)
2. Add backend instances behind nginx load balancer
3. Add PostgreSQL read replicas
4. Add Redis cluster for rate limiting
5. CDN for static assets

Vertical scaling (first step):
- 2 vCPU → 4 vCPU → 8 vCPU
- 4GB RAM → 8GB → 16GB
- SQLite → PostgreSQL
```

---

## 10. MONITORING & OBSERVABILITY

| Tool | Purpose | Status |
|---|---|---|
| Sentry | Error tracking, performance monitoring | ✅ Integrated |
| Health endpoint | /api/v1/health (DB status, uptime) | ✅ Implemented |
| Request ID tracking | X-Request-ID on all responses | ✅ Implemented |
| Python logging | Application-level logging | ✅ Configured |
| Prometheus | Metrics collection | ❌ Not setup |
| Grafana | Dashboard visualization | ❌ Not setup |
| Uptime monitoring | External monitoring (e.g., UptimeRobot) | ❌ Not setup |
| Log aggregation | ELK / Loki | ❌ Not setup |

---

## 11. KNOWN TECHNICAL DEBT

| Item | Priority | Impact | Effort to Fix |
|---|---|---|---|
| Duplicate `database.py` (root + core/) | High | Confusion, potential import issues | 1hr |
| Duplicate `POST /optimize` endpoint | **Critical** | Unpredictable behavior | 15min |
| In-memory alerts/chat/paper data | High | Data loss on restart | 4hr |
| Mock data only (no real market) | **Critical** | App non-functional in production | 2-3 weeks |
| SQLite → PostgreSQL | **Critical** | Concurrency bottleneck | 1 week |
| No Alembic migrations | High | Schema changes are manual/hacky | 4hr |
| Inconsistent API prefixes | Medium | Developer confusion | 2hr |
| Port 8000 vs 8001 mismatch | High | Docker deployment broken | 5min |
| Demo user hardcoded | Medium | Security risk in production | 1hr |
| CSP `connect-src 'self'` breaks some APIs | Medium | Some external APIs blocked | 30min |
| No frontend tests | High | Regression risk | Ongoing |

---

## 12. FUTURE ARCHITECTURE (V2)

When scaling beyond 10K users, extract these microservices:

```
Frontend (React SPA)
    │
    ├── API Gateway (Nginx / Kong)
    │       │
    │       ├── Auth Service (separate FastAPI)
    │       ├── Portfolio Service
    │       ├── Market Data Service (WebSocket-heavy)
    │       ├── AI Service (GPU-optimized)
    │       ├── Notification Service
    │       └── Export Service
    │
    ├── PostgreSQL (primary write)
    ├── PostgreSQL (read replicas x2)
    ├── Redis Cluster
    ├── RabbitMQ / Kafka (event bus)
    └── S3/MinIO (file storage for exports/reports)
```
