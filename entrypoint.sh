#!/usr/bin/env bash

./manage.py migrate

exec ./manage.py runserver 0.0.0.0:8000
