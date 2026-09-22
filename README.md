# 📈 NIFTY 50 Short Straddle Trading Bot

An automated **NIFTY 50 short-straddle trading system** built in Python using the **Upstox API**.

The system retrieves the NIFTY 50 options contract data, establishes a live WebSocket connection for option prices, identifies suitable Call (CE) and Put (PE) contracts based on premium requirements, places SELL orders through the Upstox order API, maintains a local order log, and monitors open positions for stop-loss-based exits.

> ⚠️ **Important:** This project is intended for educational, research, and algorithm-development purposes. Automated trading involves financial risk. Use appropriate testing, risk controls, API permissions, and regulatory compliance before deploying with real capital.

---

# 🚀 What This Project Does

The bot follows a continuous automated trading cycle:

```text
        NIFTY 50 Options
               │
               ▼
      Fetch Option Contracts
               │
               ▼
        Save Option Chain
               │
               ▼
       Start WebSocket
               │
               ▼
       Receive Live LTPs
               │
        ┌──────┴──────┐
        ▼             ▼
    Find CE         Find PE
        │             │
        ▼             ▼
   Premium Check   Premium Check
        │             │
        └──────┬──────┘
               ▼
         SELL Positions
               │
               ▼
        Store Order Log
               │
               ▼
       Monitor Live LTP
               │
               ▼
        Stop-Loss Check
               │
               ▼
        BUY to Exit
```

---

# ✨ Main Features

### 📊 Market Data

* Retrieves NIFTY 50 option contracts using the Upstox API.
* Saves the complete option-chain response locally.
* Extracts:

  * Strike price
  * Expiry
  * Exchange token
  * Trading symbol
  * Instrument type
* Subscribes to option contracts through Upstox Market Data WebSocket.

### ⚡ Live Price Streaming

The bot uses:

```python
upstox_client.MarketDataStreamerV3
```

to receive live option prices.

The latest LTP for each subscribed instrument is stored in:

```python
self.ltp_data
```

The structure is conceptually:

```text
Instrument Token → Latest LTP
```

For example:

```text
NSE_FO|123456 → 54.80
NSE_FO|123457 → 55.25
```

---

# 🏗️ Project Architecture

The main trading engine is implemented through:

```python
class NIFTY_STRADDLE:
```

The class maintains:

* Access token
* WebSocket streamer
* Live LTP data
* WebSocket connection status
* Order-log management
* Option-chain management
* CE entry logic
* PE entry logic
* Exit logic

---

# 📁 Local Files

The bot uses two important JSON files.

## `nifty_revised_options_chain.json`

Stores the option-contract response obtained from Upstox.

Example structure:

```json
{
    "data": [
        {
            "name": "NIFTY",
            "expiry": "2026-06-02",
            "exchange_token": "123456",
            "trading_symbol": "NIFTY26JUN25000CE",
            "strike_price": 25000,
            "instrument_type": "CE"
        }
    ]
}
```

---

## `nifty_order_log.json`

Stores the bot's locally maintained order history.

Example:

```json
[
    {
        "quantity": 195,
        "product": "D",
        "validity": "DAY",
        "instrument_token": "NSE_FO|123456",
        "order_type": "MARKET",
        "transaction_type": "SELL",
        "ltp": 55.2,
        "trade_token": "123456",
        "trade_symbol": "NIFTY26JUN25000CE",
        "trade_strikeprice": 25000,
        "trade_expiry": "2026-06-02",
        "entry_price": 55.2,
        "status": "OPEN",
        "instrument_type": "CE"
    }
]
```

The `status` field is used to track whether a position is:

```text
OPEN
CLOSED
```

---

# 🔐 Authentication

The bot uses an Upstox access token.

The token is assigned to:

```python
self.access_token
```

The token is then sent through the HTTP authorization header:

```text
Authorization: Bearer <ACCESS_TOKEN>
```

The same access token is used for:

* Option-contract API requests
* WebSocket authentication
* Order placement

### ⚠️ Security

Never commit a real access token to GitHub.

Instead of:

```python
self.access_token = 'REAL_TOKEN'
```

use an environment variable or another secure secret-management method.

---

# 📡 Option Contract Retrieval

The bot requests NIFTY 50 option contracts through the Upstox API.

The relevant endpoint is:

```text
https://api.upstox.com/v2/option/contract
```

The request specifies:

```text
instrument_key = NSE_INDEX|Nifty 50
expiry_date = selected expiry
```

The response is then saved locally as:

```text
nifty_revised_options_chain.json
```

This file becomes the local source for selecting CE and PE contracts.

---

# 🔌 WebSocket Architecture

