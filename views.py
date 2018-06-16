import os
import random
import string
import json
import httplib2
import requests
from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash, make_response
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import *
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from functools import wraps

# Flask instance
app = Flask(__name__)

# Google client id
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Name of the application
APPLICATION_NAME = "Catalog Items App"

# Connect to database
engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine

# Create database session
DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(f):
    """Checks to see whether a user is logged in"""
    @wraps(f)
    def x(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return x


# User helper functions

def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   image=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email'])\
        .one_or_none()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Show all categories on the catalog home page
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    """
    Show the home page of item catalog application
    Only logged-in user can create a new category.
    :return: the rendered page of catalog app
    """
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(asc(Item.name))

    if 'username' not in login_session:
        return render_template('public_catalog.html',
                               categories=categories,
                               items=items)
    else:
        user = getUserInfo(login_session['user_id'])
        return render_template('catalog.html',
                               categories=categories,
                               items=items)


# Show all items of a specific category
@app.route('/catalog/<path:categoryName>/')
@app.route('/catalog/<path:categoryName>/items/')
def showCategory(categoryName):
    """
    Show the page of a specific category.
    :param categoryName: name of the category user wants to show
    :return:  the rendered page of category
    """
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=categoryName).one()
    items = session.query(Item).filter_by(category=category)\
        .order_by(asc(Item.name)).all()
    itemsCount = session.query(Item).filter_by(category=category).count()
    creator = getUserInfo(category.user_id)
    if 'username' not in login_session or creator.id != \
            login_session['user_id']:
        return render_template('public_category.html',
                               categories=categories,
                               categoryName=categoryName,
                               items=items,
                               count=itemsCount)
    else:
        user = getUserInfo(login_session['user_id'])
        return render_template('category.html',
                               categories=categories,
                               categoryName=categoryName,
                               items=items,
                               count=itemsCount,
                               user=user)


# Show a specific item
@app.route('/catalog/<path:categoryName>/<path:itemName>/')
def showItem(categoryName, itemName):
    """
    Show the page of a specific item.
    User sees difference page of item depending on whether he logs in.
    :param categoryName: name of the category which the item belongs to
    :param itemName: the name of the item
    :return: the rendered page of item
    """
    item = session.query(Item).filter_by(name=itemName).one()
    itemPicture = item.picture
    itemDescription = item.description
    categories = session.query(Category).order_by(asc(Category.name))
    creator = getUserInfo(item.user_id)

    if 'username' not in login_session or creator.id !=\
            login_session['user_id']:
        return render_template('public_item_description.html',
                               item=item,
                               categoryName=categoryName,
                               categories=categories)
    else:
        return render_template('item.html',
                               item=item,
                               categoryName=categoryName,
                               categories=categories)


# Add a new category
@app.route('/catalog/addCategory/', methods=['GET', 'POST'])
@login_required
def addCategory():
    """
    Show the page of adding category.
    Only logged-in user can see the page of adding category.
    :return: the rendered page of adding a new category
    """
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        flash("New category %s has been successfully created!"
              % newCategory.name)
        return redirect(url_for('showCatalog'))
    else:
        return render_template('addCategory.html')


