# Creation of project
# Download the project and go into mainfolder
### Step 1: Initial setup
```cmd
python -m venv venv
venv\Scripts\activate
```
### Step 2: Install Django and Dependencies
1\. Download ``` requirements.txt```
2\. Install it by the following command:
```cmd
pip install -r requirements.txt
```
###  Step 3: Create the database
*Create the database from `ipo_app\models.py`.*
```cmd
python manage.py makemigrations ipo_app
python manage.py migrate
```
###  Step 4: Fill the database
1\. In `ipo_app\management\commands\fetch_ipo_data.py` set the `years = []` according to your prefference. eg. `year=[2020,2025]` 

2\. Fetch the Upcoming ipo, IPOs from the past and create or update it in the database.
```cmd
python manage.py fetch_ipo_data
```
###  Step 5: Run devlopment server
```cmd
python manage.py runserver
```