After loading the option-chain data, the bot extracts every option's exchange token.

Conceptually:

```text
Option Chain
     │
     ▼
Exchange Tokens
     │
     ▼
NSE_FO|TOKEN
     │
     ▼
Upstox WebSocket
     │
     ▼
Live LTP
```

The tokens are subscribed using:

```python
self.streamer.subscribe(tokens, "full")
```

The WebSocket receives market-data messages continuously.

The bot extracts the LTP from:

```text
fullFeed
    ↓
marketFF
    ↓
ltpc
    ↓
ltp / cp
```

The latest value is stored in:

```python
self.ltp_data[token] = ltp
```

---

# 💰 NIFTY Short-Straddle Strategy

The strategy attempts to sell both:

```text
CALL OPTION  → CE
PUT OPTION   → PE
```

This creates a short straddle structure.

Conceptually:

```text
             NIFTY
               │
       ┌───────┴───────┐
       │               │
      CE              PE
       │               │
      SELL            SELL
       │               │
       └───────┬───────┘
               │
          Short Straddle
```

---

# ⏰ Entry Timing

The bot checks:

```python
position_time = '09:25'
```

and compares it with the current system time.

The entry logic therefore becomes active once:

```text
Current Time >= 09:25
```

---

# 🎯 Premium Selection

The bot uses:

```python
required_ltp = 55
```

as the target premium level.

For contracts with LTP between:

```text
₹55
```

and

```text
< ₹56
```

the bot can immediately select the contract.

For premiums above ₹55, the bot also maintains a collection of candidate contracts and selects the minimum qualifying premium.

Conceptually:

```text
Option Chain
     │
     ▼
Check CE / PE
     │
     ▼
LTP available?
     │
     ▼
Premium >= ₹55
     │
     ▼
Select qualifying contract
     │
     ▼
SELL
```

---

# 📦 Position Quantity

The current implementation uses:

```python
quantity = 195
```

for the order.

The code also contains:

```python
lots = 3
```

and:

```python
lots = 5
```

in different sections.

The actual order quantity sent to the Upstox API is determined by the `quantity` field in `new_order`.

Therefore, the effective quantity should always be verified against the configured NIFTY lot size and the intended number of lots.

---

# 📤 Order Placement

Orders are placed using the Upstox HFT order endpoint:

```text
https://api-hft.upstox.com/v3/order/place
```

The order is constructed as a market SELL order.

Important fields include:

```text
transaction_type → SELL
order_type       → MARKET
product          → D
validity         → DAY
quantity         → 195
```

The instrument token is formatted as:

```text
NSE_FO|<exchange_token>
```

---

# 🧾 Order Logging

After attempting an order, the bot creates an order-history record containing information such as:

* Quantity
* Product
* Order type
* Transaction type
* Instrument token
* LTP
* Trading symbol
* Strike price
* Expiry
* Entry price
* Instrument type
* Status

The record is appended to:

```text
nifty_order_log.json
```

This allows the bot to maintain local state between iterations.

---

# 🛡️ Duplicate Position Protection

Before opening a CE position, the bot checks the existing order log.

If an existing CE position is found:

```text
CE → return
```

Similarly, before opening a PE position:

```text
PE → return
```

This prevents the same instrument type from being repeatedly opened during the continuous loop.

The intended structure is:

```text
             Order Log
                 │
        ┌────────┴────────┐
        ▼                 ▼
       CE?               PE?
        │                 │
       YES               YES
        │                 │
      Don't             Don't
      enter             enter
```

---

# 🛑 Stop-Loss Logic

The exit system uses:

```python
stop_loss_level = 1.25
```

The stop-loss is calculated as:

```text
Stop Loss = Entry Price × 1.25
```

For example, if:

```text
Entry Price = ₹55
```

then:

```text
Stop Loss = ₹55 × 1.25
          = ₹68.75
```

Since the strategy is selling the option, an increase in option premium represents an adverse price movement.

Therefore:

```text
Entry = ₹55
        │
        ▼
Premium rises
        │
        ▼
₹68.75
        │
        ▼
BUY to exit
```

---

# 🔄 Exit Process

For every order in the order log, the bot checks:

```text
Instrument Type
Status
Entry Price
Quantity
Current LTP
```

If:

```text
status == OPEN
```

and:

```text
current LTP >= stop-loss
```

the bot creates a BUY market order.

The position is then marked:

```text
status = CLOSED
```

and the updated order log is written back to:

```text
nifty_order_log.json
```

---

# 🔁 Main Trading Loop

Once the WebSocket has started, the bot enters a continuous loop:

