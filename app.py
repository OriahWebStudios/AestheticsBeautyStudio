from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TimeField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Optional
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from datetime import datetime, timedelta
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
import vonage
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
migrate = Migrate(app, db)
login_manager.login_view = 'login'


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.String(1000), nullable=True)

    def __repr__(self):
        return '<Appointment %r>' % self.id
    
class PromotionUpdates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    promotion = db.Column(db.String(1000), nullable=True)
    updates = db.Column(db.String(1000), nullable=True) 

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=True, nullable=False) 

def add_user_credentials():
    existing_user = Users.query.filter_by(username='hopemaluleka').first()
    if not existing_user:
        new_user = Users(
            username='hopemaluleka',
            password='Abs@admin'  
        )
        db.session.add(new_user)
        db.session.commit()
        print('Done')
    else:
        print('Already exists')

with app.app_context(): 
    db.create_all()
    add_user_credentials()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AppointmentForm(FlaskForm):
    name = StringField('Full Name *', validators=[DataRequired()])
    email = StringField('Email *', validators=[DataRequired()])
    phone = StringField('Phone *', validators=[DataRequired()])
    date = DateField('Select Prefered Date *', format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField('Select Prefered Time *', validators=[DataRequired()])
    service = SelectField('Select Service *', choices=[
        ('Plain Acrylic - Short - R200', 'Plain Acrylic - Short - R200'),
        ('Plain Acrylic - Medium - R250', 'Plain Acrylic - Medium - R250'),
        ('Plain Acrylic - Long - R300', 'Plain Acrylic - Medium - R300'),
        ('French Acrylic - Short - R280', 'French Acrylic - Short - R280'),
        ('French Acrylic - Medium - R300', 'French Acrylic - Medium - R300'),
        ('French Acrylic - Long - R350', 'French Acrylic - Long - R350'),
        ('Ombre Design - Short - R280', 'Ombre Design - Short - R280'),
        ('Ombre Design - Medium - R350', 'Ombre Desgin - Medium - R350'),
        ('Ombre Design - Long - R400', 'Ombre Design - Long - R400'),
        ('Chrome Design - Short - R330', 'Chrome Design - Short - R330'),
        ('Chrome Design - Medium - R350', 'Chrome Desgin - Medium - R350'),
        ('Chrome Design - Long - R400', 'Chrome Design - Long - R400'),
        ('Gel Toes and Hands - Gel Tip - R180', 'Gel Toes and Hands - Gel Tip - R180'),
        ('Gel Toes and Hands - Gel On Natural Nails - R150', 'Gel Toes and Hands - Gel On Natural Nails - R150'),
        ('Acrylic Toes - Plain Overlay - R150', 'Acrylic Toes - Plain Overlay - R150'),
        ('Acrylic Toes - Tips Overlay - R180', 'Acrylic Toes - Tips Overlay - R180'),
        ('Acrylic Toes - French Overlay - R200', 'Acrylic Toes - French Overlay - R200'),
        ('Acrylic Toes - Buff and Shine with Art - R150', 'Acrylic Toes - Buff and Shine with Art - R150'),
        ('Acrylic Toes - Buff and Shine Plain - R100', 'Acrylic Toes - Buff and Shine Plain - R100'),
        ('Acrylic Toes - Soak Off - R60', 'Acrylic Toes - Soak Off - R60'),
        ('Acrylic Toes - Art Per Nail - R10-20', 'Acrylic Toes - Art Per Nail - R10-20'),
        ('Make-Up - Natural Look - R350', 'Make-Up - Natural Look - R350'),
        ('Make-Up - Classic Glam - R450', 'Make-Up - Classic Glam - R450'),
        ('Make-Up - Full Glam - R550', 'Make-Up - Full Glam - R550'),
        ('Make-Up - Bridal Look - R750', 'Make-Up - Bridal Look - R750'),
        ('Make-Up - Bridesmaids - R450', 'Make-Up - Bridesmaides - R450'),
        ('Make-Up - Flower Girl - R200', 'Make-Up - Flower Girl - R200'),
        ('Lashes - Cat Eye - R250', 'Lashes - Cat Eye - R250'),
        ('Lashes - Medium Volume - R250', 'Lashes - Medium Volume - R250'),
        ('Lashes - Classic/Natural - R200', 'Lashes - Classic/Natural - R200'),
        ('Lashes - Mega Medium - R400', 'Lashes - Mega Medium - R400'),
        ('Lashes - Hybrid - R350', 'Lashes - Hybrid - R350'),
        ('Lashes - Individual Lashes - R350-400', 'Lashes - Individual Lashes - R350-400'),
        ('Lashes - Lash Cleaners - R80', 'Lashes - Lash Cleaners - R80'),
        ('Lashes - Lash Removal - R100', 'Lashes - Lash Removal - R100'),
        ('Lashes - Refill - R100/150', 'Lashes - Refill - R100/150'),
        ('Lashes - Brow Shaping - R40', 'Lashes - Brow Shaping - R40'),
        ('Lashes - Brow Tint - R100', 'Lashes - Brow Tint - R100'),
    ])
    notes = StringField('Additional Notes or Requests (Optional)')
    submit = SubmitField('Submit')

class EditAppointmentForm(FlaskForm):
    date = DateField('Date *', format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField('Time *', validators=[DataRequired()])
    submit = SubmitField('Reschedule')

class FilterForm(FlaskForm):
    name = StringField('Full Name *', validators=[Optional()])
    date = DateField('Date *', format='%Y-%m-%d', validators=[Optional()])
    time = TimeField('Time *', validators=[Optional()])
    service = SelectField('Select Service *', choices=[
        ('', 'All Services'),
        ('Plain Acrylic - Short - R200', 'Plain Acrylic - Short - R200'),
        ('Plain Acrylic - Medium - R250', 'Plain Acrylic - Medium - R250'),
        ('Plain Acrylic - Long - R300', 'Plain Acrylic - Medium - R300'),
        ('French Acrylic - Short - R280', 'French Acrylic - Short - R280'),
        ('French Acrylic - Medium - R300', 'French Acrylic - Medium - R300'),
        ('French Acrylic - Long - R350', 'French Acrylic - Long - R350'),
        ('Ombre Design - Short - R280', 'Ombre Design - Short - R280'),
        ('Ombre Design - Medium - R350', 'Ombre Desgin - Medium - R350'),
        ('Ombre Design - Long - R400', 'Ombre Design - Long - R400'),
        ('Chrome Design - Short - R330', 'Chrome Design - Short - R330'),
        ('Chrome Design - Medium - R350', 'Chrome Desgin - Medium - R350'),
        ('Chrome Design - Long - R400', 'Chrome Design - Long - R400'),
        ('Gel Toes and Hands - Gel Tip - R180', 'Gel Toes and Hands - Gel Tip - R180'),
        ('Gel Toes and Hands - Gel On Natural Nails - R150', 'Gel Toes and Hands - Gel On Natural Nails - R150'),
        ('Acrylic Toes - Plain Overlay - R150', 'Acrylic Toes - Plain Overlay - R150'),
        ('Acrylic Toes - Tips Overlay - R180', 'Acrylic Toes - Tips Overlay - R180'),
        ('Acrylic Toes - French Overlay - R200', 'Acrylic Toes - French Overlay - R200'),
        ('Acrylic Toes - Buff and Shine with Art - R150', 'Acrylic Toes - Buff and Shine with Art - R150'),
        ('Acrylic Toes - Buff and Shine Plain - R100', 'Acrylic Toes - Buff and Shine Plain - R100'),
        ('Acrylic Toes - Soak Off - R60', 'Acrylic Toes - Soak Off - R60'),
        ('Acrylic Toes - Art Per Nail - R10-20', 'Acrylic Toes - Art Per Nail - R10-20'),
        ('Make-Up - Natural Look - R350', 'Make-Up - Natural Look - R350'),
        ('Make-Up - Classic Glam - R450', 'Make-Up - Classic Glam - R450'),
        ('Make-Up - Full Glam - R550', 'Make-Up - Full Glam - R550'),
        ('Make-Up - Bridal Look - R750', 'Make-Up - Bridal Look - R750'),
        ('Make-Up - Bridesmaids - R450', 'Make-Up - Bridesmaides - R450'),
        ('Make-Up - Flower Girl - R200', 'Make-Up - Flower Girl - R200'),
        ('Lashes - Cat Eye - R250', 'Lashes - Cat Eye - R250'),
        ('Lashes - Medium Volume - R250', 'Lashes - Medium Volume - R250'),
        ('Lashes - Classic/Natural - R200', 'Lashes - Classic/Natural - R200'),
        ('Lashes - Mega Medium - R400', 'Lashes - Mega Medium - R400'),
        ('Lashes - Hybrid - R350', 'Lashes - Hybrid - R350'),
        ('Lashes - Individual Lashes - R350-400', 'Lashes - Individual Lashes - R350-400'),
        ('Lashes - Lash Cleaners - R80', 'Lashes - Lash Cleaners - R80'),
        ('Lashes - Lash Removal - R100', 'Lashes - Lash Removal - R100'),
        ('Lashes - Refill - R100/150', 'Lashes - Refill - R100/150'),
        ('Lashes - Brow Shaping - R40', 'Lashes - Brow Shaping - R40'),
        ('Lashes - Brow Tint - R100', 'Lashes - Brow Tint - R100'),
    ])
    submit = SubmitField('Apply Filters')
    clear = SubmitField('Clear Filters')


class ManageUpdatesPromotionsForm(FlaskForm):
    promotion = StringField('Enter Promotion Details')
    update = StringField('Enter Update Details')
    submit = SubmitField('Submit')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and form.password.data == user.password:
            login_user(user)
            return redirect(url_for('admin'))
        flash('Invalid Username or Password', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully been loggoed out', 'success')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    form = AppointmentForm()
    promotions_updates = PromotionUpdates.query.all()

    booked_days = db.session.query(Appointment.date).group_by(Appointment.date).having(db.func.count(Appointment.id) >= 10).all()
    fully_booked_days = [day[0].strftime('%a, %b %d') for day in booked_days]

    unavailable_slots = {}
    appointments = Appointment.query.all()
    for appointment in appointments: 
        date_str = appointment.date.strftime('%a, %b %d')
        if date_str not in unavailable_slots:
            unavailable_slots[date_str] = []
        unavailable_slots[date_str].append(appointment.time)
        

    if form.validate_on_submit():
        selected_date = form.date.data
        selected_time = form.time.data.strftime('%H:%M')

        appointments_today = Appointment.query.filter_by(date=selected_date).all()

        if len(appointments_today) >= 10:
            flash('Sorry, this date is fully booked. Please choose another date. Refer to our date and time slots.', 'error')
            return render_template('index.html', form=form, fully_booked_days=fully_booked_days, unavailable_slots=unavailable_slots, promotions_updates=promotions_updates)
        
        selected_time_obj = datetime.strptime(selected_time, '%H:%M')

        for appointment in appointments_today:
            booked_time_obj = datetime.strptime(appointment.time, '%H:%M')
            time_diff = abs((selected_time_obj - booked_time_obj).total_seconds() / 60)

            if time_diff < 30:
                flash('Selected time conflicts with an existing booking. Choose another slot. Refer to our date and time slots.', 'error')
                return render_template('index.html', form=form, fully_booked_days=fully_booked_days, unavailable_slots=unavailable_slots, promotions_updates=promotions_updates)
            
        new_appointment = Appointment(date=selected_date, time=selected_time, name=form.name.data, email=form.email.data, phone=form.phone.data, service=form.service.data, notes=form.notes.data)
        db.session.add(new_appointment)
        db.session.commit()

        return redirect(url_for('success'))
    return render_template('index.html', form=form, fully_booked_days=fully_booked_days, unavailable_slots=unavailable_slots, promotions_updates=promotions_updates)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    query = Appointment.query
    form = EditAppointmentForm()
    filter_form = FilterForm()

    if filter_form.validate_on_submit():
        if filter_form.submit.data:
            if filter_form.name.data:
                query = query.filter(Appointment.name.ilike(f'%{filter_form.name.data}%'))
            if filter_form.date.data:
                query = query.filter(Appointment.date == filter_form.date.data)
            if filter_form.time.data:
                query = query.filter(Appointment.time == filter_form.time.data.strftime('%H:%M'))
            if filter_form.service.data:
                query = query.filter(Appointment.service == filter_form.service.data)
        elif filter_form.clear.data:
            return redirect(url_for('admin'))

    appointments = query.all()
    return render_template('admin.html', appointments=appointments, form=form, filter_form=filter_form)

@app.route('/manage_updates_promotions', methods=['GET', 'POST'])
@login_required
def manage_updates_promotions():
    form = ManageUpdatesPromotionsForm()
    promotions_updates = PromotionUpdates.query.all()
    if form.validate_on_submit():
        promotion = form.promotion.data
        update = form.update.data
        new_promotion_update = PromotionUpdates(promotion=promotion, updates=update)
        db.session.add(new_promotion_update)
        db.session.commit()
        flash('Promotions and updates have been successfully added.', 'success')
        return redirect(url_for('manage_updates_promotions'))
    return render_template('manage_updates_promotions.html', form=form, promotions_updates=promotions_updates)

@app.route('/delete_promotion_update/<int:id>', methods=['POST', 'GET'])
@login_required
def delete_promotion_update(id):
    promotion_update = PromotionUpdates.query.get(id)
    db.session.delete(promotion_update)
    db.session.commit()
    flash('Promotion or Update has been removed', 'success')
    return redirect(url_for('manage_updates_promotions'))

@app.route('/delete_appointment/<int:id>', methods=['POST', 'GET'])
@login_required
def delete(id):
    appointment = Appointment.query.get_or_404(id)
    db.session.delete(appointment)
    db.session.commit()
    flash('An appointment has been completed or cancelled', 'success')
    return redirect(url_for('admin'))

@app.route('/edit_appointment/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    form = EditAppointmentForm()
    if form.validate_on_submit():
        appointment.date = form.date.data
        appointment.time = form.time.data.strftime('%H:%M')
        db.session.commit()
        flash('An appointment has been rescheduled', 'success')
        return redirect(url_for('admin', form=form, appointment=appointment))
    return render_template('admin.html', form=form, appointment=appointment)
    

@app.route('/success')
def success():
    return render_template('success.html')


if __name__ == '__main__':
    with app.app_context(): 
        db.create_all()
    app.run(host='0.0.0.0', debug=False)