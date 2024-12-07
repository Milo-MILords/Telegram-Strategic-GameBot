# Telegram Game Bot

This is a Telegram bot designed to manage resources, upgrade buildings, and handle various game functionalities in a group-based game.

## Features

- **Resource Management**: Manage resources such as money, stones, wood, iron, gold, food, and more.
- **Building Upgrades**: Upgrade various buildings and factories to increase resource production.
- **Weekly Updates**: Collect weekly outputs from factories and buildings.
- **Treaty Management**: Create, send, and confirm treaties between players.
- **Private Messaging**: Send private messages to groups.
- **Attack Handling**: Manage and record details of attacks between players.
- **Admin Controls**: Admins can change asset values and perform weekly updates.

## Getting Started

### Prerequisites

- Python 3.6 or higher
- A Telegram bot token from [BotFather](https://core.telegram.org/bots#botfather)
- SQLite3

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/telegram-game-bot.git
    cd telegram-game-bot
    ```

2. Install the required Python packages:
    ```bash
    pip install pyTelegramBotAPI
    ```

3. Set up your bot token and admin details in the code:
    ```python
    API_TOKEN = 'YOUR_TELEGRAM_BOT_API_TOKEN'
    ADMIN_ID = YOUR_ADMIN_ID
    CHANNEL_ID = "@your_channel_id"
    ```

4. Initialize the database:
    ```bash
    sqlite3 game_bot.db < schema.sql
    ```

5. Run the bot:
    ```bash
    python main.py
    ```

### Usage

- **/setlord**: Register yourself as a lord in the group.
- **/start**: Start interacting with the bot and access the menu options.

#### Menu Options

- **💰 دارایی**: View your assets and resources.
- **🛠️ ارتقا**: Upgrade buildings and factories.
- **🙌 بیانیه**: Send a statement to the channel.
- **✉️ پیام خصوصی**: Send a private message to a group.
- **📜 معاهده**: Manage treaties.
- **⚔️ لشکرکشی**: Manage and record attack details.
- **🔨 آپ هفتگی**: Collect weekly outputs (admin only).
- **🛠️ تنظیم دارایی**: Change asset values (admin only).

### Contributing

Feel free to submit issues or pull requests. For major changes, please open an issue first to discuss what you would like to change.

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.

### Acknowledgements

- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)

## Contact

For any questions or feedback, please contact https://t.me/AnonymousPython .
