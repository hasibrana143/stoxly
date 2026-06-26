# STOXLY.AI — Product Requirements Document (PRD)
**Version:** 1.0  
**Status:** Draft  
**Last Updated:** 2026-06-26  
**Author:** Product Management Team  

---

## 1. EXECUTIVE SUMMARY

Stoxly.ai is a comprehensive Indian stock market analysis and trading platform that combines traditional portfolio management with AI-powered insights, technical analysis, paper trading, and multi-language support. The platform targets Indian retail investors who want a single, intelligent dashboard for managing their stock market activities.

**Vision:** Become the go-all-in-one platform for Indian retail investors — combining research, analysis, portfolio management, and education in one place with AI as the core differentiator.

**Current State:** Functional MVP with ~95 API endpoints, 20+ database models, React frontend, and extensive feature set. However, lacks production-grade data integration, proper testing coverage, and deployment hardening.

---

## 2. TARGET USERS

| Persona | Description | Needs |
|---|---|---|
| **Retail Investor (Primary)** | Indian individual investing in stocks, 25-45 yrs, tech-savvy | Portfolio tracking, research, AI insights, paper trading |
| **Beginner Trader (Secondary)** | New to stock market, wants to learn without risk | Paper trading, educational content, screener tutorials |
| **Experienced Trader (Tertiary)** | Active trader with multiple portfolios | Advanced technicals, portfolio optimization, alerts |
| **NRI Investor** | NRI looking to invest in Indian markets | Multi-language, currency conversion, tax info |

---

## 3. USER ROLES & PERMISSIONS

| Role | Permissions |
|---|---|
| **Guest** | View stock prices, search, sector heatmap, IPO calendar, i18n |
| **Free User** | Guest + 1 portfolio, 10 watchlist items, basic analysis, paper trading, 5 alerts/day |
| **Premium User** | Free + unlimited portfolios, AI analysis, portfolio optimization, export, priority support |
| **Pro User** | Premium + real-time data, advanced analytics, API access, unlimited alerts |
| **Admin** | All + user management, system monitoring, content management |
| **Demo User** | Pre-seeded account with demo@stoxly.ai / demo123 for platform evaluation |

---

## 4. CORE FEATURES

### 4.1 Authentication & Security (P0)
- [x] Email/Password registration with CAPTCHA
- [x] JWT access + refresh token rotation
- [x] 2FA via Google Authenticator (TOTP)
- [x] Email verification flow
- [x] Password policy (min 8 chars, complexity)
- [x] Password expiry (90 days) + history (last 5)
- [x] Brute force protection (5 attempts → 15min lockout)
- [x] Rate limiting (Redis-based, per IP)

### 4.2 Market Data & Discovery (P0)
- [x] Stock search with fuzzy matching & autocomplete
- [x] Stock details (price, PE, PB, ROE, 52wk range)
- [x] Market movers (gainers, losers, active)
- [x] Sector performance & heatmap
- [x] Nifty/Sensex quick stats
- [ ] **REAL MARKET DATA INTEGRATION** — currently mock data only

### 4.3 Portfolio Management (P0)
- [x] Multiple portfolios per user
- [x] Holdings CRUD with quantity/price tracking
- [x] Portfolio analytics (value, P&L, diversification)
- [x] Sector allocation pie
- [x] Rebalancing suggestions

### 4.4 Portfolio Optimization (P1)
- [x] Mean-Variance (Markowitz) optimization
- [x] Efficient frontier visualization data
- [x] Black-Litterman model
- [x] VaR/CVaR risk metrics
- [x] Sharpe ratio calculation

### 4.5 Watchlist (P0)
- [x] Add/remove stocks
- [x] Current price display
- [x] Real-time updates via WebSocket

### 4.6 Stock Screener (P1)
- [x] 50+ financial metrics
- [x] 6 preset filters
- [x] Custom filter saving
- [x] Peer comparison
- [x] Quarterly/annual financials (P&L, Balance Sheet, Cash Flow)

### 4.7 Technical Analysis (P1)
- [x] SMA, EMA, RSI, MACD
- [x] Bollinger Bands, Stochastic, ATR, OBV
- [ ] **REAL DATA NEEDED** — currently uses simulated prices

### 4.8 AI Features (P1)
- [x] AI chat assistant (V1 keyword + Gemini, V2 context-aware)
- [x] Stock analysis with ratings & target prices
- [x] Personalized recommendations based on investment profile
- [x] Daily market brief generation

### 4.9 Paper Trading (P2)
- [x] Virtual ₹10L account
- [x] Market/limit orders
- [x] Holdings with P&L
- [x] Transaction history
- [x] Leaderboard

### 4.10 Price Alerts (P2)
- [x] Create alerts (above/below target)
- [x] CRUD operations
- [x] Alert checking endpoint
- [ ] **PERSISTENCE NEEDED** — currently in-memory only

