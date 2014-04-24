iCongress
=========
In a world filled with misinformation, talking heads and inflated egos, it can be hard to tell what is a fact and what is not. iCongress allows you to vote on real legislation that has been brought up in the US Congress (whether or not the bill died before becoming a law). We take your votes and develop a compatibility score for every Member of Congress, so you can see who <i>actually</i> votes with you on the issues that really do matter. Sign up and start now!

# What is this?
A Flask web app that allows users to see how their voting would match up with real members of Congress!

# Setting up the SQLite Database
Open up a terminal and navigate to the iCongress base directory:
```python
python
>>> from main import db
>>> db.create_all()
```

# Useful Development Tools
* [SQLite-Manager (Firefox Add-On)](https://code.google.com/p/sqlite-manager/)

# Dependencies
* [Flask](http://flask.pocoo.org/)
* Flask Extensions - more found [here](http://flask.pocoo.org/extensions/)
  * [Flask-Login](https://flask-login.readthedocs.org/en/latest/)
  * [Flask-BrowserID (Mozilla Persona)](https://github.com/garbados/flask-browserid)
  * [Flask-SQLAlchemy](http://pythonhosted.org/Flask-SQLAlchemy/)
  * [Flask-Gravatar](http://pythonhosted.org/Flask-Gravatar/)
  * [Flask-SQLAlchemy](http://pythonhosted.org/Flask-SQLAlchemy/)
In order to install all of these dependancies run this:

```bash
pip install Flask
pip install flask-login
pip install git+https://github.com/garbados/flask-browserid.git
pip install Flask-Gravatar
```