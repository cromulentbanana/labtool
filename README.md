This code is still development-grade and not yet fit for public-facing deployment.

## The Labtool has the following components:
* labfront (web interface, Django/Python application)
* Frontend (views, HTML/JS)
* Backend (models and logic)
* REST API (interface for frontend and labcli)
* labcli (console interface on cheetah talking to the API, standalone Python application)

## The following commands will set up a python virtualenv in the $PWD with all the dependencies required to run labtool:
Some of this is borrowed from here: http://www.jeffknupp.com/blog/2012/02/09/starting-a-django-project-the-right-way/

 cd $DEVDIR
 virtualenv labtoolix-env
 source labtoolix-env/bin/activate
 pip install -r labtoolIX/requirements.txt
For LDAP make sure you have the development headers installed for:

libldap-dev
python-dev
libsasl2-dev
libssl-dev
now that the virtualenv is setup, you can clone the labtoolix-dev repo:

 cd $DEVDIR
 git clone gitolite@projects.net.t-labs.tu-berlin.de:labtoolix/labtoolix-dev.git
Then to run the django app:

 cd $DEVDIR
 source labtoolix-env/bin/activate
 cd labtoolix-dev
 cd labtoolIX
 ./manage.py syncdb
 ./manage.py migrate
 #Optionally, import a database fixture consisting of sample devices, reservations, etc from the old labtool
 ./manage.py loaddata dump_06_devices_with_power_console_ethernetports_links.json
 ./manage.py runserver
Now you have a http server listening on 127.0.0.1:8000, steer your browser to that address

 pip install splinter # to support browser-automated acceptance tests
