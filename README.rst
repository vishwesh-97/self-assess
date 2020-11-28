Self Assessment BE
==================

* repository contains code for Self Assessment backend.
* repository contains 2 different branches develop and master.

Environment Setup
-----------------
* Creating virtual environment from terminal

::

    virtualenv -p python3 envname

* Activating virtual environment using terminal

::

    cd <env dir>
    source bin/activate

* Deactivating virtual environment using terminal

::

    deactivate

Installing requirements
-----------------------
* To install the project requirement run the following command in terminal

1. Activate virtual environment using above given steps.

2. Go to requirements.txt file directory in project and run below command using terminal.

::

    pip install -r requirements.txt


Creating database
-------------------

* create a new database and a user in Postgres. Grant privileges to the user for the created database.


::

    psql
    CREATE DATABASE dbname;


Setting and migrating database
------------------------------
* Update Database credentials in settings.py file in project.

* Migrate database using given command in terminal

::

    python manage.py migrate


Creating super user
-------------------
* After migrating database, to create a super user by running command given below

::

    python manage.py createsuperuser


To run django server in local
------------------------------

::

    python manage.py runserver


How to setup Questions for the tool
-----------------------------------
* After creating super user, Login to django admin panel

* After successful login, click on "AssessmentQuestion" in the left panel.

* To add new Question, click "add/create" and provide required details.