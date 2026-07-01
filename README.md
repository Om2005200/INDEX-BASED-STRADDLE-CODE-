# INDEX-BASED-STRADDLE-CODE-
An automated NIFTY Short Straddle trading system featuring live option chain analysis, real-time WebSocket market data, automated order execution, stop-loss management, and trade lifecycle automation.
# Automated NIFTY Short Straddle Trading Engine

A modular algorithmic trading engine that automates the execution and management of a **premium-based NIFTY Short Straddle** strategy using live market data. The project demonstrates the complete trade lifecycle—from option chain processing and strike selection to automated execution, live position monitoring, and risk management.

---

## Overview

This trading engine is designed to automate a daily NIFTY Short Straddle strategy by continuously processing live option prices and executing trades without manual intervention.

The current implementation integrates with the **Upstox API**, while the architecture is intentionally modular, allowing additional brokers to be integrated with minimal changes to the strategy layer.

---

## Strategy Workflow

Every trading day the engine performs the following sequence:

1. Downloads the latest NIFTY option contracts.
2. Establishes a live WebSocket connection.
3. Continuously tracks option premiums in real time.
4. Selects the Call (CE) and Put (PE) contracts trading closest to **₹55.5 premium**.
5. Simultaneously places SELL orders to create the Short Straddle.
6. Continuously monitors every open position.
7. Automatically exits positions once predefined stop-loss conditions are triggered.
8. Squares off any remaining open positions at **3:15 PM**.

---

## Key Features

* Real-time option chain processing
* Live WebSocket market data streaming
* Premium-based strike selection
* Automated Short Straddle execution
* Dynamic stop-loss monitoring
* Automatic end-of-day square-off
* Persistent trade logging
* Automatic WebSocket reconnection
* Modular broker integration architecture

---

## System Architecture

```text
                    Market Data
                         │
                         ▼
              Option Contract Manager
                         │
                         ▼
               Strike Selection Engine
                         │
                         ▼
                 Order Execution Layer
                         │
                         ▼
                Position Management
                         │
                         ▼
                Risk Management Engine
                         │
                         ▼
                   Trade Logger
```

---

---

## Design Philosophy

The project focuses on building a reusable trading engine rather than a broker-specific script.

The trading strategy remains independent from the execution layer, making it straightforward to integrate additional brokers such as Zerodha Kite, Angel One SmartAPI, Shoonya, or Fyers by replacing only the broker interface.

---

## Current Capabilities

* Automated NIFTY Short Straddle execution
* Live premium monitoring
* Automated strike selection
* Live position tracking
* Stop-loss based exits
* End-of-day position management
* Persistent trade history

---


---

## Disclaimer

This repository is intended for educational and research purposes. Algorithmic trading involves significant financial risk. Thorough testing should always be performed before deploying any strategy in a live trading environment.
