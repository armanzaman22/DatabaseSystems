from market import app #,login_manager
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User, Restaurant
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm, AddRestaurantForm, AddMealForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user
#from functools import wraps

# These commented sections raise errors but I cannot find any reason why, thus their functionality is turned off
# def login_required(role="ANY"):
#    def wrapper(fn):
#        @wraps(fn)
#        def decorated_view(*args, **kwargs):
#            if not current_user.is_authenticated():
#              return login_manager.unauthorized()
#            if ((current_user.role != role) and (role != "ANY")):
#                return login_manager.unauthorized()
#            return fn(*args, **kwargs)
#        return decorated_view
#    return wrapper

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/restaurants')
@login_required
def restaurant_page():
    restaurants = Restaurant.query.all()
    return render_template('restaurants.html', restaurants=restaurants)

@app.route('/<restaurant>/market', methods=['GET', 'POST'])
@login_required
def market_page(restaurant):
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == "POST":
        #Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for {p_item_object.price}$", category='success')
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item_object.name}!", category='danger')
        #Sell Item Logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"Congratulations! You sold {s_item_object.name} back to market!", category='success')
            else:
                flash(f"Something went wrong with selling {s_item_object.name}", category='danger')


        return redirect(url_for('home_page'))

    if request.method == "GET":
        items = Item.query.filter_by(sold_by=restaurant)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items, selling_form=selling_form)

@app.route('/addrestaurant', methods=['GET', 'POST'])
@login_required
def insert_restaurant_page():
    form = AddRestaurantForm()
    if form.validate_on_submit():    
        restaurant_to_create = Restaurant(name=form.name.data,
                                      address = form.address.data,
                                      phone = form.phone.data,
                                      email=form.email.data)
        db.session.add(restaurant_to_create)
        db.session.commit()
        flash(f'Success! You have added: {restaurant_to_create.name}', category='success')
        return redirect(url_for('insert_restaurant_page'))
    else:
        flash('Error! Fill the forms in correctly.', category='danger')
        
    return render_template('addrestaurant.html', form=form)

@app.route('/addmeal', methods=['GET', 'POST'])
@login_required
def insert_meal_page():
    form = AddMealForm()
    if form.validate_on_submit():    
        meal_to_create = Item(name=form.name.data,
                              price = form.price.data,
                              description = form.description.data,
                              sold_by=form.sold_by.data)
        db.session.add(meal_to_create)
        db.session.commit()
        flash(f'Success! You have added: {meal_to_create.name}', category='success')
        return redirect(url_for('insert_meal_page'))
    else:
        flash('Error! Fill the forms in correctly.', category='danger')
    return render_template('addmeal.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('home_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))