### 4.11 IPO & Events (P2)
- [x] Upcoming/recent IPO calendar
- [x] F&O expiry calendar
- [x] Individual IPO detail

### 4.12 Stock Comparison (P2)
- [x] Side-by-side metrics comparison
- [x] Radar chart data vs sector averages

### 4.13 Export (P2)
- [x] Portfolio CSV export
- [x] Transactions CSV export
- [x] Watchlist CSV export
- [x] Portfolio report (JSON/CSV)

### 4.14 Multi-Language (P2)
- [x] 7 languages: English, Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati
- [x] 60+ UI string translations
- [x] Language listing endpoint
- [ ] **NUMBER FORMAT LOCALIZATION** — incomplete

### 4.15 User Profile (P1)
- [x] Investment profile (risk, goals, income, age)
- [x] Display preferences (theme, currency, format)
- [x] Notification settings
- [x] Subscription & payment history
- [x] Activity & login history

### 4.16 WebSocket (P1)
- [x] Real-time stock price updates every 5s
- [x] Token-based authentication

---

## 5. OPTIONAL / FUTURE FEATURES (P3)

- Real broker integration (Zerodha, Angel, Upstox APIs)
- Mutual fund & ETF tracking
- Tax harvesting recommendations
- Social trading (follow top paper traders)
- Community features (discussions, stock ideas)
- Advanced charting with drawing tools
- Mobile app (React Native / Flutter)
- SMS/WhatsApp/Telegram alerts
- Multi-currency support for NRIs
- SIP calculator & goal planning
- Stock split / bonus history
- Corporate actions calendar

---

## 6. BUSINESS LOGIC

### Authentication Flow
```
Register → Email Verification → Login → (2FA if enabled) → Access Token (30min) + Refresh Token (7d)
Password Change → Password History Check (last 5) → Force re-login
Password Expired (90 days) → Force change on login
```

### Portfolio Math
```
Holding Value = quantity × current_price
Total Investment = ∑ (quantity_i × avg_price_i)
Total P&L = Total Value − Total Investment
P&L % = (Total P&L / Total Investment) × 100
Sector Allocation % = Sector_Value / Total_Value × 100
Diversification Score = 1 − ∑(weight_i²)   [Herfindahl-Hirschman Index normalized]
```

### Paper Trading Rules
- Initial balance: ₹10,00,000
- No short selling
- Market orders fill instantly at current price
- No brokerage/STT/Demat charges (education mode)
- 5-minute cooldown after sell before buying same stock (anti-day-trading for learning)
- Leaderboard rank by total return %

### Alert Engine
- Check alerts every 5 minutes (background task)
- Triggered when price crosses threshold
- Email/push notification (TBD which channel)
- Max 5 active alerts for Free, unlimited for Premium/Pro

---

## 7. MONETIZATION MODEL

| Tier | Price | Limits |
|---|---|---|
| **Free** | ₹0 | 1 portfolio, 10 watchlist, 5 alerts/day, basic analysis |
| **Premium** | ₹199/mo | Unlimited everything, AI analysis, export, priority |
| **Pro** | ₹499/mo | Real-time data, advanced analytics, API access, priority support |

*Note: Monetization is defined but not implemented. The subscription model exists in DB but no payment gateway is connected.*

---

## 8. TECHNICAL REQUIREMENTS

### Performance
- API response time: <200ms for 95th percentile (cached), <500ms for uncached
- WebSocket latency: <1s from server to client
- Page load: <3s first meaningful paint
- Concurrent users: 1,000+ (initial), 10,000+ (post-scaling)

### Security (OWASP Top 10 Compliant)
- ✅ A01: Broken Access Control — JWT + role-based
- ✅ A02: Cryptographic Failures — bcrypt, JWT, TOTP
- ✅ A03: Injection — SQLAlchemy ORM, input sanitization
- ✅ A04: Insecure Design — Rate limiting, CSP headers
- ✅ A05: Security Misconfiguration — Env validation
- ❌ A06: Vulnerable Components — No automated scanning
- ❌ A07: Auth Failures — No session invalidation
- ✅ A08: Data Integrity — JWT signing
- ✅ A09: Logging & Monitoring — Sentry
- ✅ A10: SSRF — httpx with timeouts

### Compliance
- GDPR: User data export, account deletion
- SEBI: Disclaimer for investment advice
- IT Act 2000: Indian IT compliance

---

## 9. SCALING EXPECTATIONS

| Metric | MVP (Current) | 6 Months | 12 Months |
|---|---|---|---|
| Users | <100 | 5,000 | 50,000 |
| Concurrent | <10 | 500 | 5,000 |
| API req/min | ~50 | 5,000 | 50,000 |
| Data storage | MBs | GBs | 100s GBs |
| DB | SQLite | PostgreSQL | PostgreSQL + read replicas |

