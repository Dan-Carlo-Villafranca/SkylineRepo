from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "skyline_super_secret"

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skyline.db'
db = SQLAlchemy(app)
# start

# Updated Model with more details
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    yob = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_country = db.Column(db.String(50), nullable=False)
    from_city = db.Column(db.String(50), nullable=False)
    to_country = db.Column(db.String(50), nullable=False)
    to_city = db.Column(db.String(50), nullable=False)
    dep_date = db.Column(db.String(20), nullable=False)
    dep_time = db.Column(db.String(20), nullable=False)
    ret_date = db.Column(db.String(20), nullable=False)
    ret_time = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.String(20), nullable=False)
    tickets_economy = db.Column(db.Integer)
    tickets_business = db.Column(db.Integer)
    tickets_first = db.Column(db.Integer)
    price = db.Column(db.Float, nullable=False)
    promo_code = db.Column(db.String(50), nullable=False)
    trip_type=db.Column(db.String(50), nullable=False)
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    # Personal Info
    first_name = db.Column(db.String(100))
    middle_initial = db.Column(db.String(1))
    last_name = db.Column(db.String(100))
    suffix = db.Column(db.String(10))
    dob = db.Column(db.String(20))
    nationality = db.Column(db.String(50))
    status = db.Column(db.String(50)) # Senior, Child, etc.
    # Flight Choices
    tier = db.Column(db.String(20)) # Economy, Business, First
    seat_number = db.Column(db.String(10))
    total_paid = db.Column(db.Float)
    payment_method = db.Column(db.String(20))
    # Inventory Tracking
    seats_remaining_after = db.Column(db.Integer) 


# Run db.create_all() after adding this
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/booking')
def booking():
    # Start with all flights
    query = Flight.query

    # 1. Trip Type Filter
    trip_type = request.args.get('trip_type')
    if trip_type:
        query = query.filter(Flight.trip_type == trip_type)

    # 2. Seat Class Filter (Only show flights that have > 0 tickets in that class)
    seat_class = request.args.get('seat_class')
    if seat_class == 'economy':
        query = query.filter(Flight.tickets_economy > 0)
    elif seat_class == 'business':
        query = query.filter(Flight.tickets_business > 0)
    elif seat_class == 'first':
        query = query.filter(Flight.tickets_first > 0)

    # 3. Destination/Origin Filters
    from_city = request.args.get('from_city')
    if from_city:
        query = query.filter(Flight.from_city.contains(from_city))
    
    to_city = request.args.get('to_city')
    if to_city:
        query = query.filter(Flight.to_city.contains(to_city))

    # 4. Date Filter
    dep_date = request.args.get('dep_date')
    if dep_date:
        query = query.filter(Flight.dep_date == dep_date)

    # 5. Promo Filter
    if request.args.get('has_promo') == 'yes':
        query = query.filter(Flight.promo_code != 'none', Flight.promo_code != '')

    # 6. Sorting
    sort_by = request.args.get('sort_by', 'dep_date')
    if sort_by == 'price':
        query = query.order_by(Flight.price.asc())
    else:
        query = query.order_by(Flight.dep_date.asc())

    flights = query.all()
    return render_template('booking.html', flights=flights, calc_arrival=calculate_arrival)

