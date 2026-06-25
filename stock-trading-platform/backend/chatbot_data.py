
# Comprehensive Q&A Knowledge Base for Stock Trading Chatbot

QA_PAIRS = [
    # Basic Stock Market Concepts
    {
        "keywords": ["what is a stock", "define stock", "meaning of stock", "stock definition"],
        "answer": "A stock (also known as equity) represents a fractional ownership in a company. When you buy a stock, you become a shareholder and own a part of that company's assets and earnings."
    },
    {
        "keywords": ["what is the stock market", "define stock market", "stock market meaning"],
        "answer": "The stock market is a collection of exchanges where the buying and selling of shares of publicly held companies take place. It serves as a marketplace for investors to trade stocks."
    },
    {
        "keywords": ["what is a bull market", "bull market meaning", "bull market"],
        "answer": "A bull market is a financial market condition where prices are rising or are expected to rise. It is characterized by optimism, investor confidence, and expectations that strong results should continue."
    },
    {
        "keywords": ["what is a bear market", "bear market meaning", "bear market"],
        "answer": "A bear market is when a market experiences prolonged price declines. It typically describes a condition in which securities prices fall 20% or more from recent highs amid widespread pessimism and negative investor sentiment."
    },
    {
        "keywords": ["what is a dividend", "define dividend", "dividend meaning", "dividends"],
        "answer": "A dividend is a distribution of a portion of a company's earnings, decided by the board of directors, to a class of its shareholders. It is often paid in cash but can also be in the form of additional stock."
    },
    {
        "keywords": ["what is ipo", "initial public offering", "ipo meaning"],
        "answer": "IPO stands for Initial Public Offering. It is the process by which a private company can go public by selling its stocks to the general public for the first time."
    },
    {
        "keywords": ["what is market capitalization", "market cap meaning", "market cap"],
        "answer": "Market capitalization (or market cap) is the total value of all a company's shares of stock. It is calculated by multiplying the price of a stock by its total number of outstanding shares."
    },
    {
        "keywords": ["what is sensex", "define sensex", "sensex meaning"],
        "answer": "Sensex, also known as the S&P BSE Sensex, is the benchmark index of the Bombay Stock Exchange (BSE) in India. It comprises 30 of the largest and most actively traded stocks on the BSE."
    },
    {
        "keywords": ["what is nifty", "define nifty", "nifty 50", "nifty meaning"],
        "answer": "Nifty 50 is the benchmark index of the National Stock Exchange (NSE) of India. It represents the weighted average of 50 of the largest Indian companies listed on the NSE."
    },
    {
        "keywords": ["what is sebi", "role of sebi", "sebi meaning"],
        "answer": "SEBI (Securities and Exchange Board of India) is the regulatory body for the securities and commodity market in India. Its role is to protect the interests of investors and promote the development of the securities market."
    },
    {
        "keywords": ["what is demat account", "demat meaning", "demat account"],
        "answer": "A Demat (Dematerialized) account is an account used to hold shares and securities in an electronic format. It is mandatory for trading in the Indian stock market."
    },
    {
        "keywords": ["what is trading account", "trading account meaning", "trading account"],
        "answer": "A trading account is used to place buy or sell orders in the stock market. It acts as an interface between your bank account and your Demat account."
    },
    {
        "keywords": ["difference between demat and trading account", "demat vs trading"],
        "answer": "A Demat account holds your shares in electronic form (like a bank locker), while a trading account is used to execute buy and sell orders in the market."
    },
    {
        "keywords": ["what is intraday trading", "intraday meaning", "intraday"],
        "answer": "Intraday trading involves buying and selling stocks within the same trading day. Positions are not held overnight, and the goal is to profit from short-term price movements."
    },
    {
        "keywords": ["what is delivery trading", "delivery meaning", "delivery trade"],
        "answer": "Delivery trading involves buying stocks and holding them for more than one day. The stocks are delivered to your Demat account, and you become a shareholder."
    },
    {
        "keywords": ["what is short selling", "short sell", "shorting"],
        "answer": "Short selling is a trading strategy where an investor sells a stock they do not own, anticipating that the price will fall. They aim to buy it back later at a lower price to make a profit."
    },
    {
        "keywords": ["what is stop loss", "stop loss meaning", "stop loss"],
        "answer": "A stop-loss order is an order placed with a broker to buy or sell a stock once the stock reaches a certain price. It is designed to limit an investor's loss on a position."
    },
    {
        "keywords": ["what is limit order", "limit order meaning", "limit order"],
        "answer": "A limit order is an order to buy or sell a stock at a specific price or better. A buy limit order can only be executed at the limit price or lower, and a sell limit order at the limit price or higher."
    },
    {
        "keywords": ["what is market order", "market order meaning", "market order"],
        "answer": "A market order is an order to buy or sell a stock immediately at the best available current price."
    },
    {
        "keywords": ["what is blue chip stock", "blue chip meaning", "blue chip"],
        "answer": "Blue-chip stocks are shares of large, well-established, and financially sound companies with a history of reliable performance. They are considered safe investments."
    },
    
    # Fundamental Analysis
    {
        "keywords": ["what is pe ratio", "price to earnings ratio", "pe ratio"],
        "answer": "The Price-to-Earnings (P/E) ratio measures a company's current share price relative to its per-share earnings. It helps investors determine if a stock is overvalued or undervalued."
    },
    {
        "keywords": ["what is eps", "earnings per share", "eps meaning"],
        "answer": "Earnings Per Share (EPS) is the portion of a company's profit allocated to each outstanding share of common stock. It serves as an indicator of a company's profitability."
    },
    {
        "keywords": ["what is roe", "return on equity", "roe meaning"],
        "answer": "Return on Equity (ROE) measures financial performance by calculating the ratio of net income to shareholders' equity. It indicates how effectively management is using a company's assets to create profits."
    },
    {
        "keywords": ["what is book value", "book value meaning", "book value"],
        "answer": "Book value is the net value of a company's assets minus its liabilities as recorded on its balance sheet. It represents the theoretical value shareholders would receive if the company were liquidated."
    },
    {
        "keywords": ["what is pb ratio", "price to book ratio", "pb ratio"],
        "answer": "The Price-to-Book (P/B) ratio compares a company's market value to its book value. A lower P/B ratio could mean the stock is undervalued."
    },
    {
        "keywords": ["what is debt to equity ratio", "debt equity ratio", "debt to equity"],
        "answer": "The Debt-to-Equity (D/E) ratio is used to evaluate a company's financial leverage. It is calculated by dividing a company's total liabilities by its shareholder equity."
    },
    {
        "keywords": ["what is dividend yield", "dividend yield meaning", "dividend yield"],
        "answer": "Dividend yield is a financial ratio that shows how much a company pays out in dividends each year relative to its stock price."
    },
    {
        "keywords": ["what is face value", "face value of stock", "face value"],
        "answer": "Face value is the nominal value of a security as stated by the issuer. For stocks, it is the original cost of the stock shown on the certificate."
    },
    {
        "keywords": ["what is beta", "stock beta", "beta meaning"],
        "answer": "Beta is a measure of a stock's volatility in relation to the overall market. A beta greater than 1 indicates the stock is more volatile than the market, while less than 1 indicates less volatility."
    },
    {
        "keywords": ["what is fundamental analysis", "fundamental analysis"],
        "answer": "Fundamental analysis is a method of evaluating a security by attempting to measure its intrinsic value by examining related economic, financial, and other qualitative and quantitative factors."
    },

    # Technical Analysis
    {
        "keywords": ["what is technical analysis", "technical analysis"],
        "answer": "Technical analysis is a trading discipline employed to evaluate investments and identify trading opportunities by analyzing statistical trends gathered from trading activity, such as price movement and volume."
    },
    {
        "keywords": ["what is rsi", "relative strength index", "rsi meaning"],
        "answer": "The Relative Strength Index (RSI) is a momentum indicator used in technical analysis that measures the magnitude of recent price changes to evaluate overbought or oversold conditions."
    },
    {
        "keywords": ["what is macd", "moving average convergence divergence", "macd meaning"],
        "answer": "MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a security's price."
    },
    {
        "keywords": ["what is moving average", "sma", "ema", "moving average"],
        "answer": "A moving average is a stock indicator that is commonly used in technical analysis. The reason for calculating the moving average of a stock is to help smooth out the price data by creating a constantly updated average price."
    },
    {
        "keywords": ["what is candlestick chart", "candlestick meaning", "candlestick"],
        "answer": "A candlestick chart is a style of financial chart used to describe price movements of a security, derivative, or currency. Each 'candlestick' typically shows one day, thus a one-month chart may show the 20 trading days as 20 candlesticks."
    },
    {
        "keywords": ["what is support and resistance", "support and resistance"],
        "answer": "Support and resistance are price levels on charts that tend to act as barriers, preventing the price of an asset from getting pushed in a certain direction."
    },
    {
        "keywords": ["what is bollinger bands", "bollinger bands"],
        "answer": "Bollinger Bands are a technical analysis tool defined by a set of trendlines plotted two standard deviations (positively and negatively) away from a simple moving average (SMA) of a security's price."
    },
    {
        "keywords": ["what is volume", "trading volume", "volume meaning"],
        "answer": "Volume is the number of shares or contracts traded in a security or an entire market during a given period of time. It is a key indicator of market activity and liquidity."
    },
    {
        "keywords": ["what is breakout", "stock breakout", "breakout meaning"],
        "answer": "A breakout occurs when a stock price moves outside a defined support or resistance level with increased volume. A breakout is entered by a trader who takes a long position after the stock price breaks above resistance or takes a short position after the stock breaks below support."
    },
    {
        "keywords": ["what is trend line", "trend line"],
        "answer": "A trendline is a straight line that connects two or more price points and then extends into the future to act as a line of support or resistance."
    },

    # Investment Strategies
    {
        "keywords": ["what is value investing", "value investing"],
        "answer": "Value investing is an investment strategy that involves picking stocks that appear to be trading for less than their intrinsic or book value."
    },
    {
        "keywords": ["what is growth investing", "growth investing"],
        "answer": "Growth investing is a strategy focused on capital appreciation. Growth investors look for companies that exhibit signs of above-average growth, even if the share price appears expensive."
    },
    {
        "keywords": ["what is sip", "systematic investment plan", "sip meaning"],
        "answer": "SIP (Systematic Investment Plan) is a facility offered by mutual funds to investors to invest in a disciplined manner. It allows an investor to invest a fixed amount of money at pre-defined intervals."
    },
    {
        "keywords": ["what is diversification", "diversification meaning"],
        "answer": "Diversification is a risk management strategy that mixes a wide variety of investments within a portfolio. The rationale is that a portfolio constructed of different kinds of assets will, on average, yield higher long-term returns and lower the risk of any individual holding."
    },
    {
        "keywords": ["what is asset allocation", "asset allocation"],
        "answer": "Asset allocation is an investment strategy that aims to balance risk and reward by apportioning a portfolio's assets according to an individual's goals, risk tolerance, and investment horizon."
    },
    {
        "keywords": ["what is compounding", "power of compounding", "compounding meaning"],
        "answer": "Compounding is the process in which an asset's earnings, from either capital gains or interest, are reinvested to generate additional earnings over time."
    },
    {
        "keywords": ["what is mutual fund", "mutual fund meaning"],
        "answer": "A mutual fund is a company that pools money from many investors and invests the money in securities such as stocks, bonds, and short-term debt."
    },
    {
        "keywords": ["what is etf", "exchange traded fund", "etf meaning"],
        "answer": "An ETF (Exchange Traded Fund) is a type of pooled investment security that operates much like a mutual fund. Typically, ETFs will track a particular index, sector, commodity, or other assets, but unlike mutual funds, ETFs can be purchased or sold on a stock exchange the same way that a regular stock can."
    },
    {
        "keywords": ["what is index fund", "index fund meaning"],
        "answer": "An index fund is a type of mutual fund or exchange-traded fund (ETF) with a portfolio constructed to match or track the components of a financial market index, such as the Nifty 50 or Sensex."
    },
    {
        "keywords": ["long term vs short term investment", "long term investment", "short term investment"],
        "answer": "Long-term investing involves holding assets for years or decades to build wealth gradually, while short-term investing involves buying and selling assets over shorter periods (days to months) to profit from price fluctuations."
    },

    # Risk Management
    {
        "keywords": ["how to manage risk", "risk management"],
        "answer": "Risk management in trading involves setting stop-losses, diversifying your portfolio, not investing more than you can afford to lose, and understanding the risk-reward ratio of each trade."
    },
    {
        "keywords": ["what is risk reward ratio", "risk reward"],
        "answer": "The risk/reward ratio marks the prospective reward an investor can earn for every dollar they risk on an investment. A common ratio is 1:2 or 1:3."
    },
    {
        "keywords": ["what is hedging", "hedging meaning"],
        "answer": "Hedging is a risk management strategy employed to offset losses in investments by taking an opposite position in a related asset."
    },
    {
        "keywords": ["what is portfolio rebalancing", "portfolio rebalancing"],
        "answer": "Portfolio rebalancing is the process of realigning the weightings of a portfolio of assets. It involves periodically buying or selling assets to maintain an original or desired level of asset allocation."
    },
    {
        "keywords": ["what is averaging down", "averaging down"],
        "answer": "Averaging down is an investment strategy that involves buying more shares of a stock as its price drops, thereby lowering the average cost per share."
    },

    # Platform Specific (Mock)
    {
        "keywords": ["how to buy stock", "how to trade", "buy stock"],
        "answer": "To buy a stock on this platform, search for the stock symbol, go to the stock details page, click on the 'Buy' button, enter the quantity, and confirm your order."
    },
    {
        "keywords": ["how to sell stock", "sell stock"],
        "answer": "To sell a stock, go to your Portfolio, select the stock you wish to sell, click 'Sell', enter the quantity, and confirm the transaction."
    },
    {
        "keywords": ["how to create portfolio", "create portfolio"],
        "answer": "You can create a new portfolio by navigating to the Portfolio section and clicking on 'Create New Portfolio'. Give it a name and description to get started."
    },
    {
        "keywords": ["how to use screener", "use screener"],
        "answer": "The Stock Screener allows you to filter stocks based on various criteria like Market Cap, P/E Ratio, and Sector. Go to the 'Screener' tab to start filtering."
    },
    {
        "keywords": ["is my data safe", "data security", "privacy"],
        "answer": "Yes, we use industry-standard encryption to protect your personal and financial data. Your security is our top priority."
    },
    {
        "keywords": ["contact support", "customer care", "support"],
        "answer": "You can reach our support team via the 'Contact Us' page or email us at support@stoxly.ai."
    },
    {
        "keywords": ["forgot password", "reset password"],
        "answer": "If you forgot your password, click on the 'Forgot Password' link on the login page and follow the instructions to reset it via email."
    },
    {
        "keywords": ["what is watchlist", "watchlist"],
        "answer": "A watchlist is a feature where you can track the performance of specific stocks that you are interested in without buying them."
    },
    {
        "keywords": ["how to add to watchlist", "add to watchlist"],
        "answer": "You can add a stock to your watchlist by clicking the 'Star' icon or 'Add to Watchlist' button on any stock's detail page."
    },
    {
        "keywords": ["are the prices real time", "real time prices"],
        "answer": "The prices displayed on the platform are simulated for demonstration purposes in this version. In a live production environment, they would be real-time."
    },

    # Advanced Concepts
    {
        "keywords": ["what is f&o", "futures and options", "f&o"],
        "answer": "Futures and Options (F&O) are derivative contracts. Futures obligate the buyer/seller to transact at a future date and price. Options give the right, but not the obligation, to buy/sell at a specific price."
    },
    {
        "keywords": ["what is call option", "call option"],
        "answer": "A Call Option gives the holder the right to buy a stock at a specified price within a specific time period."
    },
    {
        "keywords": ["what is put option", "put option"],
        "answer": "A Put Option gives the holder the right to sell a stock at a specified price within a specific time period."
    },
    {
        "keywords": ["what is margin trading", "margin trading"],
        "answer": "Margin trading involves borrowing funds from a broker to trade a financial asset, which forms the collateral for the loan from the broker."
    },
    {
        "keywords": ["what is upper circuit", "upper circuit"],
        "answer": "The upper circuit is the maximum percentage a stock price is allowed to move upwards in a single trading day. Once hit, trading may be halted or restricted."
    },
    {
        "keywords": ["what is lower circuit", "lower circuit"],
        "answer": "The lower circuit is the minimum percentage a stock price is allowed to move downwards in a single trading day."
    },
    {
        "keywords": ["what is bonus share", "bonus share"],
        "answer": "Bonus shares are additional shares given to the current shareholders without any additional cost, based upon the number of shares that a shareholder owns."
    },
    {
        "keywords": ["what is stock split", "stock split"],
        "answer": "A stock split is a corporate action in which a company divides its existing shares into multiple shares to boost the liquidity of the shares."
    },
    {
        "keywords": ["what is buyback", "buyback"],
        "answer": "A buyback, or share repurchase, is when a company buys its own outstanding shares to reduce the number of shares available on the open market."
    },
    {
        "keywords": ["what is insider trading", "insider trading"],
        "answer": "Insider trading is the trading of a public company's stock or other securities (such as bonds or stock options) based on material, nonpublic information about the company. It is illegal."
    },
    {
        "keywords": ["what is bull run", "bull run"],
        "answer": "A bull run is a period of time during which stock prices are consistently rising."
    },
    {
        "keywords": ["what is correction", "market correction"],
        "answer": "A market correction is a decline of 10% or more in the price of a security, asset, or a financial market from its most recent peak."
    },
    {
        "keywords": ["what is volatility", "volatility"],
        "answer": "Volatility is a statistical measure of the dispersion of returns for a given security or market index. Higher volatility means the price can change dramatically over a short time period."
    },
    {
        "keywords": ["what is liquidity", "liquidity"],
        "answer": "Liquidity refers to the efficiency or ease with which an asset or security can be converted into ready cash without affecting its market price."
    },
    {
        "keywords": ["what is portfolio", "portfolio meaning"],
        "answer": "A portfolio is a collection of financial investments like stocks, bonds, commodities, cash, and cash equivalents, including closed-end funds and exchange-traded funds (ETFs)."
    },
    {
        "keywords": ["what is roi", "return on investment", "roi meaning"],
        "answer": "Return on Investment (ROI) is a performance measure used to evaluate the efficiency or profitability of an investment."
    },
    {
        "keywords": ["what is cagr", "compound annual growth rate", "cagr meaning"],
        "answer": "CAGR is the mean annual growth rate of an investment over a specified period of time longer than one year."
    },
    {
        "keywords": ["what is fiscal deficit", "fiscal deficit"],
        "answer": "Fiscal deficit is the difference between the total revenue and the total expenditure of the government. It indicates the amount of money the government needs to borrow."
    },
    {
        "keywords": ["what is gdp", "gross domestic product", "gdp meaning"],
        "answer": "GDP is the total monetary or market value of all the finished goods and services produced within a country's borders in a specific time period."
    },
    {
        "keywords": ["what is inflation", "inflation meaning"],
        "answer": "Inflation is the rate at which the general level of prices for goods and services is rising and, consequently, the purchasing power of currency is falling."
    },
    {
        "keywords": ["what is repo rate", "repo rate"],
        "answer": "Repo rate is the rate at which the central bank of a country (RBI in India) lends money to commercial banks in the event of any shortfall of funds."
    },
    {
        "keywords": ["what is reverse repo rate", "reverse repo rate"],
        "answer": "Reverse repo rate is the rate at which the central bank of a country (RBI in India) borrows money from commercial banks within the country."
    },
    {
        "keywords": ["what is crr", "cash reserve ratio", "crr meaning"],
        "answer": "CRR is a specified minimum fraction of the total deposits of customers, which commercial banks have to hold as reserves either in cash or as deposits with the central bank."
    },
    {
        "keywords": ["what is slr", "statutory liquidity ratio", "slr meaning"],
        "answer": "SLR is the minimum percentage of deposits that a commercial bank has to maintain in the form of liquid cash, gold, or other securities."
    },
    {
        "keywords": ["what is fdi", "foreign direct investment", "fdi meaning"],
        "answer": "FDI is an investment made by a firm or individual in one country into business interests located in another country."
    },
    {
        "keywords": ["what is fii", "foreign institutional investor", "fii meaning"],
        "answer": "FIIs are investors or investment funds registered in a country outside of the one in which they are investing. They play a significant role in the Indian stock market."
    },
    {
        "keywords": ["what is dii", "domestic institutional investor", "dii meaning"],
        "answer": "DIIs are institutional investors like mutual funds, insurance companies, and banks that invest in the financial assets of the country they are based in."
    },
    {
        "keywords": ["what is nse", "nse meaning"],
        "answer": "NSE (National Stock Exchange) is the leading stock exchange of India, located in Mumbai."
    },
    {
        "keywords": ["what is bse", "bse meaning"],
        "answer": "BSE (Bombay Stock Exchange) is the oldest stock exchange in Asia, located in Mumbai, India."
    },
    {
        "keywords": ["what is mcx", "mcx meaning"],
        "answer": "MCX (Multi Commodity Exchange) is India's largest commodity derivatives exchange."
    },
    {
        "keywords": ["what is sebi registered", "sebi registered"],
        "answer": "SEBI registered means that the entity (broker, advisor, etc.) is registered with the Securities and Exchange Board of India and is authorized to conduct business in the securities market."
    },
    {
        "keywords": ["what is kyc", "kyc meaning"],
        "answer": "KYC (Know Your Customer) is a mandatory process of identifying and verifying the identity of the client when opening an account and periodically over time."
    },
    {
        "keywords": ["what is pan card", "pan card"],
        "answer": "PAN (Permanent Account Number) is a ten-character alphanumeric identifier, issued in the form of a laminated 'PAN card', by the Indian Income Tax Department. It is mandatory for financial transactions."
    },
    {
        "keywords": ["what is aadhar", "aadhar card"],
        "answer": "Aadhaar is a 12-digit unique identity number that can be obtained voluntarily by residents or passport holders of India, based on their biometric and demographic data."
    },
    {
        "keywords": ["what is gst", "gst meaning"],
        "answer": "GST (Goods and Services Tax) is a value-added tax levied on most goods and services sold for domestic consumption."
    },
    {
        "keywords": ["what is ltcg", "long term capital gains", "ltcg"],
        "answer": "LTCG tax is a tax levied on the profits made from the sale of assets held for a long period (usually more than 1 year for stocks)."
    },
    {
        "keywords": ["what is stcg", "short term capital gains", "stcg"],
        "answer": "STCG tax is a tax levied on the profits made from the sale of assets held for a short period (usually less than 1 year for stocks)."
    },
    {
        "keywords": ["what is swing trading", "swing trading"],
        "answer": "Swing trading is a style of trading that attempts to capture gains in a stock (or any financial instrument) over a period of a few days to several weeks."
    },
    {
        "keywords": ["what is scalping", "scalping"],
        "answer": "Scalping is a trading strategy that attempts to make many small profits on small price changes throughout the day."
    },
    {
        "keywords": ["what is algo trading", "algorithmic trading", "algo trading"],
        "answer": "Algorithmic trading is a method of executing orders using automated pre-programmed trading instructions accounting for variables such as time, price, and volume."
    },
    {
        "keywords": ["what is hft", "high frequency trading", "hft"],
        "answer": "High-frequency trading (HFT) is a type of algorithmic trading characterized by high speeds, high turnover rates, and high order-to-trade ratios that leverages high-frequency financial data and electronic trading tools."
    },
    {
        "keywords": ["what is dark pool", "dark pool"],
        "answer": "A dark pool is a private financial forum or exchange for trading securities. Dark pools allow investors to trade without exposure until after the trade has been executed and reported."
    },
    {
        "keywords": ["what is block deal", "block deal"],
        "answer": "A block deal is a single transaction between two parties of a minimum quantity of 5,00,000 shares or a minimum value of Rs. 5 crore."
    },
    {
        "keywords": ["what is bulk deal", "bulk deal"],
        "answer": "A bulk deal is a deal where the total quantity of shares bought or sold is more than 0.5% of the share capital of the company."
    },
    {
        "keywords": ["what is circuit breaker", "circuit breaker"],
        "answer": "A circuit breaker is a regulatory measure to temporarily halt trading on an exchange to curb panic selling or excessive volatility."
    },
    {
        "keywords": ["what is pre-open session", "pre-open"],
        "answer": "The pre-open session is a 15-minute duration (9:00 AM to 9:15 AM) before the regular trading session starts, used to determine the opening price of stocks."
    },
    {
        "keywords": ["what is post-closing session", "post-closing"],
        "answer": "The post-closing session (3:40 PM to 4:00 PM) allows investors to buy or sell stocks at the closing price determined during the regular session."
    },
    {
        "keywords": ["what is muhurat trading", "muhurat trading"],
        "answer": "Muhurat Trading is a special one-hour trading session held on Diwali evening, considered auspicious for investing."
    },
    # Beginner Questions
    {
        "keywords": ["which stock to buy for beginner", "beginner stock", "stock for beginner"],
        "answer": "As a beginner, you should look for large-cap companies with stable earnings, strong fundamentals, and consistent performance."
    },
    {
        "keywords": ["safest stock to buy", "safe stock", "safest type of stock"],
        "answer": "Large-cap, fundamentally strong stocks are generally considered safer due to stable business models."
    },
    {
        "keywords": ["buy high or low price stock", "stock price matter", "high vs low price stock"],
        "answer": "Stock price alone does not matter; focus on company fundamentals and valuation metrics."
    },
    {
        "keywords": ["good stock for long term", "long term investment stock", "best long term stock"],
        "answer": "Stocks with consistent revenue growth, low debt, and strong management are suitable for long-term investment."
    },
    {
        "keywords": ["good stock for short term", "short term trading stock", "best short term stock"],
        "answer": "Short-term traders usually focus on high-volume stocks with strong price momentum and trends."
    },

    # Fundamental Analysis
    {
        "keywords": ["how to know if stock is worth buying", "is stock worth buying", "check stock worth"],
        "answer": "Check financial ratios like P/E, ROE, Debt-to-Equity, and revenue growth."
    },
    {
        "keywords": ["buy stock with low pe", "low pe ratio good", "is low pe good"],
        "answer": "A low P/E may indicate undervaluation, but it should be compared with industry averages."
    },
    {
        "keywords": ["is high roe good", "high roe meaning", "buy high roe stock"],
        "answer": "Yes, high ROE generally indicates efficient use of shareholder capital."
    },
    {
        "keywords": ["avoid high debt stocks", "high debt stock bad", "should i buy high debt stock"],
        "answer": "High debt can increase risk, especially during market downturns."
    },
    {
        "keywords": ["is profit growth important", "profit growth importance", "consistent profit growth"],
        "answer": "Yes, consistent profit growth shows business sustainability."
    },

    # Market & Trend
    {
        "keywords": ["buy stocks when market is falling", "buy in falling market", "market correction buy"],
        "answer": "Market corrections can offer opportunities, but stock selection should be based on fundamentals."
    },
    {
        "keywords": ["how trends help in buying", "stock trends importance", "follow trends"],
        "answer": "Trends indicate market sentiment and potential price direction."
    },
    {
        "keywords": ["buy stock near 52 week low", "52 week low buy", "is 52 week low good"],
        "answer": "Only if fundamentals are strong and the fall is not due to serious business issues."
    },
    {
        "keywords": ["buy stock near 52 week high", "52 week high buy", "is 52 week high good"],
        "answer": "Stocks at highs may still perform well if growth momentum is strong."
    },
    {
        "keywords": ["is volume important", "volume importance", "high trading volume"],
        "answer": "Yes, high trading volume confirms strong investor interest."
    },

    # Sector & Category
    {
        "keywords": ["which sector to buy", "best sector to invest", "sector selection"],
        "answer": "Choose sectors showing strong growth, demand, and long-term potential."
    },
    {
        "keywords": ["buy stocks from same sector", "same sector stocks", "sector concentration"],
        "answer": "Diversification across sectors helps reduce risk."
    },
    {
        "keywords": ["invest in trending sectors", "trending sector investment", "chase trending sectors"],
        "answer": "Trending sectors can offer opportunities but may also be volatile."
    },
    {
        "keywords": ["are it stocks good", "it sector investment", "invest in it stocks"],
        "answer": "IT stocks are often suitable for long-term growth due to global demand."
    },
    {
        "keywords": ["should i buy psu stocks", "psu stock investment", "invest in psu"],
        "answer": "PSU stocks can offer value but depend on government policies and financial health."
    },

    # Risk & Strategy
    {
        "keywords": ["how much risk to take", "risk tolerance", "stock market risk"],
        "answer": "Risk should match your financial goals, time horizon, and risk tolerance."
    },
    {
        "keywords": ["should i buy penny stocks", "penny stock investment", "are penny stocks good"],
        "answer": "Penny stocks are high-risk and not recommended for beginners."
    },
    {
        "keywords": ["is diversification important", "importance of diversification", "why diversify"],
        "answer": "Yes, diversification reduces the impact of losses from a single stock."
    },
    {
        "keywords": ["buy regularly or all at once", "lump sum vs sip", "regular investing"],
        "answer": "Regular investing helps average out market volatility."
    },
    {
        "keywords": ["how many stocks in portfolio", "ideal portfolio size", "number of stocks to own"],
        "answer": "A balanced portfolio usually contains 10–15 diversified stocks."
    },

    # AI & Platform (Stoxly.ai)
    {
        "keywords": ["how stoxly helps", "stoxly features", "stoxly analysis"],
        "answer": "Stoxly.ai analyzes financial data, trends, and ratios to generate insights."
    },
    {
        "keywords": ["does stoxly recommend stocks", "stoxly recommendations", "stoxly tips"],
        "answer": "No, it provides research-based insights, not direct recommendations."
    },
    {
        "keywords": ["can ai help in stock selection", "ai in trading", "ai stock picking"],
        "answer": "AI helps by analyzing large data sets and identifying patterns."
    },
    {
        "keywords": ["filters to find good stocks", "stock filters", "best stock filters"],
        "answer": "Use filters like Market Cap, P/E ratio, ROE, and Profit Growth."
    },
    {
        "keywords": ["compare multiple stocks", "stock comparison", "compare stocks"],
        "answer": "Yes, stock comparison helps evaluate better investment options."
    },

    # Practical Decision Making
    {
        "keywords": ["good fundamentals poor chart", "fundamentals vs technicals", "chart vs fundamentals"],
        "answer": "Long-term investors prioritize fundamentals, while traders focus on charts."
    },
    {
        "keywords": ["buy during market news", "trading on news", "market news impact"],
        "answer": "Market news increases volatility; careful analysis is required."
    },
    {
        "keywords": ["avoid bad stocks", "identify bad stocks", "what stocks to avoid"],
        "answer": "Avoid companies with weak earnings, high debt, and poor governance."
    },
    {
        "keywords": ["is past performance important", "past performance vs future", "historical performance"],
        "answer": "Past performance helps, but future growth potential is more important."
    },
    {
        "keywords": ["buy social media recommended stocks", "social media tips", "stock tips"],
        "answer": "Always verify data before investing; social media tips can be risky."
    },

    # Portfolio & Watchlist
    {
        "keywords": ["add to watchlist before buying", "watchlist importance", "why use watchlist"],
        "answer": "Yes, tracking stocks helps make better-timed decisions."
    },
    {
        "keywords": ["how watchlist helps", "watchlist benefits", "using watchlist"],
        "answer": "It allows monitoring price movement and fundamentals over time."
    },
    {
        "keywords": ["review stocks regularly", "portfolio review", "monitor stocks"],
        "answer": "Yes, regular review helps manage risk and performance."
    },
    {
        "keywords": ["when to sell stock", "selling strategy", "exit strategy"],
        "answer": "Sell if fundamentals deteriorate or goals are achieved."
    },
    {
        "keywords": ["reinvest profits", "compounding profits", "reinvesting"],
        "answer": "Reinvesting profits can help compound returns."
    },

    # Advanced Understanding
    {
        "keywords": ["market cap effect", "large vs mid vs small cap", "market cap importance"],
        "answer": "Large-cap stocks are stable, mid-cap offer growth, small-cap are high-risk."
    },
    {
        "keywords": ["growth vs value stocks", "growth or value", "value vs growth"],
        "answer": "Choice depends on investment goals and risk tolerance."
    },
    {
        "keywords": ["can ai predict stock price", "ai price prediction", "stock prediction"],
        "answer": "AI can analyze trends but cannot guarantee predictions."
    },
    {
        "keywords": ["timing the market", "market timing", "time the market"],
        "answer": "Long-term investing focuses more on quality than timing."
    },
    {
        "keywords": ["buy dividend stocks", "dividend investing", "dividend stocks good"],
        "answer": "Dividend stocks are suitable for stable income-focused investors."
    },

    # Final User Intent
    {
        "keywords": ["which stock to buy today", "buy stock today", "todays best stock"],
        "answer": "Stoxly.ai provides analysis to help you decide, not direct advice."
    },
    {
        "keywords": ["choose stocks based on goals", "goal based investing", "investing goals"],
        "answer": "Define goals like growth, income, or stability and apply suitable filters."
    },
    {
        "keywords": ["beginners start with index", "index funds for beginners", "index investing"],
        "answer": "Index stocks are generally safer and less volatile."
    },
    {
        "keywords": ["is stock buying risky", "stock market risk", "investing risk"],
        "answer": "Yes, all stock investments carry market risk."
    },
    {
        "keywords": ["smartest way to choose stocks", "smart investing", "how to pick stocks"],
        "answer": "Use data-driven analysis, diversification, and long-term planning."
    }
]