```text
             START
               │
               ▼
        WebSocket Connected
               │
               ▼
        Check Connection
               │
               ▼
        CE Entry Check
               │
               ▼
        PE Entry Check
               │
               ▼
        Exit Check
               │
               ▼
            Sleep
               │
               ▼
          Repeat ♻️
```

The current loop waits:

```python
time.sleep(1)
```

between iterations.

Therefore, the strategy continuously checks the trading conditions approximately every second.

---

# 🔌 WebSocket Reconnection

The bot monitors:

```python
self.websocket_connected
```

If the WebSocket disconnects, the system attempts to reconnect.

The flow is:

```text
WebSocket disconnected
        │
        ▼
Disconnect existing streamer
        │
        ▼
Start WebSocket again
        │
        ▼
Subscribe to tokens
        │
        ▼
Continue trading loop
```

This provides basic connection-recovery behavior.

---

# 🧠 Core Components

| Component                        | Responsibility                    |
| -------------------------------- | --------------------------------- |
| `ensure_order_log()`             | Creates order-log file if missing |
| `saving_the_order_log()`         | Saves order data                  |
| `opening_the_order_log()`        | Reads existing orders             |
| `getting_the_options_contract()` | Retrieves option contracts        |
| `openinig_the_data()`            | Loads option-chain JSON           |
| `start_websocket()`              | Starts live market-data stream    |
| `get_ltp()`                      | Retrieves latest LTP              |
| `taking_a_call_position()`       | Handles CE entry                  |
| `taking_a_put_position()`        | Handles PE entry                  |
| `exiting_the_trades()`           | Handles stop-loss exits           |

---

# 🗂️ Data Flow

The complete data flow is:

```text
                    Upstox
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
    Option Contract API       Market Data WebSocket
          │                         │
          ▼                         ▼
 options_chain.json             Live LTP
          │                         │
          └────────────┬────────────┘
                       ▼
                Strategy Logic
                       │
              ┌────────┴────────┐
              ▼                 ▼
          CE Position       PE Position
              │                 │
              └────────┬────────┘
                       ▼
                Order Placement
                       │
                       ▼
              nifty_order_log.json
                       │
                       ▼
                 Exit Monitor
                       │
                       ▼
                  Stop Loss
                       │
                       ▼
                  BUY Exit
```

---

# 🛠️ Technologies Used

### 🐍 Python

Main programming language.

### 📡 Requests

Used for HTTP communication with the Upstox REST API.

### 🐼 Pandas

Imported for data processing and future analysis.

### 📄 JSON

Used for:

* Option-chain storage
* Order-log storage
* Reading persisted trading state

### ⏱️ Datetime

Used for entry-time checks.

### ⏳ Time

Used for loop delays and WebSocket startup waiting.

### 💻 OS

Used for checking whether the order-log file exists.

### 📈 Upstox Python SDK

Used for:

* Market Data WebSocket
* Live option-price streaming

---

