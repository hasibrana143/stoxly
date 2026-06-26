# StockTrader Pro - AI-Powered Trading Platform

A comprehensive full-stack stock trading platform built with FastAPI and React, featuring AI-powered portfolio optimization, real-time stock data, and intelligent market analysis.

## 🚀 Features

### Backend (FastAPI)
- **Authentication System**: JWT-based user registration and login
- **Stock Data Integration**: Real-time stock prices and historical data from Yahoo Finance
- **Portfolio Management**: Create and manage multiple portfolios
- **AI Chat Assistant**: Intelligent stock advice and market analysis
- **Portfolio Optimization**: Modern Portfolio Theory-based optimization with Sharpe ratio maximization
- **Database Management**: SQLite/PostgreSQL with SQLAlchemy ORM
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

### Frontend (React + TypeScript)
- **Modern UI**: Clean, responsive design with Tailwind CSS
- **Stock Search**: Search and analyze stocks with real-time data
- **Interactive Charts**: Stock price visualization and technical analysis
- **AI Chatbot**: Natural language interface for investment advice
- **Portfolio Optimizer**: Visual portfolio optimization with risk/return analysis
- **State Management**: Redux Toolkit with RTK Query for efficient data fetching
- **Authentication**: Secure user sessions with JWT tokens

### Supported Markets
- **US Markets**: NASDAQ, NYSE
- **Indian Markets**: NSE, BSE

## 🛠 Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for Python
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **JWT**: JSON Web Tokens for authentication
- **Pandas & NumPy**: Data analysis and numerical computing
- **SciPy**: Scientific computing for optimization algorithms
- **yfinance**: Yahoo Finance API for stock data
- **OpenAI**: AI-powered chat assistant

### Frontend
- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type-safe JavaScript
- **Redux Toolkit**: State management with RTK Query
- **Tailwind CSS**: Utility-first CSS framework
- **Heroicons**: Beautiful SVG icons
- **React Router**: Client-side routing
- **Chart.js**: Interactive charts and graphs
- **React Hot Toast**: Elegant notifications

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock-trading-platform/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   # Copy and edit the .env file
   cp .env.example .env
   ```
   
   Update the `.env` file with your configuration:
   ```env
   DATABASE_URL=sqlite:///./stock_platform.db
   SECRET_KEY=your-very-long-secret-key-here
   OPENAI_API_KEY=your-openai-api-key
   ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
   ```

5. **Run the backend server**
   ```bash
   python main.py
   ```
   
   The API will be available at: http://localhost:8000
   API Documentation: http://localhost:8000/docs

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```
   
   The app will be available at: http://localhost:3000

## 🔧 Configuration

### API Keys Required

1. **OpenAI API Key** (Optional - for AI chat functionality)
   - Sign up at: https://openai.com/
   - Generate API key from dashboard
   - Add to `.env` file

2. **Alpha Vantage API Key** (Optional - for additional stock data)
   - Sign up at: https://www.alphavantage.co/
   - Get free API key
   - Add to `.env` file

### Database Configuration

By default, the application uses SQLite for development. For production, you can use PostgreSQL:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/stock_platform
```

## 🎯 Usage Guide

### 1. User Registration
- Navigate to http://localhost:3000
- Click "Sign up" to create an account
- Fill in your details and register

### 2. Stock Search & Analysis
- Go to "Stock Search" from the navigation
- Search for stocks by symbol (AAPL, GOOGL, etc.) or company name
- Click on any stock to view detailed information and charts

### 3. Portfolio Management
- Visit "Portfolio" section
- Create new portfolios for different investment strategies
- Add stocks to your portfolios

### 4. Portfolio Optimization
- Go to "Optimizer" section
- Add 2 or more stock symbols
- Click "Optimize Portfolio" to get AI-powered allocation suggestions
- View expected returns, risk metrics, and Sharpe ratio

### 5. AI Chat Assistant
- Access "AI Chat" from navigation
- Ask questions about stocks, market trends, or investment advice
- Get intelligent responses based on market knowledge

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Stock Data
- `GET /api/stocks/search/{query}` - Search stocks
- `GET /api/stocks/price/{symbol}` - Get current stock price
- `GET /api/stocks/history/{symbol}` - Get historical stock data

### Portfolio
- `POST /api/portfolio/create` - Create new portfolio
- `GET /api/portfolio/list` - List user portfolios
- `POST /api/portfolio/optimize` - Optimize portfolio allocation

### AI Chat
- `POST /api/chat` - Chat with AI assistant

## 🔐 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📈 Performance Optimization

- **Frontend**: Code splitting, lazy loading, memoization
- **Backend**: Database query optimization, caching with Redis
- **API**: Response compression, rate limiting

## 🚀 Deployment

### Backend Deployment (Heroku/AWS)
1. Set environment variables
2. Configure production database
3. Deploy with gunicorn:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Frontend Deployment (Vercel/Netlify)
1. Build the project:
   ```bash
   npm run build
   ```
2. Deploy the `build` directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the GitHub Issues section
2. Review the API documentation at `/docs`
3. Contact the development team

## 🏗️ Architecture

```
stock-trading-platform/
├── backend/                          # FastAPI Python backend
│   ├── api/v1/                       # Route handlers (9 modules)
│   │   ├── auth.py          Auth endpoints
│   │   ├── stocks.py        Stock data endpoints
│   │   ├── portfolio.py     Portfolio CRUD + optimization
│   │   ├── watchlist.py     Watchlist management
│   │   ├── screener.py      Stock screener + filters
│   │   ├── chat.py          AI chat (public + personalized)
│   │   ├── profile.py       Investment profile
│   │   ├── indian_stocks.py Indian stock explorer
│   │   └── recommendations.py Portfolio recommendations
│   ├── core/                         Config, DB, security
│   ├── services/                     Business logic layer
│   ├── repositories/                 Data access layer (6 repos)
│   ├── middleware/                   Error handler, rate limiter
│   ├── models.py, schemas.py         DB models + Pydantic schemas
│   ├── alembic/                      DB migrations
│   └── tests/                        11 tests across 4 files
├── frontend/                         React + TypeScript
│   ├── src/
│   │   ├── features/                 Feature-based modules (9)
│   │   ├── shared/ui/                Reusable component library
│   │   ├── types/                    Centralized TypeScript types
│   │   └── store/                    Redux store + slices
│   └── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml         CI/CD pipeline
```

### Architecture Patterns
- **Clean Architecture**: Route → Service → Repository (no DB in routes)
- **API Versioning**: All endpoints under `/api/v1/`
- **Rate Limiting**: 100 req/min per IP
- **Request Tracing**: X-Request-ID header on all responses
- **Error Tracking**: Sentry integration
- **DB Migrations**: Alembic with autogenerate
- **CI/CD**: GitHub Actions (lint + test + build)

### Tech Stack
| Layer | Technology |
|-------|------------|
| Backend | FastAPI, SQLAlchemy, Alembic |
| Frontend | React 18, Redux Toolkit, Tailwind CSS |
| AI | Google Gemini API |
| Real-time | WebSocket |
| Monitoring | Sentry |
| Infrastructure | Docker, GitHub Actions |

## 🔄 Future Enhancements (cont.)

- [ ] Advanced technical indicators
- [ ] Options trading support
- [ ] Social trading features
- [ ] Mobile app (React Native)
- [ ] Backtesting functionality
- [ ] Risk assessment tools
- [ ] News sentiment analysis

---

**Built with ❤️ using FastAPI and React**
