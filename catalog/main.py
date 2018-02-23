#!/usr/bin/python
from flask import Flask, render_template, request, redirect, url_for, \
    flash, jsonify
from flask import session as login_session
from flask import make_response

# importing SqlAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, ClothDB, User
import random
import string
import httplib2
import json
import requests

# importing oauth

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials

# app configuration

app = Flask(__name__)
app.secret_key = 'itsasecret1'

# google client secret
secret_file = json.loads(open('client_secrets.json', 'r').read())
CLIENT_ID = secret_file['web']['client_id']
APPLICATION_NAME = 'Clothing Catalog'

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

engine = create_engine('sqlite:///ClothesCatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# validating current loggedin user

def check_user():
    email = login_session['email']
    return session.query(User).filter_by(email=email).one_or_none()


# retreive admin user details

def check_admin():
    return session.query(User).filter_by(
        email='arpanasrinivas@gmail.com').one_or_none()


# Add new user into database

def createUser():
    name = login_session['name']
    email = login_session['email']
    url = login_session['img']
    provider = login_session['provider']
    newUser = User(name=name, email=email, image=url, provider=provider)
    session.add(newUser)
    session.commit()


def new_state():
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    return state


def queryAllClothes():
    return session.query(ClothDB).all()

#main page 1

# main page

@app.route('/')
@app.route('/clothes/')
def showClothes():
    clothes = queryAllClothes()
    state = new_state()
    return render_template('main.html', clothes=clothes, currentPage='main',
                           state=state, login_session=login_session)


# To add new Cloth 

@app.route('/clothes/new/', methods=['GET', 'POST'])
def newCloth():
    if request.method == 'POST':

        # check if user is logged in or not

        if 'provider' in login_session and \
                    login_session['provider'] != 'null':
            brandName = request.form['brandName']
            color = request.form['color']
            price = request.form['price']
            description = request.form['clothDescription']
            description = description.replace('\n', '<br>')
            clothCategory = request.form['category']
            user_id = check_user().id

            if brandName and color and price and description \
                    and clothCategory:
                    newCloth = ClothDB(
                    brandName=brandName,
                    color=color,
                    price=price,
                    description=description,
                    category=clothCategory,
                    user_id=user_id,
                    )
                    session.add(newCloth)
                    session.commit()
                    return redirect(url_for('showClothes'))
            else:
                state = new_state()
                return render_template(
                    'newItem.html',
                    currentPage='new',
                    title='Add New Cloth',
                    errorMsg='All Fields are Required!',
                    state=state,
                    login_session=login_session,
                    )
        else:
            state = new_state()
            clothes = queryAllClothes()
            return render_template(
                'main.html',
                clothes=clothes,
                currentPage='main',
                state=state,
                login_session=login_session,
                errorMsg='Please Login first to Add Cloth!',
                )
    elif 'provider' in login_session and login_session['provider'] \
            != 'null':
        state = new_state()
        return render_template('newItem.html', currentPage='new',
                               title='Add New Cloth', state=state,
                               login_session=login_session)
    else:
        state = new_state()
        clothes = queryAllClothes()
        return render_template(
            'main.html',
            clothes=clothes,
            currentPage='main',
            state=state,
            login_session=login_session,
            errorMsg='Please Login first to Add Cloth!',
            )


# To show cloth of different category

@app.route('/clothes/category/<string:category>/')
def sortClothes(category):
    clothes= session.query(ClothDB).filter_by(category=category).all()
    state = new_state()
    return render_template(
        'main.html',
        clothes=clothes,
        currentPage='main',
        error='Sorry! No Clothes in Database With This Category :(',
        state=state,
        login_session=login_session)


# To show cloth detail

@app.route('/clothes/category/<string:category>/<int:clothId>/')
def clothDetail(category, clothId):
   cloth = session.query(ClothDB).filter_by(id=clothId,
                                           category=category).first()
   state = new_state()
   if cloth:
        return render_template('itemDetail.html', cloth=cloth,
                               currentPage='detail', state=state,
                               login_session=login_session)
   else:
        return render_template('main.html', currentPage='main',
                               error="""No Cloth Found with this Category
                               and Cloth Id :(""",
                               state=state,
                               login_session=login_session)


# To edit cloth detail

@app.route('/clothes/category/<string:category>/<int:clothId>/edit/',
           methods=['GET', 'POST'])
def editClothDetails(category, clothId):
    cloth = session.query(ClothDB).filter_by(id=clothId,
                                           category=category).first()
    if request.method == 'POST':

        # check if user is logged in or not

        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            brandName = request.form['brandName']
            color = request.form['color']
            price = request.form['price']
            description = request.form['clothDescription']
            clothCategory = request.form['category']
            user_id = check_user().id
            admin_id = check_admin().id

            # check if brand owner is same as logged in user or admin or not

            if cloth.user_id == user_id or user_id == admin_id:
                if brandName and color and price and description \
                        and clothCategory:
                    cloth.brandName = brandName
                    cloth.color = color 
                    cloth.price = price 
                    description = description.replace('\n', '<br>')
                    cloth.description = description
                    cloth.category = clothCategory
                    session.add(cloth)
                    session.commit()
                    return redirect(url_for('clothDetail',
                                    category=cloth.category,
                                    clothId=cloth.id))
                else:
                    state = new_state()
                    return render_template(
                        'editItem.html',
                        currentPage='edit',
                        title='Edit Cloth Details',
                        cloth=cloth,
                        state=state,
                        login_session=login_session,
                        errorMsg='All Fields are Required!',
                        )
            else:
                state = new_state()
                return render_template(
                    'itemDetail.html',
                    cloth=cloth,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! The Owner can only edit cloth Details!')
        else:
            state = new_state()
            return render_template(
                'itemDetail.html',
                cloth=cloth,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Edit the Cloth Details!',
                )
    elif cloth:
        state = new_state()
        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            user_id = check_user().id
            admin_id = check_admin().id
            if user_id == cloth.user_id or user_id == admin_id:
                cloth.description = cloth.description.replace('<br>', '\n')
                return render_template(
                    'editItem.html',
                    currentPage='edit',
                    title='Edit Cloth Details',
                    cloth=cloth,
                    state=state,
                    login_session=login_session,
                    )
            else:
                return render_template(
                    'itemDetail.html',
                    cloth=cloth,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! The Owner can only edit Cloth Details!')
        else:
            return render_template(
                'itemDetail.html',
                cloth=cloth,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Edit the Cloth Details!',
                )
    else:
        state = new_state()
        return render_template('main.html', currentPage='main',
                               error="""Error Editing Cloth! No Cloth Found
                               with this Category and Cloth Id :(""",
                               state=state,
                               login_session=login_session)


# To delete clothes 

@app.route('/clothes/category/<string:category>/<int:clothId>/delete/')
def deleteCloth(category, clothId):
    cloth = session.query(ClothDB).filter_by(category=category,
                                           id=clothId).first()
    state = new_state()
    if cloth:

        # check if user is logged in or not

        if 'provider' in login_session and login_session['provider'] \
                != 'null':
            user_id = check_user().id
            admin_id = check_admin().id
            if user_id == cloth.user_id or user_id == admin_id:
                session.delete(cloth)
                session.commit()
                return redirect(url_for('showClothes'))
            else:
                return render_template(
                    'itemDetail.html',
                    cloth=cloth,
                    currentPage='detail',
                    state=state,
                    login_session=login_session,
                    errorMsg='Sorry! Only the Owner Can delete the cloth'
                    )
        else:
            return render_template(
                'itemDetail.html',
                cloth=cloth,
                currentPage='detail',
                state=state,
                login_session=login_session,
                errorMsg='Please Login to Delete the Cloth!',
                )
    else:
        return render_template('main.html', currentPage='main',
                               error="""Error Deleting Cloth! No Cloth Found
                               with this Category and Cloth Id :(""",
                               state=state,
                               login_session=login_session)


# JSON Endpoints

@app.route('/clothes.json/')
def clothesJSON():
    clothes = session.query(ClothDB).all()
    return jsonify(Clothes=[cloth.serialize for cloth in clothes])


@app.route('/clothes/category/<string:category>.json/')
def clothCategoryJSON(category):
    clothes = session.query(ClothDB).filter_by(category=category).all()
    return jsonify(Clothes=[cloth.serialize for cloth in clothes])


@app.route('/clothes/category/<string:category>/<int:clothId>.json/')
def clothJSON(category, clothId):
    cloth = session.query(ClothDB).filter_by(category=category,
                                           id=clothId).first()
    return jsonify(Cloth=cloth.serialize)


# google signin function

@app.route('/gconnect', methods=['POST'])
def gConnect():
    if request.args.get('state') != login_session['state']:
        response.make_response(json.dumps('Invalid State paramenter'),
                               401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code

    code = request.data
    try:

        # Upgrade the authorization code into a credentials object

        oauth_flow = flow_from_clientsecrets('client_secrets.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps("""Failed to upgrade the
        authorisation code"""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % access_token
    header = httplib2.Http()
    result = json.loads(header.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
                            """Token's user ID does not
                            match given user ID."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            """Token's client ID
            does not match app's."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user is already connected.'),
                          200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['credentials'] = access_token
    login_session['id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # ADD PROVIDER TO LOGIN SESSION

    login_session['name'] = data['name']
    login_session['img'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'
    if not check_user():
        createUser()
    return jsonify(name=login_session['name'],
                   email=login_session['email'],
                   img=login_session['img'])


# logout user

@app.route('/logout', methods=['post'])
def logout():

    # Disconnect based on provider

    if login_session.get('provider') == 'google':
        return gdisconnect()
    else:
        response = make_response(json.dumps({'state': 'notConnected'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['credentials']

    # Only disconnect a connected user.

    if access_token is None:
        response = make_response(json.dumps({'state': 'notConnected'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % access_token
    header = httplib2.Http()
    result = header.request(url, 'GET')[0]

    if result['status'] == '200':

        # Reset the user's session.

        del login_session['credentials']
        del login_session['id']
        del login_session['name']
        del login_session['email']
        del login_session['img']
        login_session['provider'] = 'null'
        response = make_response(json.dumps({'state': 'loggedOut'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:

        # if given token is invalid, unable to revoke token

        response = make_response(json.dumps({'state': 'errorRevoke'}),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

if __name__ == '__main__':
    app.debug = True
    app.run(host='', port=5000)