# Edit a category
@app.route('/catalog/<path:categoryName>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(categoryName):
    """
    Show the page of edit a category.
    A category can only be edited by the logged-in user who originally
    creates the category.
    :param categoryName: the name of category to be edited
    :return: the rendered page of editing category
    """
    category = session.query(Category).filter_by(name=categoryName).one()
    creator = getUserInfo(category.user_id)

    if creator.id != login_session['user_id']:
        flash("You do not have the privilege to edit this category!")
        return redirect(url_for('showCatalog'))

    categories = session.query(Category).all()

    if request.method == 'POST':
        if request.form['name']:
            category.name = request.form['name']
        session.add(category)
        session.commit()
        flash("The category %s has been successfully edited!" % category.name)
        return redirect(url_for('showCatalog'))
    else:
        return render_template('editCategory.html', categories=categories,
                               category=category)


# Delete a category
@app.route('/catalog/<path:categoryName>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(categoryName):
    """
    Show the page of delete a category.
    A Category can only be deleted by the logged-in user who originally
    creates the category.
    :param categoryName: the name of category to be deleted
    :return: the rendered page of deleting category
    """
    category = session.query(Category).filter_by(name=categoryName).one()
    creator = getUserInfo(category.user_id)

    # find all items belonging to this category
    items = session.query(Item).filter_by(category=category)\
        .order_by(asc(Item.name)).all()

    if creator.id != login_session['user_id']:
        flash("You do not have the privilege to delete this category!")
        return redirect(url_for('showCatalog'))

    if request.method == 'POST':
        # before deleting the category, first delete all items in the category
        for item in items:
            session.delete(item)
            session.commit()
        # delete the category
        session.delete(category)
        session.commit()
        flash("The category %s has been successfully deleted" % category.name)
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteCategory.html',
                               category=category)


# Add a new item
@app.route('/catalog/addItem/', methods=['GET', 'POST'])
@login_required
def addItem():
    """
    Show the page of creating a new item.
    Only logged-in user can create a new item.
    :return: the rendered page of creating a new item
    """
    categories = session.query(Category).all()
    if request.method == 'POST':
        category = session.query(Category).filter_by(
            name=request.form['category']).one()
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       picture=request.form['picture'],
                       category=category,
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("The item %s has been successfully added!" % newItem.name)
        return redirect(url_for('showCategory', categoryName=category.name))
    else:
        return render_template('addItem.html',
                               categories=categories)


# Edit an item
@app.route('/catalog/<path:categoryName>/<path:itemName>/edit/',
           methods=['GET', 'POST'])
@login_required
def editItem(categoryName, itemName):
    """
    Show the page of editing an item.
    An item can only be edited by the logged-in user
    who originally creates the item.
    :param categoryName: the name of category which the edited item belongs to
    :param itemName: the name of item to be edited
    :return: the rendered page of editing an item
    """
    item = session.query(Item).filter_by(name=itemName).one()
    categories = session.query(Category).all()
    creator = getUserInfo(item.user_id)

    if creator.id != login_session['user_id']:
        flash("You do not have the privilege to edit this item!")
        return redirect(url_for('showCatalog'))

    if request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['picture']:
            item.picture = request.form['picture']
        if request.form['category']:
            category = session.query(Category).filter_by(
                name=request.form['category']).one()
            item.category = category
        session.add(item)
        session.commit()
        flash("The item %s has been successfully edited!" % item.name)
        return redirect(url_for('showCategory',
                                categoryName=item.category.name))
    else:
        return render_template('editItem.html',
                               item=item,
                               categories=categories,
                               categoryName=categoryName)


# Delete an item
@app.route('/catalog/<path:categoryName>/<path:itemName>/delete/',
           methods=['GET', 'POST'])
@login_required
def deleteItem(categoryName, itemName):
    """
    Show the page of deleting an item.
    An item can only be deleted by the logged-in user who originally
    creates the item.
    :param categoryName: the name of category which the item belongs to
    :param itemName: the name of item to be deleted
    :return: the rendered page of deleting an item
    """
    item = session.query(Item).filter_by(name=itemName).one()
    category = session.query(Category).filter_by(name=categoryName).one()
    creator = getUserInfo(category.user_id)

    if creator.id != login_session['user_id']:
        flash("You do not have the privilege to delete this item!")
        return redirect(url_for('showCatalog'))

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("The item %s has been successfully deleted" % item.name)
        return redirect(url_for('showCategory',
                                categoryName=category.name))
    else:
        return render_template('deleteItem.html',
                               item=item)


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Create Google Sign in
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    # request.get_data()
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()

    result = json.loads(h.request(url, 'GET')[1].decode("utf-8"))

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']

    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
                   json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])

    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']
    output += '!</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 80px; height: 80px;border-radius: 100px;' \
              '-webkit-border-radius: 100px;-moz-border-radius: 100px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect the user if he is connected
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Add Facebook Sign in
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # Validate anti-forgery state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = request.data

    app_id = json.loads(open('fb_client_secrets.json', 'r')
                        .read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').
                            read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=' \
          'fb_exchange_token&client_id=%s&client_secret=%s&' \
          'fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = json.loads((h.request(url, 'GET')[1]).decode('utf-8'))

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"

    token = result.get('access_token')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=' \
          'name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&' \
          'redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data['data']['url']

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']

    output += '!</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 100px; height: 100px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


# Facebook disconnect
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']

    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' \
          % (facebook_id, access_token)

    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Disconnect based on login type (provider)
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']

        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in!")
        return redirect(url_for('showCatalog'))


# JSON APIs to view catalog Information


@app.route('/catalog/JSON')
def showCategoriesJSON():
    """return JSON for all categories"""
    categories = session.query(Category).all()
    category_dict = [cat.serialize for cat in categories]
    for cat in range(len(category_dict)):
        items = [item.serialize for item in session.query(Item)
                 .filter_by(category_id=category_dict[cat]["id"]).all()]
        if items:
            category_dict[cat]["Item"] = items
    return jsonify(Category=category_dict)


@app.route('/catalog/<path:categoryName>/JSON')
@app.route('/catalog/<path:categoryName>/items/JSON')
def showCategoryJSON(categoryName):
    """return JSON for a specific category"""
    category = session.query(Category).filter_by(name=categoryName).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(items=[item.serialize for item in items])


@app.route('/catalog/items/JSON')
def showItemsJSON():
    """return JSON for all items"""
    items = session.query(Item).all()
    return jsonify(items=[item.serialize for item in items])


@app.route('/catalog/<path:categoryName>/<path:itemName>/JSON')
def showItemJSON(categoryName, itemName):
    """return JSON for a specific item"""
    category = session.query(Category).filter_by(name=categoryName).one()
    item = session.query(Item).filter_by(name=itemName,
                                         category_id=category.id).one()
    return jsonify(item=[item.serialize])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
