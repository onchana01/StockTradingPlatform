# StockTradingPlatform
# StockPlatform

StockPlatform is a robust, Dockerized Django application designed for stock trading enthusiasts and developers. It offers a modern web interface with advanced trading capabilities, including options trading, margin trading, and algorithmic trading, all styled with a clean, centered CSS design. Built with scalability and portability in mind, this project leverages Docker Compose for easy setup and PostgreSQL for reliable data persistence.

## Features

- **User Authentication**: Secure registration and login system for managing user accounts.
- **Portfolio Management**: Create, edit, and delete portfolios with image uploads for personalization.
- **Real-Time Market Data**: Integrates with the Alpha Vantage API to fetch up-to-date stock prices and historical data.
- **Advanced Trading**:
  - **Options Trading**: Support for call and put options with strike prices and expiration dates.
  - **Margin Trading**: Enable trading on borrowed funds with margin balance tracking.
  - **Algorithmic Trading**: Define and execute rule-based trading strategies (e.g., moving average crossovers).
- **Responsive Design**: Centered UI elements with a professional, consistent layout using custom CSS.
- **API Integration**: RESTful endpoints via Django REST Framework for programmatic access.
- **Testing Suite**: Comprehensive unit and integration tests to ensure reliability.

## Tech Stack

- **Backend**: Django 5.1.7, Python 3.12
- **Database**: PostgreSQL 15 (via Docker)
- **Frontend**: HTML, CSS (centered design), JavaScript (Chart.js for visualizations)
- **API**: Alpha Vantage for market data, Django REST Framework for endpoints
- **Containerization**: Docker and Docker Compose
- **Dependencies**: Managed via `requirements.txt` (e.g., `pandas`, `gunicorn`, `coverage`)

## Prerequisites

To run StockPlatform locally or contribute to its development, ensure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A free [Alpha Vantage API key](https://www.alphavantage.co/support/#api-key) (25 requests/day limit; premium recommended for heavy use)

## Installation

Follow these steps to set up and run StockPlatform on your local machine:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/StockPlatform.git
   cd StockPlatform

Configure Environment Variables:
Create a .env file in the root directory with your Alpha Vantage API key:
bash

echo "ALPHA_VANTAGE_API_KEY=your_api_key_here" > .env

Replace your_api_key_here with your actual key.

Build and Run with Docker Compose:
bash

docker-compose up --build

This builds the Django app and PostgreSQL services.

The app will be available at http://127.0.0.1:8000/.

Stop the services with Ctrl+C and clean up with docker-compose down.

Verify Setup:
Open http://127.0.0.1:8000/ in your browser to see the public dashboard or login page.

Register a user and explore features like portfolio creation and advanced trading.

Running Tests
StockPlatform includes a suite of unit and integration tests to ensure functionality. To run them:
bash

docker-compose run web python manage.py test stock_app

Tests cover models, forms, and views, including advanced trading features.

Project Structure

StockPlatform/
├── stock_app/              # Django app directory
│   ├── static/            # CSS and JS files (e.g., styles.css)
│   ├── templates/         # HTML templates with centered design
│   ├── tests/             # Unit and integration tests
│   ├── migrations/        # Database migrations
│   ├── models.py          # Data models (Stock, Portfolio, etc.)
│   ├── views.py           # Application logic
│   └── urls.py            # URL routing
├── StockPlatform/         # Django project settings
├── Dockerfile             # Docker configuration for the app
├── docker-compose.yml     # Multi-container setup with PostgreSQL
├── requirements.txt       # Python dependencies
├── media/                 # Uploaded files (e.g., portfolio images)
└── README.md              # Project documentation

Contributing
Contributions are welcome! To contribute:
Fork the repository.

Create a feature branch (git checkout -b feature/your-feature).

Commit your changes (git commit -m "Add your feature").

Push to your fork (git push origin feature/your-feature).

Open a Pull Request.

Please ensure tests pass and follow Python/Django coding standards.
Notes
API Key: The free Alpha Vantage key has a 25-request/day limit. For production or heavy testing, consider a premium plan.

Database: Uses PostgreSQL by default. SQLite can be configured by modifying settings.py and Dockerfile.

Static Files: Located in stock_app/static/ and collected to staticfiles/ during the Docker build.

Media: User-uploaded files (e.g., portfolio images) are stored in media/ and mounted via Docker volumes.

License
This project is open-source and available under the MIT License (LICENSE). Feel free to use, modify, and distribute it as needed.
Contact
For questions or feedback, open an issue on GitHub or reach out to Onchana.

Happy trading with StockPlatform!

