import os

from flask import Flask
from flask_login import login_user, LoginManager, UserMixin, logout_user, current_user

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate


SECRET_KEY=os.urandom(12)

# CREDIT: This code is copied from Dash official documentation:
# https://dash.plotly.com/urls

# Since we're adding callbacks to elements that don't exist in the app.layout,
# Dash will raise an exception to warn us that we might be
# doing something wrong.
# In this case, we're adding the elements through a callback, so we can ignore
# the exception.
# Exposing the Flask Server to enable configuring it for logging in
server = Flask(__name__)
app = dash.Dash(__name__, server=server,
                suppress_callback_exceptions=True)

# Updating the Flask Server configuration with Secret Key to encrypt the user session cookie
server.config.update(SECRET_KEY=SECRET_KEY)

# Login manager object will be used to login / logout users
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

# User data model. It has to have at least self.id as a minimum


class User(UserMixin):
    def __init__(self, username):
        self.id = username


@ login_manager.user_loader
def load_user(username):
    ''' This function loads the user by user id. Typically this looks up the user from a user database.
        We won't be registering or looking up users in this example, since we'll just login using LDAP server.
        So we'll simply return a User object with the passed in username.
    '''
    return User(username)


# User status management views


# Login screen
login = html.Div([dcc.Location(id='url_login', refresh=True),
                  html.H2('''Please log in to continue:''', id='h1'),
                  dcc.Input(placeholder='Enter your username',
                            type='text', id='uname-box'),
                  dcc.Input(placeholder='Enter your password',
                            type='password', id='pwd-box'),
                  html.Button(children='Login', n_clicks=0,
                              type='submit', id='login-button'),
                  html.Div(id='output-state')
                  ])

# Successful login
success = html.Div([
    html.H1('Page 1'),
    dcc.Dropdown(
        id='page-1-dropdown',
        options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
        value='LA'
    ),
    html.Div(id='page-1-content'),
    html.Br(),
    dcc.Link('Go to Page 2', href='/page-2'),
    html.Br(),
    dcc.Link('Go back to home', href='/'),
])


# Failed Login
failed = html.Div([html.Div([html.H2('Log in Failed. Please try again.'),
                             html.Br(),
                             html.Div([login])
                             ])  # end div
                   ])  # end div

# logout
logout = html.Div([html.Div(html.H2('You have been logged out - Please login')),
                   html.Br()
                   ])  # end div

# Callback function to login the user, or update the screen if the username or password are incorrect


@app.callback(
    Output('url_login', 'pathname'), 
    Output('output-state', 'children'), 
    [Input('login-button', 'n_clicks')], 
    [State('uname-box', 'value'), State('pwd-box', 'value')])
def login_button_click(n_clicks, username, password):
    if n_clicks > 0:
        if username == 'test' and password == 'test':
            user = User(username)
            login_user(user)
            return '/success', ''
        else:
            return '/login', 'Incorrect username or password'
    
    raise PreventUpdate


# Main Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Location(id='redirect', refresh=True),
    html.Div(id='page-content'),
    dcc.Location(id='url_login', refresh=True),
    html.H2('''Please log in to continue:''', id='h1'),
    dcc.Input(placeholder='Enter your username', type='text', id='uname-box'),
    dcc.Input(placeholder='Enter your password', type='password', id='pwd-box'),
    html.Button(children='Login', n_clicks=0, type='submit', id='login-button'),
    html.Div(id='output-state')
])

@app.callback(Output('page-1-content', 'children'),
              [Input('page-1-dropdown', 'value')])
def page_1_dropdown(value):
    return 'You have selected "{}"'.format(value)

# Main router


@app.callback(Output('page-content', 'children'), Output('redirect', 'pathname'),
              [Input('url', 'pathname')])
def display_page(pathname):
    ''' callback to determine layout to return '''
    # We need to determine two things for everytime the user navigates:
    # Can they access this page? If so, we just return the view
    # Otherwise, if they need to be authenticated first, we need to redirect them to the login page
    # So we have two outputs, the first is which view we'll return
    # The second one is a redirection to another page is needed
    # In most cases, we won't need to redirect. Instead of having to return two variables everytime in the if statement
    # We setup the defaults at the beginning, with redirect to dash.no_update; which simply means, just keep the requested url
    view = None
    url = dash.no_update
    if pathname == '/login':
        view = login
    elif pathname == '/success':
        if current_user.is_authenticated:
            view = success
        else:
            view = failed
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            view = logout
        else:
            view = login
            url = '/login'
    # You could also return a 404 "URL not found" page here
    return view, url


if __name__ == '__main__':
    app.run_server(debug=True)