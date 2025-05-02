#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as Form
from forms import *
import sys
import datetime
from sqlalchemy import func

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

app.config.from_object('config')
db = SQLAlchemy()
migrate = Migrate()

db.init_app(app)
migrate.init_app(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String, nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='venue', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String, nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='artist', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

    shows = db.relationship('Show', backref='artist', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} Artist: {self.artist_id} Venue: {self.venue_id} Time: {self.start_time}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = None
  if isinstance(value, datetime.datetime):
      date = value
  elif isinstance(value, str):
      try:
          date = dateutil.parser.parse(value)
      except (ValueError, TypeError):
          return ''
  else:
      return ''

  if date:
      try:
          if format == 'full':
              format_string ="EEEE MMMM, d, y 'at' h:mma"
          elif format == 'medium':
              format_string ="EE MM, dd, y h:mma"
          else:
              format_string = format 
          return babel.dates.format_datetime(date, format_string, locale='en')
      except Exception as e:
          return str(date)
  else:
      return '' 

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  current_time = datetime.datetime.now()
  error = False
  try: 
    distinct_venues = db.session.query(Venue.city, Venue.state).distinct().order_by(Venue.state, Venue.city).all()

    for venue in distinct_venues:
      city, state = venue
      venues_in_city = Venue.query.filter_by(city=city, state=state).order_by(Venue.name).all()

      venue_list = []
      for venue in venues_in_city:
        upcoming_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time > current_time).count()
        venue_list.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": upcoming_shows
        })

      data.append({
        "city": city,
        "state": state,
        "venues": venue_list
      })

  except Exception as e:
    error = True
    print(f"Error occurred while fetching venues: {e}")

  if error:
    return render_template('pages/venues.html', venues=[])
  else:
    return render_template('pages/venues.html', areas=data)
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '').strip()
  current_time = datetime.datetime.now()
  response = {"count": 0, "data": []}
  error = False
  
  try:
    results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).order_by(Venue.name).all()
    response["count"] = len(results)

    for venue in results:
      num_upcoming_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time > current_time).count()

      response["data"].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      })

  except Exception as e:
    error = True
    print(f"Error occurred while searching venues: {e}")

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  current_time = datetime.datetime.now()
  past_shows_data = []
  upcoming_shows_data = []
  data = {} 
  error = False

  try:
    shows_query = Show.query.filter_by(venue_id=venue_id).order_by(Show.start_time).all()

    for show in shows_query:
        if show.artist:
            artist_details = {
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": format_datetime(show.start_time) 
            }
            if show.start_time <= current_time:
                past_shows_data.append(artist_details)
            else:
                upcoming_shows_data.append(artist_details)
        else:
            print(f"Warning: Show ID {show.id} for Venue {venue_id} is missing related Artist.")

    
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.split(',') if venue.genres else [],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows_data,
        "upcoming_shows": upcoming_shows_data,
        "past_shows_count": len(past_shows_data),
        "upcoming_shows_count": len(upcoming_shows_data),
    }

  except Exception as e:
    error = True
    db.session.rollback()
    print(f"Error occurred while fetching venue details: {e}")

  finally:
    db.session.close()

  if error:
     return redirect(url_for('index'))
  else:
     return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  error = False

  if form.validate_on_submit():
      try:
          new_venue = Venue(
              name=form.name.data.strip(),
              city=form.city.data.strip(),
              state=form.state.data,
              address=form.address.data.strip(),
              phone=form.phone.data,
              genres=','.join(form.genres.data),
              image_link=form.image_link.data,
              facebook_link=form.facebook_link.data,
              website_link=form.website_link.data,
              seeking_talent=form.seeking_talent.data,
              seeking_description=form.seeking_description.data
          )
          db.session.add(new_venue)
          db.session.commit()
          flash('Venue ' + new_venue.name + ' was successfully listed!', 'success')
      except Exception as e:
          error = True
          db.session.rollback()
          print(e)
          flash('An error occurred. Venue ' + form.name.data + ' could not be listed.', 'danger')
      finally:
          db.session.close()
  else:
      error = True

  if error:
      return render_template('forms/new_venue.html', form=form)
  else:
      return redirect(url_for('index'))

