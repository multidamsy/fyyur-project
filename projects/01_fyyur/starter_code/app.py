#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils.log import error
from email.policy import default
import json
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for, 
  jsonify
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  # to fix date format error for shows
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
      date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # To query for the page title of  venue city and state
  areas = db.session.query(Venue.city, Venue.state)
  data=[]
  for area in areas:
    venue_list =  Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []
    for venue in venue_list:
      venue_data.append({
        'id': venue.id,
        'name': venue.name
      })
      
      upcoming_shows = (
        (db.session.query(Show).filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).all())
      )
  # To add all the query results to the page
      data.append({
        'city': area.city,
        'state': area.state,
        'venues': venue_data,
        'num_upcoming_shows': len(upcoming_shows)
      })
  
  return render_template('pages/venues.html', areas=data);
    
@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []
  for result in results:
        data.append({
          'id': result.id,
          'name': result.name,
        })
  response = {
    'count': len(results),
    'data': results
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue= Venue.query.get(venue_id)

  # To query all upcoming shows
  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  
  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()

  # All data to be added to individual venue pages
  data = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website_link,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'upcoming_shows': upcoming_shows_query,
    'upcoming_shows_count': len(upcoming_shows_query),
    'past_shows': past_shows_query,
    'past_shows_count': len(past_shows_query)
  }

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
    try:
      venue = Venue()
      form.populate_obj(venue)
     
      db.session.add(venue)      
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except ValueError as e:
      print(e)
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
    return render_template('pages/home.html')

  # on successful db insert, flash success
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>/delete')
def delete_venue(venue_id):
    error= False
    venue_to_delete = Venue.query.get(venue_id)
    try:
      db.session.delete(venue_to_delete)
      db.session.commit()
      flash('Venue has been deleted')
    except:
      error= True
      db.session.rollback()
      flash('Oops! There was an error deleting venue')
    finally:
      db.session.close()
    return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = db.session.query(Artist.id, Artist.name)
  data=[]
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []
  for result in results:
        data.append({
          'id': result.id,
          'name': result.name,
        })
  response = {
    'count': len(results),
    'data': results
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist= Artist.query.get(artist_id)
  # To query all upcoming shows
  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  
  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
  # All data to be added to individual venue pages
  data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website_link,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'upcoming_shows': upcoming_shows_query,
    'upcoming_shows_count': len(upcoming_shows_query),
    'past_shows': past_shows_query,
    'past_shows_count': len(past_shows_query)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # To fill form with values from database
  if artist:
        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.genres.data = artist.genres
        form.facebook_link.data = artist.facebook_link
        form.image_link.data = artist.image_link
        form.website_link.data = artist.website_link
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist_to_update = Artist.query.get(artist_id)
  if request.method == 'POST':
        artist_to_update.name = request.form['name']
        artist_to_update.city = request.form['city']
        artist_to_update.state = request.form['state']
        artist_to_update.phone = request.form['phone']
        artist_to_update.genres = request.form['genres']
        artist_to_update.facebook_link = request.form['facebook_link']
        artist_to_update.image_link = request.form['image_link']
        artist_to_update.website_link = request.form['website_link']
        artist_to_update.seeking_venue = True if 'seeking_venue' in request.form else False
        artist_to_update.seeking_description = request.form['seeking_description']
        try:
          db.session.commit()
          flash('Artist ' + request.form['name'] + ' updated successfully.')

        except:
          db.session.rollback()
          flash('Unable to update artist')
        finally:
          db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # To fill form with values from database
  if venue:
        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.address.data = venue.address
        form.phone.data = venue.phone
        form.genres.data = venue.genres
        form.facebook_link.data = venue.facebook_link
        form.image_link.data = venue.image_link
        form.website_link.data = venue.website_link
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description


  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue_to_update = Venue.query.get(venue_id)
  if request.method == 'POST':
        venue_to_update.name = request.form['name']
        venue_to_update.city = request.form['city']
        venue_to_update.state = request.form['state']
        venue_to_update.address = request.form['address']
        venue_to_update.phone = request.form['phone']
        venue_to_update.genres = request.form['genres']
        venue_to_update.facebook_link = request.form['facebook_link']
        venue_to_update.image_link = request.form['image_link']
        venue_to_update.website_link = request.form['website_link']
        venue_to_update.seeking_talent = True if 'seeking_talent' in request.form else False
        venue_to_update.seeking_description = request.form['seeking_description']
        try:
          db.session.commit()
          flash('Venue ' + request.form['name'] + ' updated successfully.')

        except:
          db.session.rollback()
          flash('Unable to update venue')
        finally:
          db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = VenueForm(request.form)
  try:
    artist = Artist()
    form.populate_obj(artist)
    db.session.add(artist)      
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

  # on successful db insert, flash success
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.all()
  data=[]
  for show in shows:
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  form = ShowForm(request.form)
  try:
    # new_show = Show(
    #   artist_id=request.form.get('artist_id'),
    #   venue_id=request.form.get('venue_id'),
    #   start_time=request.form.get('start_time'),
    # )
    show = Show()
    form.populate_obj(show)
    
    db.session.add(show)      
    db.session.commit()
    flash('Show was successfully listed!')
  except ValueError as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

  # on successful db insert, flash success
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

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
