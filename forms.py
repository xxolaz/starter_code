from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, AnyOf, URL, Regexp, Optional, Length

genre_choices = [
        ('Alternative', 'Alternative'),
        ('Blues', 'Blues'),
        ('Classical', 'Classical'),
        ('Country', 'Country'),
        ('Electronic', 'Electronic'),
        ('Folk', 'Folk'),
        ('Funk', 'Funk'),
        ('Hip-Hop', 'Hip-Hop'),
        ('Heavy Metal', 'Heavy Metal'),
        ('Instrumental', 'Instrumental'),
        ('Jazz', 'Jazz'),
        ('Musical Theatre', 'Musical Theatre'),
        ('Pop', 'Pop'),
        ('Punk', 'Punk'),
        ('R&B', 'R&B'),
        ('Reggae', 'Reggae'),
        ('Rock n Roll', 'Rock n Roll'),
        ('Soul', 'Soul'),
        ('Other', 'Other'),
]

state_choices = [
        ('AL', 'AL'),
        ('AK', 'AK'),
        ('AZ', 'AZ'),
        ('AR', 'AR'),
        ('CA', 'CA'),
        ('CO', 'CO'),
        ('CT', 'CT'),
        ('DE', 'DE'),
        ('DC', 'DC'),
        ('FL', 'FL'),
        ('GA', 'GA'),
        ('HI', 'HI'),
        ('ID', 'ID'),
        ('IL', 'IL'),
        ('IN', 'IN'),
        ('IA', 'IA'),
        ('KS', 'KS'),
        ('KY', 'KY'),
        ('LA', 'LA'),
        ('ME', 'ME'),
        ('MT', 'MT'),
        ('NE', 'NE'),
        ('NV', 'NV'),
        ('NH', 'NH'),
        ('NJ', 'NJ'),
        ('NM', 'NM'),
        ('NY', 'NY'),
        ('NC', 'NC'),
        ('ND', 'ND'),
        ('OH', 'OH'),
        ('OK', 'OK'),
        ('OR', 'OR'),
        ('MD', 'MD'),
        ('MA', 'MA'),
        ('MI', 'MI'),
        ('MN', 'MN'),
        ('MS', 'MS'),
        ('MO', 'MO'),
        ('PA', 'PA'),
        ('RI', 'RI'),
        ('SC', 'SC'),
        ('SD', 'SD'),
        ('TN', 'TN'),
        ('TX', 'TX'),
        ('UT', 'UT'),
        ('VT', 'VT'),
        ('VA', 'VA'),
        ('WA', 'WA'),
        ('WV', 'WV'),
        ('WI', 'WI'),
        ('WY', 'WY'),
    ]

phone_regex = r'^\(?([0-9]{3})\)?[-.●\s]?([0-9]{3})[-.●\s]?([0-9]{4})$' #Fancy Phone Number Regex
phone_error_message = 'Invalid phone number format. Use xxx-xxx-xxxx or similar.'

class ShowForm(Form):
    artist_id = StringField(
        'artist_id',
        validators=[DataRequired(message='Artist ID is required')]
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired(message='Venue ID is required')]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired(message='Start time is required')],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name',
        validators=[DataRequired(message='Name is required')]
    )
    city = StringField(
        'city',
        validators=[DataRequired(message='City is required')]
    )
    state = SelectField(
        'state',
        validators=[DataRequired(message='State is required'), AnyOf([choice[0] for choice in state_choices], message="Invalid state selected.")],
        choices=state_choices
    )
    address = StringField(
        'address',
        validators=[DataRequired(message="Address is required.")]
    )
    phone = StringField(
        'phone',
        validators=[Optional(), Regexp(phone_regex, message=phone_error_message)]
    )
    genres = SelectMultipleField(
        'genres',
        validators=[DataRequired(message="At least one genre must be selected.")],
        choices=genre_choices
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[Optional(), URL(message="Invalid Facebook URL provided.")]
    )
    website_link = StringField(
        'website_link',
        validators=[Optional(), URL(message="Invalid Website URL provided.")]
    )
    image_link = StringField(
        'image_link',
        validators=[Optional(), URL(message="Invalid Image URL provided.")]
    )
    seeking_talent = BooleanField(
        'seeking_talent',
        default=False
    )
    seeking_description = StringField(
        'seeking_description',
        validators=[Optional(), Length(max=500)]
    )



class ArtistForm(Form):
    name = StringField(
        'name',
        validators=[DataRequired(message="Artist name is required.")]
    )
    city = StringField(
        'city',
        validators=[DataRequired(message="City is required.")]
    )
    state = SelectField(
        'state',
        validators=[DataRequired(message="State is required."), AnyOf([choice[0] for choice in state_choices], message="Invalid state selected.")],
        choices=state_choices
    )
    phone = StringField(
        'phone',
        validators=[Optional(), Regexp(phone_regex, message=phone_error_message)]
    )
    genres = SelectMultipleField(
        'genres',
        validators=[DataRequired(message="At least one genre must be selected.")],
        choices=genre_choices
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[Optional(), URL(message="Invalid Facebook URL provided.")]
    )
    image_link = StringField(
        'image_link',
        validators=[Optional(), URL(message="Invalid Image URL provided.")]
    )
    website_link = StringField(
        'website_link',
        validators=[Optional(), URL(message="Invalid Website URL provided.")]
    )
    seeking_venue = BooleanField(
        'seeking_venue',
        default=False
    )
    seeking_description = StringField(
        'seeking_description',
        validators=[Optional(), Length(max=500)]
    )