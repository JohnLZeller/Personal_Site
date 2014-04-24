John Zeller's Website
=========
This repository serves as version control for my personal website. It goes through many iterations as I learn new techniques that I'd like to play around with. Feel free to fork and modify for your own sites, just please follow the GNU General Public License

# Setting up the SQLite Database
Open up a terminal and navigate to the project base directory:
```python
python
>>> from main import db
>>> db.create_all()
```

# To Do
* Pull in commit history
** Github
** Mozilla
** etc?
* Install Ghost
** Export Wordpress work blog to Ghost
* Personal Blog and work blog?

# Useful Development Tools
* [SQLite-Manager (Firefox Add-On)](https://code.google.com/p/sqlite-manager/)

# Dependencies
* [Flask](http://flask.pocoo.org/)
* Flask Extensions - more found [here](http://flask.pocoo.org/extensions/)
  * [Flask-SQLAlchemy](http://pythonhosted.org/Flask-SQLAlchemy/)
In order to install all of these dependancies run this:

```bash
pip install Flask
```