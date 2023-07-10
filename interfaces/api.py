from flask import Flask, session
from flask_restx import Api, Resource
from scraper import initialise_selenium, MyGesScraper
from utils.schedule_utils import get_week_schedule_json


app = Flask(__name__)
api = Api(app, version='1.0', title='MyGes API', description='A simple API to fetch MyGes data')

app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'

ns = api.namespace('myges', description='MyGes operations')

login_parser = api.parser()
login_parser.add_argument('username', type=str, required=True, help='Username for MyGes', location='json')
login_parser.add_argument('password', type=str, required=True, help='Password for MyGes', location='json')


@ns.route('/login')
class Login(Resource):
    @api.expect(login_parser)
    @api.response(200, 'Successful login')
    @api.response(401, 'Login failed')
    def post(self):
        args = login_parser.parse_args()
        username = args.get('username')
        password = args.get('password')
        session['username'] = username
        session['password'] = password
        driver = initialise_selenium()
        scraper = MyGesScraper(driver, username, password)
        login = scraper.login()
        driver.quit()

        if login:
            return {'message': 'Logged in and fetched schedule successfully'}, 200
        else:
            return {'message': 'Login failed'}, 401


@ns.route('/week/<string:date_string>')
@api.response(200, 'Successful')
@api.response(400, 'Bad request')
@api.doc(params={'date_string': 'A date string in the format dd_mm_yyyy'})
class Week(Resource):
    def get(self, date_string):
        schedule = get_week_schedule_json(date_string)
        if 404 in schedule:
            if 'username' in session and 'password' in session:
                username = session['username']
                password = session['password']
                driver = initialise_selenium()
                scraper = MyGesScraper(driver, username, password)
                login = scraper.login()

                if login:
                    schedule = scraper.get_schedule(to_json=False, to_mongo=True, to_Console=False,
                                                    startOfTheYear=False, endOfTheYear=False,
                                                    date_string=date_string)
                    driver.quit()
                    return schedule
        else:
            return schedule
