# BraveBot Project

## Overview
BraveBot is an AI-powered Telegram bot designed to analyze trends, suggest pricing, and provide insights for various products. It integrates with multiple APIs and offers a dashboard for monitoring and managing its functionalities.

## Features
- **AI Engine**: Analyzes trends and suggests pricing based on viral scores.
- **Telegram Bot**: Interacts with users, handling commands and messages.
- **Dashboard**: Provides a user-friendly interface for monitoring the bot's status and functionalities.
- **Configurable**: Easily adjustable settings through configuration files.

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/bravebot.git
   cd bravebot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env` and fill in the required values.

## Usage
To start the BraveBot application, run:
```
python main.py
```

You can interact with the bot on Telegram by sending commands such as `/start`.

## Configuration
Configuration settings can be found in the `config` directory:
- `ai_config.json`: Settings for the AI engine.
- `settings.json`: Additional application settings.

## Logging
Logs are stored in the `logs` directory. Ensure to check this directory for any runtime errors or information.

## Testing
To run the tests, execute:
```
pytest tests/
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.