# RE-Immo

## Project Description
RE-Immo is a tool designed to analyze the carbon risk of your property based on CRREM models. It features an easy-to-use interface for adding buildings and relevant data on emissions and retrofitting activities. This project aims to provide property owners and managers with insights into their buildings' sustainability performance and areas for improvement.

## Features
- **Building Data Input**: Easily add and manage information about buildings and retrofitting activities.
- **Carbon Risk Analysis**: Calculate the carbon risk based on current emissions and potential future scenarios.
- **User Management**: Secure user authentication and management.
- **Localization**: Multi-language support through Flask-Babel.

## Installation Instructions
To set up and run the project locally, follow these steps:

1. Clone the project repository:
``` git clone https://github.com/lululululu5/re-immo ```

2. Navigate to the project directory:

``` cd re-immo ```

3. Setup a virtual python environment

``` python -m venv venv ```

4. Activate the virtual environment
- On MacOs/Linux: 
``` source venv/bin/activate ```

5. Install the required dependencies

``` pip install -r requirements.txt ```

6. Initilaize the database: 

``` flask db init
flask db migrate
flask db upgrade ```

7. Run the Flask application

``` flask run ```


## Technologies Used
- **Python Flask**: Web framework for the application.
- **SQLAlchemy (with SQLite)**: ORM for database management.
- **Flask-Babel**: For multi-language support.
- **Jinja and WTForms**: For templating and form handling.
- **Flask-Login**: User authentication and session management.
- **Flask-Mail**: For sending emails.
- **Unittest**: For testing the application.

## Project Structure
The project uses an app factory pattern for easy configuration and testing. The configuration options are set in the `config.py` file, allowing for different setups. It's a multi-page application, with separate HTML files containing Jinja templates rendered from specific routes.

Data for emission calculations is stored in JSON files for easy accessibility, with basic building information stored in the database. The core calculations are handled by a `BuildingCalculation` class, ensuring efficient computation of all relevant metrics.

There are three main models:
- **User**: Handles user-related data and authentication.
- **Building**: Stores basic building information.
- **Settings**: Configuration options and user preferences.

## License
This project is licensed under the MIT License

## Future Plans
- **Deployment**: Deploy the application to a production environment.
- **Storage Architecture**: Improve performance by transitioning from JSON files to a database.
- **Data Insertion Process**: Streamline the process of adding new data.
- **Stranding Periods**: Implement stranding periods instead of events for better timeline tracking.
- **Sustainability Recommendations**: Provide more comprehensive recommendations for improving sustainability performance.
- **Portfolio View**: Allow for multiple properties per account to be more valuable for real estate investors. This would require a larger rewrite of the logic with respect to database constraints, and routing logic.


