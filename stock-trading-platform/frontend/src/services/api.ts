import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { RootState } from '../store/store';

const baseQuery = fetchBaseQuery({
  baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.token;
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }
    return headers;
  },
});

export const stockApi = createApi({
  reducerPath: 'stockApi',
  baseQuery: baseQuery,
  tagTypes: ['User', 'Stock', 'Portfolio', 'Chat', 'InvestmentProfile', 'Recommendations', 'IndianStock', 'Watchlist'],
  endpoints: (builder) => ({
    // Authentication endpoints
    login: builder.mutation<
      { access_token: string; token_type: string; user: any },
      { email: string; password: string }
    >({
      query: (credentials) => ({
        url: 'auth/login',
        method: 'POST',
        body: credentials,
      }),
      invalidatesTags: ['User'],
    }),

    register: builder.mutation<
      { access_token: string; token_type: string; user: any },
      { username: string; email: string; password: string }
    >({
      query: (userData) => ({
        url: 'auth/register',
        method: 'POST',
        body: userData,
      }),
      invalidatesTags: ['User'],
    }),

    // Stock endpoints
    searchStocks: builder.query<
      { stocks: Array<{ symbol: string; name: string; exchange: string; sector: string; market_cap_category: string }> },
      string
    >({
      query: (query) => `stocks/search/${encodeURIComponent(query)}`,
      providesTags: ['Stock'],
    }),

    getStockPrice: builder.query<
      {
        symbol: string;
        current_price: number;
        previous_close: number;
        change: number;
        change_percent: number;
        volume: number;
        market_cap?: number;
        company_name: string;
      },
      string
    >({
      query: (symbol) => `stocks/price/${encodeURIComponent(symbol)}`,
      providesTags: (result, error, symbol) => [{ type: 'Stock', id: symbol }],
    }),

    getStockDetails: builder.query<
      {
        symbol: string;
        current_price: number;
        previous_close: number;
        change: number;
        change_percent: number;
        volume: number;
        market_cap?: number;
        company_name: string;
        pe_ratio?: number;
        high_52w?: number;
        low_52w?: number;
      },
      string
    >({
      query: (symbol) => `stocks/${encodeURIComponent(symbol)}`,
      providesTags: (result, error, symbol) => [{ type: 'Stock', id: symbol }],
    }),

    getStockHistory: builder.query<
      {
        symbol: string;
        period: string;
        interval: string;
        data: Array<{
          date: string;
          open: number;
          high: number;
          low: number;
          close: number;
          volume: number;
        }>;
      },
      { symbol: string; period?: string; interval?: string }
    >({
      query: ({ symbol, period = '1y', interval = '1d' }) =>
        `stocks/history/${encodeURIComponent(symbol)}?period=${period}&interval=${interval}`,
      providesTags: (result, error, { symbol }) => [{ type: 'Stock', id: `${symbol}_history` }],
    }),

    // Portfolio endpoints
    createPortfolio: builder.mutation<
      { id: number; name: string; description?: string; created_at: string },
      { name: string; description?: string }
    >({
      query: (portfolioData) => ({
        url: 'portfolio/create',
        method: 'POST',
        body: portfolioData,
      }),
      invalidatesTags: ['Portfolio'],
    }),

    listPortfolios: builder.query<
      {
        portfolios: Array<{
          id: number;
          name: string;
          description?: string;
          created_at: string;
        }>;
      },
      void
    >({
      query: () => 'portfolio/list',
      providesTags: ['Portfolio'],
    }),

    // Portfolio optimization
    optimizePortfolio: builder.mutation<
      {
        symbols: string[];
        allocation: Array<{
          symbol: string;
          weight: number;
          percentage: number;
        }>;
        expected_return: number;
        risk: number;
        sharpe_ratio: number;
        optimization_successful: boolean;
      },
      {
        symbols: string[];
        risk_tolerance?: string;
        investment_horizon?: string;
      }
    >({
      query: (request) => ({
        url: 'portfolio/optimize',
        method: 'POST',
        body: request,
      }),
    }),

    // Chat endpoint
    chatWithAI: builder.mutation<
      {
        message: string;
        response: string;
        timestamp: string;
      },
      { message: string }
    >({
      query: (message) => ({
        url: 'chat',
        method: 'POST',
        body: message,
      }),
      invalidatesTags: ['Chat'],
    }),

    // Indian Stock specific endpoints
    getAllIndianStocks: builder.query<
      {
        stocks: Array<{
          symbol: string;
          name: string;
          sector: string;
          market_cap_category: string;
          current_price: number;
          formatted_price: string;
          change: number;
          change_percent: number;
          is_nifty50: boolean;
          is_nifty100: boolean;
          volume: number;
          market_cap: number;
        }>;
      },
      void
    >({
      query: () => 'indian-stocks/all',
      providesTags: ['IndianStock'],
    }),

    getIndianStockPrice: builder.query<
      {
        symbol: string;
        current_price: number;
        previous_close: number;
        change: number;
        change_percent: number;
        volume: number;
        market_cap?: number;
        company_name: string;
        currency: string;
        formatted_price: string;
        pe_ratio?: number;
        dividend_yield?: number;
      },
      string
    >({
      query: (symbol) => `indian-stocks/price/${encodeURIComponent(symbol)}`,
      providesTags: (result, error, symbol) => [{ type: 'IndianStock', id: symbol }],
    }),

    searchIndianStocks: builder.query<
      {
        stocks: Array<{
          symbol: string;
          name: string;
          sector: string;
          market_cap_category: string;
          is_nifty50: boolean;
          is_nifty100: boolean;
          is_nifty500: boolean;
        }>;
      },
      { query: string; limit?: number }
    >({
      query: ({ query, limit = 20 }) =>
        `indian-stocks/search/${encodeURIComponent(query)}?limit=${limit}`,
      providesTags: ['IndianStock'],
    }),

    // Investment Profile endpoints
    createInvestmentProfile: builder.mutation<
      {
        id: number;
        user_id: number;
        investment_amount: number;
        risk_level: string;
        timeline: string;
        investment_goals?: string;
        monthly_income?: number;
        age?: number;
        created_at: string;
      },
      {
        investment_amount: number;
        risk_level: string;
        timeline: string;
        investment_goals?: string;
        monthly_income?: number;
        age?: number;
      }
    >({
      query: (profileData) => ({
        url: 'profile/investment',
        method: 'POST',
        body: profileData,
      }),
      invalidatesTags: ['InvestmentProfile', 'Recommendations'],
    }),

    getInvestmentProfile: builder.query<
      {
        id: number;
        user_id: number;
        investment_amount: number;
        risk_level: string;
        timeline: string;
        investment_goals?: string;
        monthly_income?: number;
        age?: number;
        created_at: string;
        updated_at?: string;
      },
      void
    >({
      query: () => 'profile/investment',
      providesTags: ['InvestmentProfile'],
    }),

    updateInvestmentProfile: builder.mutation<
      {
        id: number;
        user_id: number;
        investment_amount: number;
        risk_level: string;
        timeline: string;
        investment_goals?: string;
        monthly_income?: number;
        age?: number;
        created_at: string;
        updated_at: string;
      },
      Partial<{
        investment_amount: number;
        risk_level: string;
        timeline: string;
        investment_goals: string;
        monthly_income: number;
        age: number;
      }>
    >({
      query: (profileData) => ({
        url: 'profile/investment',
        method: 'PUT',
        body: profileData,
      }),
      invalidatesTags: ['InvestmentProfile', 'Recommendations'],
    }),

    getPortfolioDetails: builder.query<
      {
        id: number;
        name: string;
        description: string;
        user_id: number;
        created_at: string;
        holdings: Array<{
          id: number;
          portfolio_id: number;
          symbol: string;
          quantity: number;
          average_price: number;
          created_at: string;
          current_price: number;
          current_value: number;
          pnl: number;
          pnl_percent: number;
        }>;
        total_value: number;
        total_investment: number;
        total_pnl: number;
        total_pnl_percent: number;
      },
      number
    >({
      query: (id) => `portfolio/${id}`,
      providesTags: (result, error, id) => [{ type: 'Portfolio', id }],
    }),

    addPortfolioItem: builder.mutation<
      { success: boolean; message: string },
      { portfolioId: number; symbol: string; quantity: number; average_price: number }
    >({
      query: ({ portfolioId, ...item }) => ({
        url: `portfolio/${portfolioId}/add`,
        method: 'POST',
        body: item,
      }),
      invalidatesTags: (result, error, { portfolioId }) => [{ type: 'Portfolio', id: portfolioId }],
    }),

    deletePortfolioItem: builder.mutation<
      { success: boolean; message: string },
      { portfolioId: number; itemId: number }
    >({
      query: ({ portfolioId, itemId }) => ({
        url: `portfolio/${portfolioId}/items/${itemId}`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, { portfolioId }) => [{ type: 'Portfolio', id: portfolioId }],
    }),

    updatePortfolioItem: builder.mutation<
      { success: boolean; message: string },
      { portfolioId: number; itemId: number; quantity?: number; average_price?: number }
    >({
      query: ({ portfolioId, itemId, ...body }) => ({
        url: `portfolio/${portfolioId}/items/${itemId}`,
        method: 'PUT',
        body,
      }),
      invalidatesTags: (result, error, { portfolioId }) => [{ type: 'Portfolio', id: portfolioId }],
    }),

    // New Dashboard Endpoints
    getPortfolioHoldings: builder.query<
      {
        holdings: Array<{
          symbol: string;
          name: string;
          quantity: number;
          average_price: number;
          current_price: number;
          current_value: number;
          investment_value: number;
          pnl: number;
          pnl_percent: number;
          portfolio_name: string;
          portfolio_id: number;
        }>;
      },
      void
    >({
      query: () => 'portfolio/holdings',
      providesTags: ['Portfolio'],
    }),

    getWatchlist: builder.query<
      {
        watchlist: Array<{
          id: number;
          symbol: string;
          name: string;
          current_price: number;
          change_percent: number;
          market_cap: number;
          pe_ratio: number;
        }>;
      },
      void
    >({
      query: () => 'watchlist',
      providesTags: ['Watchlist'],
    }),

    removeFromWatchlist: builder.mutation<
      { success: boolean; message: string },
      number
    >({
      query: (id) => ({
        url: `watchlist/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Watchlist'],
    }),

    addToWatchlist: builder.mutation<
      { message: string; id: number },
      { symbol: string }
    >({
      query: (body) => ({
        url: 'watchlist',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Watchlist'],
    }),

    getMarketMovers: builder.query<
      {
        stocks: Array<{
          rank: number;
          symbol: string;
          name: string;
          current_price: number;
          change_percent: number;
          volume: number;
        }>;
      },
      { type: 'gainers' | 'losers'; limit?: number }
    >({
      query: ({ type, limit = 10 }) => `stocks/market-movers?type=${type}&limit=${limit}`,
    }),

    // Personalized Chat endpoint
    personalizedChat: builder.mutation<
      {
        message: string;
        response: string;
        recommendations?: Array<{
          stock_symbol: string;
          recommendation_type: string;
          confidence_score?: number;
          reason?: string;
          target_price?: number;
        }>;
        timestamp: string;
        user_profile_considered: boolean;
      },
      { message: string; include_profile?: boolean }
    >({
      query: (messageData) => ({
        url: 'chat',
        method: 'POST',
        body: messageData,
      }),
      invalidatesTags: ['Chat'],
    }),

    // Screener endpoints
    getScreenerStockDetails: builder.query<
      {
        symbol: string;
        name: string;
        sector: string;
        industry: string;
        current_price: number;
        market_cap: number;
        pe_ratio: number;
        pb_ratio: number;
        roe: number;
        roce: number;
        debt_to_equity: number;
        dividend_yield: number;
        book_value: number;
        face_value: number;
        eps: number;
        sales_growth: number;
        profit_growth: number;
        week_52_high: number;
        week_52_low: number;
        pros: string[];
        cons: string[];
        website?: string;
        market_cap_category: string;
        price_change_1w: number;
        price_change_1m: number;
        price_change_3m: number;
        price_change_6m: number;
        price_change_1y: number;
      },
      string
    >({
      query: (symbol) => `screener/stock/${encodeURIComponent(symbol)}`,
    }),

    getScreenerQuarters: builder.query<
      { quarters: Array<any> },
      string
    >({
      query: (symbol) => `screener/quarters/${encodeURIComponent(symbol)}`,
    }),

    getScreenerPL: builder.query<
      { profit_loss: Array<any> },
      string
    >({
      query: (symbol) => `screener/financials/pl/${encodeURIComponent(symbol)}`,
    }),

    getScreenerBalanceSheet: builder.query<
      { balance_sheet: Array<any> },
      string
    >({
      query: (symbol) => `screener/financials/balance/${encodeURIComponent(symbol)}`,
    }),

    getScreenerCashFlow: builder.query<
      { cash_flow: Array<any> },
      string
    >({
      query: (symbol) => `screener/financials/cashflow/${encodeURIComponent(symbol)}`,
    }),

    getScreenerPeers: builder.query<
      { peers: Array<any> },
      string
    >({
      query: (symbol) => `screener/peers/${encodeURIComponent(symbol)}`,
    }),

    // --- Enhanced Profile Endpoints ---
    getProfileBasic: builder.query<any, void>({
      query: () => 'profile/basic',
      providesTags: ['User'],
    }),
    updateProfileBasic: builder.mutation<any, any>({
      query: (data) => ({
        url: 'profile/basic',
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: ['User'],
    }),
    getNotificationSettings: builder.query<any, void>({
      query: () => 'profile/notifications',
    }),
    updateNotificationSettings: builder.mutation<any, any>({
      query: (data) => ({
        url: 'profile/notifications',
        method: 'PUT',
        body: data,
      }),
    }),
    getDisplayPreferences: builder.query<any, void>({
      query: () => 'profile/display',
    }),
    updateDisplayPreferences: builder.mutation<any, any>({
      query: (data) => ({
        url: 'profile/display',
        method: 'PUT',
        body: data,
      }),
    }),
    getUserActivity: builder.query<any, number | void>({
      query: (limit = 20) => `profile/activity?limit=${limit}`,
    }),
    getLoginHistory: builder.query<any, number | void>({
      query: (limit = 10) => `profile/login-history?limit=${limit}`,
    }),
    getSubscription: builder.query<any, void>({
      query: () => 'profile/subscription',
    }),

    // Get personalized recommendations
    getUserRecommendations: builder.query<
      {
        recommendations: Array<{
          stock_symbol: string;
          recommendation_type: string;
          confidence_score?: number;
          reason?: string;
          target_price?: number;
        }>;
        profile: {
          risk_level: string;
          timeline: string;
          investment_amount: number;
        };
      },
      void
    >({
      query: () => 'recommendations',
      providesTags: ['Recommendations'],
    }),
  }),
});

export const {
  useLoginMutation,
  useRegisterMutation,
  useSearchStocksQuery,
  useGetStockPriceQuery,
  useGetStockDetailsQuery,
  useGetStockHistoryQuery,
  useCreatePortfolioMutation,
  useListPortfoliosQuery,
  useGetPortfolioDetailsQuery,
  useAddPortfolioItemMutation,
  useDeletePortfolioItemMutation,
  useUpdatePortfolioItemMutation,
  useOptimizePortfolioMutation,
  useChatWithAIMutation,
  // Indian Stock hooks
  useGetAllIndianStocksQuery,
  useGetIndianStockPriceQuery,
  useSearchIndianStocksQuery,
  // Investment Profile hooks
  useCreateInvestmentProfileMutation,
  useGetInvestmentProfileQuery,
  useUpdateInvestmentProfileMutation,
  // Personalized features
  usePersonalizedChatMutation,
  useGetUserRecommendationsQuery,
  useGetScreenerStockDetailsQuery,
  useGetScreenerQuartersQuery,
  useGetScreenerPLQuery,
  useGetScreenerBalanceSheetQuery,
  useGetScreenerCashFlowQuery,
  useGetScreenerPeersQuery,
  // Enhanced Profile Hooks
  useGetProfileBasicQuery,
  useUpdateProfileBasicMutation,
  useGetNotificationSettingsQuery,
  useUpdateNotificationSettingsMutation,
  useGetDisplayPreferencesQuery,
  useUpdateDisplayPreferencesMutation,
  useGetUserActivityQuery,
  useGetLoginHistoryQuery,
  useGetSubscriptionQuery,
  // New Dashboard Hooks
  useGetPortfolioHoldingsQuery,
  useGetWatchlistQuery,
  useRemoveFromWatchlistMutation,
  useAddToWatchlistMutation,
  useGetMarketMoversQuery,
} = stockApi;
