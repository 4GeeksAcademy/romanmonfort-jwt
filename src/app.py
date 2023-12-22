"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_migrate import Migrate
from flask_swagger import swagger
from api.utils import APIException, generate_sitemap
from api.models import db,User
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
# from models import Person

ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
static_file_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '../public/')
app = Flask(__name__)
app.url_map.strict_slashes = False


app.config["JWT_SECRET_KEY"] = "super-lafamilia"  # Change this!
jwt = JWTManager(app)

bcrypt = Bcrypt(app)
# database condiguration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)

# add the admin
setup_admin(app)

# add the admin
setup_commands(app)

# Add all endpoints form the API with a "api" prefix
app.register_blueprint(api, url_prefix='/api')

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# any other endpoint will try to serve it like a static file


@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0  # avoid cache memory
    return response


@app.route('/login',methos=['POST'])
def login():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg':'Debes enviar informacion en el body'}),400
    if 'email'not in body:
        return jsonify({'msg':'El campo email es obligatorio'}),400
    if 'password'not in body:
        return jsonify({'msg':'El campo password es necesario'}),400
    user = User.query.filter_by(email=body['email']).first()
    if user is None:
        return jsonify({'msg':'usuario o password incorrecto'}),400
    check_password = bcrypt.check_password_hash(user.password, body['password']) # returns True
    if not check_password:
        return jsonify({'msg':'Usuario o password incorrecto'}),400
    access_token = create_access_token(identity=user.email)
    return jsonify({'msg':'ok','token':access_token})


@app('/register', methods=['POST'])
def register():
    body = request.get_json(silent=True)
    if body is None:
       return jsonify({'msg':'Debes enviar informacion en el body'})
    if 'email' not in body:
        return jsonify({'msg':'el campo Email es obligatorio'})
    if 'password'not in body:
        return jsonify({'msg':'el campo password es obligatorio'})
    user = User()
    user.email = body['email']
    pw_hash = bcrypt.generate_password_hash(body['password'])
    user.password = pw_hash
    user.is_active= True
    db.session.add(user)
    db.session.commit()
    return jsonify ({'msg':'ok'}),200





@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify({'msg':'ok','user': current_user}), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
