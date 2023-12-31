﻿# **Scholar Stream - Online Learning Platform**

Scholar Stream is an innovative online learning platform built with Django. It provides an interactive and streamlined learning experience, bringing high-quality educational content right to your fingertips.

**Table of Contents**

- [Getting Started]
- [Prerequisites]
- [Installation]
- [Usage]
- [Database Loading]
- [Environment Variables]

**Getting Started**

These instructions will help you get a copy of the project up and running on your local machine for development and testing purposes.

**Prerequisites**

Ensure you have the following software installed on your system:

- Python 3.8 or later
- Django 3.2 or later
- pip (Python package manager)

**Installation**

1. Clone the repository

git clone https://github.com/akshaykumar19002/scholarstream.git

2. Navigate to the project directory

cd scholar-stream

3. Create a virtual environment

python3 -m venv env

4. Activate the virtual environment

On Linux or Mac, use `source env/bin/activate`
On Windows, use `.\env\Scripts\activate`

5. Install the required packages

pip install -r requirements.txt

6. Make migrations to the database

python manage.py makemigrations

7. Apply the migrations

python manage.py migrate

8. Load data into the database

python manage.py loaddata db.json

9. Run the Django development server

python manage.py runserver

You should now be able to access the application at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

**Database Loading**

To load data from the `db.json` file into your database, ensure that you have run the `migrate` command, and then run the following command:

python manage.py loaddata db.json

**Environment Variables**

For this project to run properly, you will need to create a `.env` file in the project root directory and fill in your required environment variables. Refer to the `.env.example` file in the project directory to see an example of how to set this up. Remember to add your actual data where necessary.

After updating the `.env` file, remember to restart your server so the changes can take effect.
