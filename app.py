
# Basic flask app with form based login & signup flows.
#
# From https://github.com/maxcountryman/flask-login
#

import flask
import flask_login

# Our mock database.
USERS = {
    'admin': {'password': 'password'},
    'user': {'password': 'password'},
    'apiuser': {'password': 'password'}
}

app = flask.Flask(__name__)
app.secret_key = 'super secret string 12345'  # Change this!

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in USERS:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in USERS:
        return

    user = User()
    user.id = email
    return user


# the index page
@app.route('/')
@app.route('/index.html')
def home():
    return flask.render_template('index.html.jinja', title='home', flask_login=flask_login)


# serve static content
@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory('static', 'favicon.ico')


@app.route('/static/<path:path>')
def static_assets(path):
    return flask.send_from_directory('static', path)


# register and signup routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    form-based authentication flow
    """

    # handle GETs
    if flask.request.method == 'GET':
        return flask.render_template('login.html.jinja', title='login', flask_login=flask_login)

    # successful login POST
    email = flask.escape(flask.request.form['email'])
    password = flask.escape(flask.request.form['password'])
    if password == USERS.get(email, {}).get('password', None):
        user = User()
        user.id = email
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('members'))

    # unsuccessful login POST
    return flask.render_template('login.html.jinja', title='login', flask_login=flask_login, err='Bad Login'), 401


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    form-based signup flow
    """

    # handle GETs
    if flask.request.method == 'GET':
        return flask.render_template('login.html.jinja', title='register', flask_login=flask_login)

    # signup POST processing
    email = flask.escape(flask.request.form['email'])
    password = flask.escape(flask.request.form['password'])
    if email in USERS.keys():
        return flask.render_template('login.html.jinja', title='register', flask_login=flask_login, err='User already exists'), 400

    if len(password) < 5:
        return flask.render_template('login.html.jinja', title='register', flask_login=flask_login, err='Password is too weak'), 400

    # successful signup POST
    USERS[email] = {"password": password}
    return flask.render_template('login.html.jinja', title='register', flask_login=flask_login, signupemail=email)


#members routes
@app.route('/members')
@flask_login.login_required
def members():
    """
    protected route, requiring a valid auth cookie
    """
    return flask.render_template('members.html.jinja', title='members', flask_login=flask_login, message='90265')


#checkout routes
@app.route('/checkout', methods=['GET', 'POST'])
@flask_login.login_required
def checkout():
    """
    protected route, requiring a valid auth cookie
    """

    # handle GETs
    if flask.request.method == 'GET':
        return flask.render_template('checkout.html.jinja', title='register', flask_login=flask_login, message='90265')

    # signup POST processing
    frm = flask.escape(flask.request.form['from'])
    to = flask.escape(flask.request.form['to'])
    route = f'from {frm} to {to}'

    return flask.render_template('checkout.html.jinja', title='checkout', flask_login=flask_login, message='90265', booksuccessful=route )


# api routes


@app.route('/api/login', methods=['POST'])
def api_login():
    """
    login API endpoint
    """

    # successful login POST
    json = flask.request.get_json(force=True)
    email = flask.escape(json.get('email'))
    password = flask.escape(json.get('password'))
    if password == USERS.get(email, {}).get('password', None):
        user = User()
        user.id = email
        flask_login.login_user(user)
        return flask.jsonify({"err": False, "msg": "valid credentials", "user": flask_login.current_user.id, "next": flask.url_for('members')}), 200

    # unsuccessful login POST
    return flask.jsonify({"err": True, "msg": "invalid credentials"}), 401


@app.route('/api/members', methods=['GET'])
@flask_login.login_required
def api_members():
    """
    members API endpoint
    """

    return flask.jsonify({"err": False, "user": flask_login.current_user.id, "balance": 90265}), 200


@app.route('/api/checkout', methods=['GET', 'POST'])
@flask_login.login_required
def api_checkout():
    """
    checkout API endpoint
    """

    if flask.request.method == 'GET':
        return flask.jsonify({"err": False, "user": flask_login.current_user.id, "balance": 90265}), 200

    # successful login POST
    json = flask.request.get_json(force=True)
    frm = flask.escape(json.get('from'))
    to = flask.escape(json.get('to'))
    route = f'from {frm} to {to}'

    return flask.jsonify({"err": False, "msg": "booked", "user": flask_login.current_user.id, "balance": 90265, "route": route}), 200


# logout route
@app.route('/logout')
def logout():
    """
    logout / expire auth cookie
    """
    flask_login.logout_user()
    return flask.redirect(flask.url_for('home'))


@login_manager.unauthorized_handler
def unauthorized_handler():
    return flask.render_template('members.html.jinja', title='unauthorized', flask_login=flask_login, err='Access Denied'), 403


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)
