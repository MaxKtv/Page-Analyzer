### Hexlet tests and linter status:
[![Actions Status](https://github.com/MaxKtv/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/MaxKtv/python-project-83/actions)
[![Actions Status](https://github.com/MaxKtv/python-project-83/actions/workflows/pyci.yml/badge.svg)](https://github.com/MaxKtv/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/c3b73db088733929feae/maintainability)](https://codeclimate.com/github/MaxKtv/python-project-83/maintainability)
***
## Demo: https://python-project-83-jlm0.onrender.com
***
# System Requirements:

#### 1. Python3
> [Python3 installation](https://www.python.org/downloads/ "Use python 3.10 or higher!")
#### 2. Pip
> [Pip installation](https://pip.pypa.io/en/stable/installation/ "Pip how to install Documentation")
#### 3. Poetry
> [Poetry installation](https://python-poetry.org/docs/ "Poetry how to install Documentation")
> ##### Linux, macOS, Windows (WSL) 
>
> `curl -sSL https://install.python-poetry.org | python3 -`
 
#### 4. PostgreSQL
> [PostgreSQL innstallation](https://skillbox.ru/media/ "Download PostgreSQL for your OS")
***
# Installation:

### First Way (pip)

to install use:

> `python3 -m pip install --user https://github.com/MaxKtv/python-project-83/archive/refs/heads/main.zip`


### Second Way (clone repo)

 to clone repository - in any directory/folder use:

>`git clone https://github.com/MaxKtv/python-project-83.git`
> 

### Create and set environment
#### create .env file in the root directory of the project with values:
>`SECRET_KEY=your_secret_key`
>
>`DATABASE_URL=postgresql:your_login_password_connection`
#### build
>`make build`
#### start your server!
>`make start`
