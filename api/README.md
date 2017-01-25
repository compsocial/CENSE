# README #

Don't forget to setup virtual environment!

Install `virtualenv` using `pip`
```
#!bash

sudo pip install virtualenv
```


Then create a virtual environment
```
#!bash

virtualenv homophone_backend_environment
```

Then activate the virtual environment
```
#!bash

source homophone_backend_environment/bin/activate
```

The prompt will change, don't be alarmed. Once in the virtual environment, install uwsgi and flask using `pip`
```
#!bash
pip install uwsgi flask
```

Deactivate virtual environment with command
```
#!bash

deactivate
```

Refer to (https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-14-04)


Currently setup on flashmob00 port 8000

