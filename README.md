# Suburb Services

Suburb Services is a modern professional services platform where users and professionals can foster an environment of moderated and industry-grade professional work, ranging from house help to advanced technical assistance. It is my sophomore year project for Modern Application Development-1 at IIT Madras. Built entirely with Flask and Jinja2.

## Prerequisites

- Python (latest version)
- Flask
- SQLAlchemy

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/dotcomaki/household_services.git
    ```

2. Navigate to the project directory:

    ```bash
    cd household_services
    ```

3. Create a virtual environment and activate it:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4. Install required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Database Setup

1. Configure the database connection in your environment variables.

2. Initialize the database:

    ```bash
    python create_db.py
    ```

3. Seed the database:

    ```bash
    python seed.py
    ```

## Running the Application

1. Initialize Python Virtualenv

    ```py
    source venv/bin/activate
    ```

2. Start the Flask development server:

    ```bash
    flask run
    ```

Access the application at `http://localhost:5000`.