**Action Required:** SQLite → PostgreSQL migration is the #1 blocking issue for scaling beyond 10 concurrent users.

---

## 10. DEPENDENCIES & INTEGRATIONS

| Dependency | Status | Criticality |
|---|---|---|
| Google Gemini API | ✅ Integrated | High — AI features |
| Redis | ✅ Integrated (optional) | Medium — rate limiting |
| Sentry | ✅ Integrated | Low — monitoring |
| Real Market Data Provider | ❌ Missing | **Critical** |
| Email Service (SMTP) | ✅ Code, ❌ configured | High — verification |
| reCAPTCHA | ✅ Code, ❌ configured | Medium |
| Payment Gateway | ❌ Missing | Low — monetization |
| SMS Provider | ❌ Missing | Low — alerts |

---

## 11. RISKS & MITIGATION

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| No real market data | App is non-functional in production | High | Integrate Alpha Vantage / Yahoo Finance / BSE API |
| SQLite concurrency | DB corruption with >10 concurrent users | High | Migrate to PostgreSQL before launch |
| In-memory storage | Data loss on restart (alerts, chat, paper trading) | Medium | Persist to DB |
| Duplicate `/optimize` endpoint | Unpredictable behavior | High | Remove duplicate |
| No frontend tests | Regression bugs | Medium | Add critical path tests |
| Demo credentials exposed | Security risk | Medium | Make configurable, disable in production |
| Port mismatch (8000 vs 8001) | Docker deployment fails | High | Fix to single port |
| No backup strategy | Data loss | Medium | Implement automated backups |

---

## 12. SUCCESS METRICS (KPIs)

| Metric | Target |
|---|---|
| User acquisition rate | 500 new users/month |
| DAU/MAU ratio | >30% |
| Avg session duration | >8 minutes |
| Paper trading conversion to real | >15% |
| Premium conversion rate | >5% |
| API uptime | 99.9% |
| API p95 latency | <200ms |
| Test coverage | >70% |
| Bug recurrence rate | <5% |
| CSAT score | >4.2/5 |

---

## 13. PHASED ROADMAP

### Phase 1 — Foundation (Current) ✅
- All current features as documented above
- Docker setup with Redis
- CI pipeline
- Basic tests (13)

### Phase 2 — Production Hardening (Next)
- **Real market data integration** — highest priority
- SQLite → PostgreSQL migration with Alembic
- Persist alerts, chat, paper trading to DB
- Fix duplicate endpoint
- Port consistency (8000)
- Proper testing (unit + integration + E2E)
- Error tracking dashboard

### Phase 3 — Growth
- Payment gateway integration
- Real broker APIs
- Mobile app
- Social features
- Advanced analytics
- Marketing site

### Phase 4 — Scale
- Read replicas
- CDN for static assets
- Multi-region deployment
- Microservices extraction (AI service, data service)

---

## 14. APPENDIX

### A. Tech Stack Decision Matrix

| Component | Chosen | Alternatives Considered | Rationale |
|---|---|---|---|
| Backend Framework | FastAPI (Python) | Node.js/Express, Go/Gin | FastAPI has native async, automatic OpenAPI docs, Pydantic validation |
| ORM | SQLAlchemy | Prisma, TypeORM | Mature, async support, wide DB compatibility |
| Frontend | React 18 | Next.js, Vue, Svelte | Existing codebase, rich ecosystem |
| State Management | Redux Toolkit | Zustand, Jotai | RTK Query for API caching, familiar pattern |
| Database | SQLite → PostgreSQL | MySQL, MongoDB | PostgreSQL has best Indian market support, JSON fields for flexible schemas |
| Cache | Redis | Memcached | Multi-data structure support, pub/sub for WebSocket |
| AI | Google Gemini | OpenAI, Claude | Better Indian context, cheaper |
| Container | Docker | Kubernetes (overkill now) | Simple, universal |
| Cloud | TBD | AWS, GCP, Azure | Decision deferred |

### B. Database Migration Plan
1. Export SQLite data via `sqlite3 .dump`
2. Set up PostgreSQL in Docker
3. Run Alembic migrations against PostgreSQL
4. Import data with transformation
5. Update DATABASE_URL in production env
6. Test all endpoints
7. Switch traffic

### C. Real Data Provider Evaluation
| Provider | Coverage | Cost | Reliability | API Limit |
|---|---|---|---|---|
| Yahoo Finance (yfinance) | BSE/NSE | Free | Good but unofficial | 2000 req/hr |
| Alpha Vantage | BSE/NSE | Free tier 5 req/min | Excellent | 5/min free |
| BSE Direct API | BSE only | Free | Official | Unknown |
| NSE Direct API | NSE only | Free | Official | Unknown |
| Zerodha Kite API | NSE/BSE with broker | Paid | Excellent | Depends on plan |
| Upstox API | NSE/BSE with broker | Paid | Excellent | Depends on plan |