@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  error = False
  venue_name = ""
  try:
      venue = db.session.get(Venue, venue_id)
      if venue:
          venue_name = venue.name
          db.session.delete(venue)
          db.session.commit()
          flash('Venue ' + venue_name + ' was successfully deleted!', 'success')
      else:
          error = True
          flash(f'Venue with ID {venue_id} not found.', 'warning')

  except Exception as e:
      error = True
      db.session.rollback()
      print(e)
  finally:
      db.session.close()

  return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  error = False
  try:
    artists = Artist.query.order_by(Artist.name).all()
    for artist in artists:
      data.append({
        "id": artist.id,
        "name": artist.name,
      })
  except Exception as e:
    error = True
    print(f"Error occurred while fetching artists: {e}")

  if error:
    return render_template('pages/artists.html', artists=[])
  else:
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '').strip()
  current_time = datetime.datetime.now()
  response = {"count": 0, "data": []}
  error = False

  try:
    results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).order_by(Artist.name).all()
    response["count"] = len(results)

    for artist in results:
      num_upcoming_shows = Show.query.filter(Show.artist_id == artist.id, Show.start_time > current_time).count()

      response["data"].append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": num_upcoming_shows
      })
  except Exception as e:
    error = True
    print(f"Error occurred while searching artists: {e}")

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  current_time = datetime.datetime.now()
  past_shows_data = []
  upcoming_shows_data = []
  data = {}
  error = False

  try:
      shows_query = Show.query.filter_by(artist_id=artist_id).order_by(Show.start_time).all()

      for show in shows_query:
          if show.venue: 
              venue_details = {
                  "venue_id": show.venue.id,
                  "venue_name": show.venue.name,
                  "venue_image_link": show.venue.image_link,
                  "start_time": format_datetime(show.start_time) 
              }
              if show.start_time <= current_time:
                  past_shows_data.append(venue_details)
              else:
                  upcoming_shows_data.append(venue_details)
          else:
              print(f"Warning: Show ID {show.id} for Artist {artist_id} is missing related Venue.")


      
      data = {
          "id": artist.id,
          "name": artist.name,
          "genres": artist.genres.split(','),
          "city": artist.city,
          "state": artist.state,
          "phone": artist.phone,
          "website": artist.website_link,
          "facebook_link": artist.facebook_link,
          "seeking_venue": artist.seeking_venue,
          "seeking_description": artist.seeking_description,
          "image_link": artist.image_link,
          "past_shows": past_shows_data,
          "upcoming_shows": upcoming_shows_data,
          "past_shows_count": len(past_shows_data),
          "upcoming_shows_count": len(upcoming_shows_data),
      }

  except Exception as e:
      error = True
      db.session.rollback()
      print(f"Error fetching artist details for ID {artist_id}: {e}")
  finally:
      db.session.close()

  if error:
      return redirect(('index'))
  else:
      return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  form.genres.data = artist.genres.split(',')
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(request.form)
  error = False

  if form.validate_on_submit():
    try:
      artist.name = form.name.data.strip()
      artist.city = form.city.data.strip()
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = ','.join(form.genres.data)
      artist.image_link = form.image_link.data
      artist.facebook_link = form.facebook_link.data
      artist.website_link = form.website_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data

      db.session.commit()
      flash('Artist ' + form.name.data + ' was successfully updated!', 'success')
      return redirect(url_for('show_artist', artist_id=artist_id))
    except Exception as e:
      error = True 
      db.session.rollback()
      print(f"Error occurred while updating artist: {e}")
    finally:
      db.session.close()
  else:
      error = True

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  form.genres.data = venue.genres.split(',')  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(request.form)
  error = False 

  if form.validate_on_submit():
    try:
      venue.name = form.name.data.strip()
      venue.city = form.city.data.strip()
      venue.state = form.state.data
      venue.address = form.address.data.strip()
      venue.phone = form.phone.data
      venue.genres = ','.join(form.genres.data)
      venue.image_link = form.image_link.data
      venue.facebook_link = form.facebook_link.data
      venue.website_link = form.website_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data

      db.session.commit()
      flash('Venue ' + form.name.data + ' was successfully updated!', 'success')
      return redirect(url_for('show_venue', venue_id=venue_id))

    except Exception as e:
      error = True
      db.session.rollback()
      print(f"Error occurred while updating venue: {e}")
    finally:
      db.session.close()
  else:
      error = True

  return render_template('forms/edit_venue.html', form=form, venue=venue)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  error = False

  if form.validate_on_submit():
      try:
          new_artist = Artist(
              name=form.name.data.strip(),
              city=form.city.data.strip(),
              state=form.state.data,
              phone=form.phone.data,
              genres=','.join(form.genres.data),
              image_link=form.image_link.data,
              facebook_link=form.facebook_link.data,
              website_link=form.website_link.data,
              seeking_venue=form.seeking_venue.data, 
              seeking_description=form.seeking_description.data
          )
          db.session.add(new_artist)
          db.session.commit()
          flash('Artist ' + new_artist.name + ' was successfully listed!', 'success')
      except Exception as e:
          error = True
          db.session.rollback()
          print(e)
      finally:
          db.session.close()
  else:
      error = True

  if error:
      return render_template('forms/new_artist.html', form=form)
  else:
      return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  error = False
  try:
      shows_list = Show.query.order_by(Show.start_time.desc()).all()

      for show in shows_list:
          if show.venue and show.artist:
              data.append({
                  "venue_id": show.venue.id,
                  "venue_name": show.venue.name,
                  "artist_id": show.artist.id,
                  "artist_name": show.artist.name,
                  "artist_image_link": show.artist.image_link,
                  "start_time": format_datetime(show.start_time) 
              })
          else:
              print(f"Warning: Show ID {show.id} is missing related Venue or Artist.")

  except Exception as e:
      error = True
      db.session.rollback()
      print(f"Error querying shows: {e}")
  finally:
      db.session.close()

  if error:
      return render_template('pages/shows.html', shows=[])
  else:
      return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  error = False

  if form.validate_on_submit():
      try:
          artist = db.session.get(Artist, form.artist_id.data) 
          venue = db.session.get(Venue, form.venue_id.data) 

          if not artist or not venue:
              error = True
          else:
              new_show = Show(
                  artist_id=form.artist_id.data,
                  venue_id=form.venue_id.data,
                  start_time=form.start_time.data
              )
              db.session.add(new_show)
              db.session.commit()
              flash('Show was successfully listed!', 'success')

      except Exception as e:
          error = True
          db.session.rollback()
          print(e)
      finally:
          db.session.close()
  else:
      error = True

  if error:
      return render_template('forms/new_show.html', form=form)
  else:
      return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
