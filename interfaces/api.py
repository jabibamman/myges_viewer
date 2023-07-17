from datetime import datetime

from flask import Flask, session
from flask_restful import reqparse
from flask_restx import Api, Resource

from scraper import initialise_selenium, MyGesScraper
from utils.schedule_utils import get_week_schedule_json
from utils.marks_utils import get_marks_json

app = Flask(__name__)
api = Api(app)

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


@ns.route('/week/')
@api.response(200, 'Successful')
@api.response(400, 'Bad request')
@api.doc(params={
                    'date_string': 'A date string in the format dd_mm_yy',
                    'to_json': 'Output the schedule be in JSON format',
                    'to_Console': 'Output the schedule to the console',
})
class Week(Resource):
    parser = reqparse.RequestParser()  # Initialiser l'analyseur de requête
    parser.add_argument('to_json', type=bool, default=False, help='Output the schedule be in JSON format (boolean)')
    parser.add_argument('to_Console', type=bool, default=False, help='Output the schedule to the console (boolean)')
    parser.add_argument('date_string', type=str, default=None, help='A date string in the format dd_mm_yy (string)')


    def get(self):
        args = self.parser.parse_args()
        date_string = args.get('date_string')
        if date_string is not None:
            input_date = datetime.strptime(date_string, "%d_%m_%y").date()
            today = datetime.now().date()
            print(input_date, today)

            if input_date >= today:
                print("Date is in the future")
                schedule = {"error": "Date is in the future"}, 404
            else:
                print("Date is in the past")
                schedule = get_week_schedule_json(date_string)
        else:
            print("No date provided")
            schedule = get_week_schedule_json(date_string)

        if 404 in schedule:
            if 'username' in session and 'password' in session:
                username = session['username']
                password = session['password']
                driver = initialise_selenium(headless=False)
                scraper = MyGesScraper(driver, username, password)
                login = scraper.login()

                if login:
                    schedule = scraper.get_schedule(
                        to_json=args['to_json'],
                        to_Console=args['to_Console'],
                        startOfTheYear=False,
                        endOfTheYear=False,
                        date_string=args['date_string']
                    )
                    return schedule
            return schedule

@ns.route('/marks/year/<string:year_string>/semester/<string:semester_string>')
@api.response(200, 'Successful')
@api.response(400, 'Bad request')
@api.doc(params={'year_string': 'A year string in the format 2020-2021',
                 'semester_string': 'A semester string "1" or "2"'})
class Marks(Resource):
    def get(self, year_string, semester_string):
        marks = get_marks_json(year_string,semester_string)
        if 404 in marks:
            if 'username' in session and 'password' in session:
                username = session['username']
                password = session['password']
                driver = initialise_selenium()
                scraper = MyGesScraper(driver, username, password)
                login = scraper.login()

                if login:
                    marks = scraper.get_marks(year_string, semester_string)
                    driver.quit()
                    return marks
        else:
            return marks

