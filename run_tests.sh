#!/usr/bin/bash

coverage run --omit 'env/*','venv/*','tests/*' -m pytest -vs tests/ && coverage html