@app.route('/checkout/<int:flight_id>')
def checkout(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    return render_template('checkout.html', flight=flight, calc_arrival=calculate_arrival)

@app.route('/book_flight/<int:flight_id>')
def book_flight(flight_id):
    flight = Flight.query.get_or_404(flight_id) #
    return render_template('checkout.html', flight=flight, calc_arrival=calculate_arrival)

@app.route('/about')
def about():
    return render_template('index.html')
@app.route('/contact')
def contact():
    return render_template('index.html')

@app.route('/baggage')
def baggage():
    return render_template('baggage.html')
@app.route('/payment')
def payment():
    return render_template('payment.html')
@app.route('/booking&checkin')
def bookinginfo():
    return render_template('checkininfo.html')
@app.route('/specialassistance')
def specialassist():
    return render_template('special.html')
@app.route('/airlinepolicies')
def policies():
    return render_template('policies.html')
@app.route('/popular')
def popular():
    return render_template('popular.html')

# In app.py
def calculate_arrival(start_time_str, duration_str):
    # Check if data is missing or set to "none"
    if not start_time_str or start_time_str == "none" or not duration_str:
        return "--:--"
    
    try:
        # 1. Parse the starting time (e.g., "14:30")
        start_time = datetime.strptime(start_time_str, "%H:%M")
        
        # 2. Extract hours and minutes from duration "12h 30m"
        # We use .replace and .strip to ensure the strings are clean
        clean_duration = duration_str.lower()
        hours = int(clean_duration.split('h')[0].strip())
        minutes = 0
        if 'm' in clean_duration:
            minutes = int(clean_duration.split('h')[1].split('m')[0].strip())
            
        # 3. Add duration to start time
        arrival_time = start_time + timedelta(hours=hours, minutes=minutes)
        return arrival_time.strftime("%H:%M")
    except (ValueError, IndexError):
        # If the user typed the duration wrong (like "12 hours"), return a placeholder
        return "--:--"

@app.route('/edittickets')
def edittickets():
    return render_template('index.html')

@app.route('/addpromos')
def addpromos():
    return render_template('index.html')

@app.route('/editpromos')
def editpromos():
    return render_template('index.html')

@app.route('/archivetickets')
def archivetickets():
    return render_template('index.html')

@app.route('/archivepromos')
def archivepromos():
    return render_template('index.html')

@app.route('/managebook')
def managebook():
    return render_template('index.html')

@app.route('/archivebook')
def archivebook():
    return render_template('index.html')

@app.route('/manageuser')
def manageuser():
    return render_template('index.html')

@app.route('/logs')
def logs():
    return render_template('index.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            return f"Welcome back, {user.first_name}!"
        return "Invalid login."
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = request.form.get('first_name')
        lname = request.form.get('last_name')
        yob = request.form.get('yob')
        email = request.form.get('email')
        pw = request.form.get('password')
        pw_confirm = request.form.get('confirm_password')
    # if you fuck up the pass validation    
        if pw != pw_confirm:
            return "Passwords do not match!"

    # find email in db so no dupes
        if User.query.filter_by(email=email).first():
            return "Email already exists!"

        # put shit in db
        new_user = User(first_name=fname, last_name=lname, yob=yob, email=email, password=pw)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/addtickets', methods=['GET', 'POST'])
def addtickets():
    if request.method == 'POST':
        # 1. Determine Trip Type String
        trip_type_value = "one way trip"

        # 2. Handle Price Logic
        raw_price = float(request.form.get('price', 0))
        final_price = raw_price * 2 if is_round_trip else raw_price
        ret_date= "none"
        ret_time= "none"
        # 3. Create the Flight Object
        new_flight = Flight(
            from_country=request.form.get('from_country'),
            from_city=request.form.get('from_city'),
            to_country=request.form.get('to_country'),
            to_city=request.form.get('to_city'),
            dep_date=request.form.get('dep_date'),
            dep_time=request.form.get('dep_time'),

            ret_date=ret_date,
            ret_time=ret_time,

            duration=request.form.get('duration'),
            tickets_economy=request.form.get('tickets_economy'),
            tickets_business=request.form.get('tickets_business'),
            tickets_first=request.form.get('tickets_first'),
            
            # Use our new calculated values
            trip_type=trip_type_value, 
            price=final_price,
            
            promo_code=request.form.get('promo_code')
        )
        
        db.session.add(new_flight)
        db.session.commit()
        return "Flight Added! <a href='/addtickets'>Back</a>"

    return render_template('addtickets.html')

@app.route('/addticketsround', methods=['GET', 'POST'])
def addticketsround():
    if request.method == 'POST':
        raw_price = float(request.form.get('price', 0))
        final_price = raw_price * 2
        trip_type_value = "round trip"
        # 3. Create the Flight Object
        new_flight = Flight(
            from_country=request.form.get('from_country'),
            from_city=request.form.get('from_city'),
            to_country=request.form.get('to_country'),
            to_city=request.form.get('to_city'),
            dep_date=request.form.get('dep_date'),
            dep_time=request.form.get('dep_time'),
            ret_date=request.form.get('ret_date'),
            ret_time=request.form.get('ret_time'),
            duration=request.form.get('duration'),
            tickets_economy=request.form.get('tickets_economy'),
            tickets_business=request.form.get('tickets_business'),
            tickets_first=request.form.get('tickets_first'),
            
            # Use our new calculated values
            trip_type=trip_type_value, 
            price=final_price,
            
            promo_code=request.form.get('promo_code')
        )
        
        db.session.add(new_flight)
        db.session.commit()
        return "Flight Added! <a href='/addticketsround'>Back</a>"

    return render_template('addticketsround.html')

@app.route('/process_booking/<int:flight_id>', methods=['POST'])
def process_booking(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    
    # Get form data
    tier = request.form.get('tier_choice')
    p_count = int(request.form.get('p_count', 1))
    payment_method = request.form.get('payment_method')
    total_paid = float(request.form.get('total_amount', 0))

    # We loop through based on the number of passengers
    for i in range(1, p_count + 1):
        # Update Inventory based on Tier
        if tier == 'economy':
            current_seats = flight.tickets_economy
            flight.tickets_economy -= 1
        elif tier == 'business':
            current_seats = flight.tickets_business
            flight.tickets_business -= 1
        else:
            current_seats = flight.tickets_first
            flight.tickets_first -= 1

        # Create unique booking for each passenger
        new_booking = Booking(
            flight_id=flight.id,
            first_name=request.form.get(f'first_name_{i}'),
            middle_initial=request.form.get(f'mi_{i}'),
            last_name=request.form.get(f'last_name_{i}'),
            suffix=request.form.get(f'suffix_{i}'),
            dob=request.form.get(f'dob_{i}'),
            nationality=request.form.get(f'nationality_{i}'),
            status=request.form.get(f'status_{i}'), # e.g. "Senior"
            tier=tier,
            seat_number=request.form.get('selected_seat') if i == 1 else "Auto-Assigned",
            total_paid=total_paid / p_count, # Split total among tickets
            payment_method=payment_method,
            seats_remaining_after=flight.tickets_economy if tier == 'economy' else (flight.tickets_business if tier == 'business' else flight.tickets_first)
        )
        db.session.add(new_booking)

    db.session.commit()
    flash(f"Success! {p_count} ticket(s) have been booked.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)