#!/bin/bash

# set up a new virtualenv for the api
python3 -m venv flask

# upgrade the included pip
flask/bin/pip install --upgrade pip
# install wheel
flask/bin/pip install wheel
# install app requirements
flask/bin/pip install -r requirements.txt