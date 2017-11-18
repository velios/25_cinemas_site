# Cinemas Site

### How to Install

Python 3 should be already installed. Then use pip (or pip3 if there is a conflict with old Python 2 setup) to install dependencies:

```bash
pip install -r requirements.txt # alternatively try pip3
```

### How to use
##### Sample run
```bash
$ python3 server.py -d
* Restarting with stat
* Debugger is active!
* Debugger PIN: 146-845-781
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
##### Link to Heroku server
This project also exist on [heroku PaaS platform](https://www.heroku.com/)

Visit https://obscure-refuge-89039.herokuapp.com/ to see application in work

### API
Also available [API](https://obscure-refuge-89039.herokuapp.com/api) 
* `/api/movies` - return json response with info about movie from main page
* `/api/movies/:result_amount/cinemas/:cinemas_amount` - same json but you can filter it
    * `:result_amount` - amount of result items
    * `:cinemas_amount` - min cinemas threshold 

# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)