# 📦 Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd <project-folder>
```

Install the required packages:

```bash
pip install requests pandas upstox-python-sdk
```

Depending on the installed Upstox SDK package/version, the exact package name may differ.

---

# 🔑 Configuration

Before running the bot, configure your Upstox access token:

```python
self.access_token = 'YOUR_ACCESS_TOKEN'
```

For real deployment, it is strongly recommended to load credentials from environment variables instead of hard-coding them.

---

# ▶️ Running the Bot

Run:

```bash
python nifty_straddle.py
```

The program will:

1. Create the order-log file if necessary.
2. Retrieve the NIFTY option contracts.
3. Save the option-chain response.
4. Load the contracts.
5. Subscribe to their live market data.
6. Wait for live LTP data.
7. Check CE entry conditions.
8. Check PE entry conditions.
9. Monitor open positions.
10. Execute stop-loss exits.
11. Continue running continuously.

---

# 📊 Example Strategy Flow

Suppose the bot finds:

```text
CE Premium = ₹55.20
PE Premium = ₹54.70
```

The CE satisfies the configured premium requirement.

The bot can create a SELL order for the qualifying CE contract.

The same process is performed independently for the PE side.

Once both positions are established:

```text
CE → SELL
PE → SELL
```

the bot continuously monitors their LTPs.

If a position reaches its calculated stop-loss:

```text
Entry = ₹55
SL    = ₹68.75
```

the bot sends:

```text
BUY → MARKET
```

to close that position.

---

# ⚠️ Important Trading Considerations

This project interacts directly with a live trading API. Before using it with real capital, several areas should be carefully tested.

### 🔐 API Security

Never publish:

* Access tokens
* API secrets
* Authentication credentials

in a public repository.

### 📏 Quantity Validation

Always verify the configured quantity against the current exchange lot size and your intended number of lots.

### 🌐 Internet Connectivity

The strategy depends on continuous WebSocket connectivity for live LTP data.

### 📡 Data Validation

The bot should verify that a valid LTP exists before using it for trading decisions.

### 🧾 Order Confirmation

A local order log does not by itself guarantee that an exchange order was successfully executed. Production systems should reconcile local state with actual broker order status.

### 🛑 Risk Management

The current stop-loss logic is based on the option's premium reaching:

```text
Entry × 1.25
```

Additional risk controls may be required for production use.

---

# 🔮 Future Improvements

Possible improvements include:

### 📊 Better Position Management

* Track actual broker order IDs
* Fetch order status from Upstox
* Track filled quantity
* Track actual average fill price
* Handle partial fills

### 🛡️ Risk Management

* Daily maximum loss
* Maximum number of trades
* Maximum position size
* Emergency square-off
* Broker-side stop-loss orders
* Connection-failure protection

### 🗄️ Database

Replace JSON-based persistence with:

```text
SQLite
PostgreSQL
Redis
```

for more reliable state management.

### 📈 Monitoring

Add:

* Telegram alerts
* Trade notifications
* Entry notifications
* Exit notifications
* WebSocket status alerts
* Daily P&L reporting

### 🧪 Testing

Add:

* Backtesting
* Paper trading
* Historical replay
* Unit tests
* Mock Upstox API responses

### ⚙️ Configuration

Move strategy parameters into a configuration file:

```text
ENTRY_TIME
REQUIRED_PREMIUM
STOP_LOSS_MULTIPLIER
QUANTITY
EXPIRY
```

This would make strategy changes easier without modifying the main code.

---

# 🧩 Project Structure

A cleaner repository structure could eventually look like:

```text
nifty-straddle/
│
├── nifty_straddle.py
│
├── nifty_revised_options_chain.json
├── nifty_order_log.json
│
├── requirements.txt
├── README.md
│
└── .gitignore
```

The JSON files should generally be excluded from Git if they contain live/private trading information.

---

# 📜 Disclaimer

This software is provided for educational and research purposes.

It is an automated trading system capable of interacting with a broker API. Financial markets involve significant risk, and automated execution can result in losses due to market movements, latency, connectivity problems, incorrect data, API failures, rejected orders, partial fills, or software errors.

The author does not guarantee profitability or uninterrupted operation.

Always test thoroughly in a non-production environment before considering live deployment.

---

# 👨‍💻 Author

Built as a Python-based algorithmic trading and market-data engineering project.

### 🐍 Python

### 📡 Upstox API

### ⚡ WebSocket Market Data

### 📊 NIFTY 50 Options

### 🤖 Automated Execution

**From live market data → strategy logic → automated execution → risk-based exit.** 🚀
# 📥 Clone the Project

To get a local copy of this project, first make sure **Git** is installed on your system.

### 1️⃣ Clone the Repository

Open your terminal or command prompt and run:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
```

Replace:

```text
YOUR-USERNAME
```

with your GitHub username and:

```text
YOUR-REPOSITORY
```

with the name of this repository.

For example:

```bash
git clone https://github.com/username/nifty-straddle.git
```

### 2️⃣ Move Into the Project Directory

```bash
cd nifty-straddle
```

### 3️⃣ Create a Virtual Environment

It is recommended to create a virtual environment for the project:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 4️⃣ Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

If a `requirements.txt` file is not provided, install the required packages manually:

```bash
pip install requests pandas upstox-python-sdk
```

### 5️⃣ Configure Your Upstox Access Token 🔐

Before running the bot, configure your Upstox access token.

The token is required for:

* 📡 Live market-data WebSocket
* 📊 Option-contract API
* 📤 Order placement

**Do not use someone else's access token.**

For development, configure your own valid Upstox API credentials.

### 6️⃣ Run the Project ▶️

Once the dependencies and credentials are configured:

```bash
python nifty_straddle.py
```

The bot will then:

```text
Clone Repository
       ↓
Install Dependencies
       ↓
Configure Upstox Token
       ↓
Run Python Script
       ↓
Fetch NIFTY Option Contracts
       ↓
Start WebSocket
       ↓
Receive Live LTP
       ↓
Execute Strategy
```

### ⚠️ Important

This project can interact with a live broker API and place orders.

Before running it with real money, make sure you understand the strategy and have configured the required API credentials correctly.

Never commit your:

```text
Access Token
API Secret
Private Credentials
Live Order Logs
```

to a public GitHub repository.
