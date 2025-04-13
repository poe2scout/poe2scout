# [![](https://poe2scout.com/favicon.ico)](#) POE2 Scout

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

POE2 Scout is your ultimate market tool for Path of Exile 2, providing real-time item price checking. It aims to help players make informed trading decisions by leveraging the official Path of Exile Trade API and presenting the data in an accessible way.

## Project Overview

- **`frontend`**: Serves the React single-page application using Nginx.
  - Code: `frontend/vite-project/`
  - Nginx Config: `frontend/vite-project/nginx.conf`
- **`api`**: The backend API service that the frontend interacts with.
  - Code: `services/apiService/`
- **`item-sync-service`**: A background service responsible for periodically fetching the list of available items (Unique, Currency, etc.) from the POE API and storing their base information in the database.
  - Code: `services/itemSyncService/`
- **`price-fetch-service`**: A background service that periodically fetches the *prices* for items from the POE Trade API for active leagues and records them in the database. It includes logic to handle rate limits and potential POE maintenance windows.
  - Code: `services/priceFetchService/`
- **`db`**: The PostgreSQL database storing item information, prices, and potentially user/build data.
- **`https-portal`**: (Production profile only) Manages SSL certificates and acts as a reverse proxy for the frontend and API.

The application is containerised using Docker for production. For running locally we run the python modules and npm run dev manually. Docker is only used locally for streamlining the db initialisation.

## Api

POE2 Scout has an api which is used by the website. This api is completely open for others to use as well.

Please include a user-agent field with an email so I can contact you. If your usage is likely to be high (consistently several times a minute) get in touch with me and I can create specific endpoints that serve your tools needs the most efficiently.

Documentation can be found at [poe2scout.com/api/swagger](https://poe2scout.com/api/swagger)

## Contributing

Contributions are welcome! Please follow these general steps:

1. Fork the repository on github.
2. Clone your forked repository to your local machine.
3. Create a new branch (`git checkout -b feature/your-feature-name`).
4. Make your changes.
5. Commit your changes (`git commit -m 'Add some feature'`).
6. Push to the branch (`git push origin feature/your-feature-name`).
7. Open a Pull Request.

## Local Development Setup

These instructions will help you get a local development environment running.

**Prerequisites:**

- Git
- Docker & Docker Compose (Optional, simplifies database setup. You can run PostgreSQL natively instead.)
- Python 3.12.3 (Managed with `pyenv` is recommended)
- Node.js and npm (For the frontend)

**Steps:**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/poe2scout/poe2scout.git # Replace /poe2scout/ with your own username if you have forked the repo 
    cd poe2scout
    ```

2.  **Configure Environment Variables:**
    Copy `.env.example` to `.env`. For local development, the default values are likely sufficient.
    ```bash
    cp .env.example .env
    ```

3.  **Start the Database:**
    The easiest way is using Docker Compose:
    ```bash
    docker-compose up -d # Will only run db by default
    ```
    *(Alternatively, set up and run PostgreSQL natively and update `.env` accordingly.)*

4.  **Set up the Python Backend Environment:**
    Navigate to the project root if you aren't already there.
    ```bash
    # Install and set the correct Python version (if using pyenv)
    pyenv install 3.12.3
    pyenv local 3.12.3

    # Create and activate a virtual environment
    python -m venv .venv
    # On macOS/Linux:
    source .venv/bin/activate
    # On Windows:
    # .venv\Scripts\activate

    # Install dependencies
    pip install uv
    uv pip install -r services/requirements.txt
    ```

5.  **Initial Backend Data Population:**
    *   **Run Item Sync:** This service fetches item base data from the POE API. Run it once and wait for it to complete.
        ```bash
        python -m services.itemSyncService
        ```
    *   **Run Database Migration:** After the item sync is done, apply the necessary SQL script to set up initial league data. You'll need a PostgreSQL client (like `psql` or a GUI tool like pgadmin 4) connected to the database defined in your `.env` / `docker-compose.yml`.
        ```sql
        -- Example using psql, adjust connection details as needed:
        -- psql -h localhost -p 5432 -U your_db_user -d your_db_name -f db/migrations/PostItemSyncService.sql

        -- Content of db/migrations/PostItemSyncService.sql needs to be executed
        ```

6.  **Run the Backend API:**
    You can now run the main API service.
    *   **Recommended (with auto-reload):**
        ```bash
        uvicorn services.apiService.app:app --reload --port 5000
        ```
    *   **Alternative (no auto-reload):**
        ```bash
        python -m services.apiService.app
        ```

7.  **Set up and Run the Frontend:**
    ```bash
    cd frontend/vite-project
    npm install
    npm run dev
    ```

8.  **Access the Application:**
    *   Frontend: Open your browser to `http://localhost:5173`
    *   API Docs: Open your browser to `http://localhost:5000/swagger` 

## Running Optional Background Services

These services run periodically in the background in a production-like environment but can be run manually for testing.

*   **Price Fetch Service:** Fetches item *prices*. Be mindful of POE Trade API rate limits when running this manually alongside other API interactions.
    ```bash
    # Ensure your Python venv is active
    python -m services.priceFetchService
    ```
*   **Item Sync Service (Recurring):** If you need to re-run the item sync later (e.g., after a major POE update):
    ```bash
    # Ensure your Python venv is active
    python -m services.itemSyncService
    ```

## Community

- **Discord:** [https://discord.gg/EHXVdQCpBq](https://discord.gg/EHXVdQCpBq)


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 

## Disclaimer

POE2Scout is an independent project and is not affiliated with or endorsed by Grinding Gear Games.

