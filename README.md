# Price Tracker Bot

An LLM-powered generic price tracker that can keep tabs on products from any random website (I can’t guarantee it. You bet on the LLM, bro).

## How to Run

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/price-tracker-bot.git
   cd price-tracker-bot
   ```

2. **Set Up Environment Variables:**
   Copy `.env.example` to `.env` and fill in your API keys (you know the drill):
   ```bash
   cp .env.example .env
   ```

3. **Build the Docker Image:**
   ```bash
   docker build -t price-tracker-bot .
   ```

4. **Run the Bot:**
   ```bash
   docker run price-tracker-bot
   ```

## Where?

Host it yourself. I host mine. Good luck!
