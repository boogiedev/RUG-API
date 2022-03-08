from flask import Flask

application = Flask(__name__)

@application.route('/')
def home():
    return 'suh dude'


if __name__ == '__main__':
    application.run(debug=True)
