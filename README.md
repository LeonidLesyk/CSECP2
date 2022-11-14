#The instructions given assume that you are on the linux lab machines
#Server Setup
##Database Setup
You should have access to the mariadb servers that the uni provide https://systems.wiki.cs.st-andrews.ac.uk/index.php/Linux_Host_service#MariaDB, 
If not set up a mariadb server on your machine https://mariadb.org/ or contact fixit to be given one
Login to your mariadb server
Create a database with whatever name you like
CREATE DATABASE <database_name>;
##Virtual Environment Setup
create a python virtual environment
-python -m venv <environment_name>
navigate into the activate file in the environment you just created <environment_name>/bin/activate
open it and add the following lines to the end of the activate file
-export dbname='<db_username>'
-export dbuser='<db_user>'
-export dbpassword='<db_password>'
-export dbhost='<db_host>'
-export djangosecretkey='<django_secret key>'
insert all the details of your database that you have created in place of the <>
for the djangosecretkey run the following command to obtain a key
-python -c "import secrets; print(secrets.token_urlsafe())"
copy that and put it into the file
now when ever you activate it will automatically export the system variables to be used by django for the database
activate the environment
-source <environment_name>/bin/activate
install the required modules (includes those required for the client)
-pip install django
-pip install pymysql
-pip install cryptography
-pip install requests
##Making the Database Migrations
navigate into the messagehost/ directory and run
-python manage.py makemigrations
-python manage.py migrate
##Running the Server
you can make your server accessible through an nginx proxy 
https://systems.wiki.cs.st-andrews.ac.uk/index.php/New_Linux_Web_Service#Creating_a_configuration_file
or you can host locally
be sure to use a port that you have access to
usually the number given by
-id -u
will give you a valid port number available for you to use
to run the server 
- python manage.py runserver <port_number>
access the url in a browser you should see a django debug page
##Running the client
whilst still using the python virtual environment you have created
navigate into the client directory (important that you are in exactly the client directory!)
run
-python client.py
this will print the usage
not that the server url will be local host if you are running locally 
e.g http://localhost:<port_number> 
or whatever your uni url is (no backslash at the end!)
try the following
-python client.py <server_url> register me
-python client.py <server_url> send 'my first message' me me
-python client.py <server_url> read me
this will register you, send a message to yourself and then read it
