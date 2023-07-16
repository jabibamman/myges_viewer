from flask import Flask, session
from flask_restx import Api, Resource
from scraper import initialise_selenium, MyGesScraper
from utils.directory_utils import get_teacher_directory_json, get_student_directory_json
from utils.schedule_utils import get_week_schedule_json
from utils.marks_utils import get_marks_json


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
@api.doc(params={'date_string': 'A date string in the format dd_mm_yy'})
class Week(Resource):
    def get(self, date_string):
        schedule = get_week_schedule_json(date_string)
        if 404 in schedule:
            if 'username' in session and 'password' in session:
                username = session['username']
                password = session['password']
                driver = initialise_selenium(headless=False)
                scraper = MyGesScraper(driver, username, password)
                login = scraper.login()

                if login:
                    schedule = scraper.get_schedule(to_json=False, to_mongo=True, to_Console=False,
                                                    startOfTheYear=True, endOfTheYear=False,
                                                    date_string=date_string)
                    driver.quit()
                    return schedule
        else:
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


@ns.route('/directory/student/year/<string:year>/promotion/<string:promotion>/semester/<string:semester>')
@api.response(200, 'Successful')
@api.response(400, 'Bad request')
@api.doc(params={'year': 'A year string, e.g. "1", "2", "3", "4", "5"',
                 'promotion': 'A promotion string, e.g. "AL", "AL2", "ESGI"',
                 'semester_string': 'A semester string "1" or "2"'})
class StudentDirectory(Resource):
    def get(self, year, promotion, semester):
        directory = get_student_directory_json(year, promotion, semester)
        if 404 not in directory:
            return directory

        if 'username' in session and 'password' in session:
            username = session['username']
            password = session['password']
            driver = initialise_selenium(headless=False)
            scraper = MyGesScraper(driver, username, password)
            login = scraper.login()

            if login:
                scraper.get_schedule()
                driver.quit()
                directory = get_student_directory_json(year, promotion, semester)
                return directory


@ns.route('/directory/teacher')
@api.response(200, 'Successful')
@api.response(400, 'Bad request')
class StudentDirectory(Resource):
    def get(self):
        directory = get_teacher_directory_json()
        if 404 not in directory:
            return directory

        if 'username' in session and 'password' in session:
            username = session['username']
            password = session['password']
            driver = initialise_selenium(headless=False)
            scraper = MyGesScraper(driver, username, password)
            login = scraper.login()

            if login:
                scraper.get_teachers_directory()
                driver.quit()
                directory = get_teacher_directory_json()
                return directory
