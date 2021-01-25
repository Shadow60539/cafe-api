from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://iyfbzhxzryhdne:90dff2c857a47d5136cba7c94dcab41662dab1b931cb28c97ebdab69df8eb7f5@ec2-52-54-174-5.compute-1.amazonaws.com:5432/del3ul7iohu30a'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


all_cafes_dict = {
    'cafes': []
}
for cafe in db.session.query(Cafe).all():
    local_dict = {
        "can_take_calls": cafe.can_take_calls,
        "coffee_price": cafe.coffee_price,
        "has_sockets": cafe.has_sockets,
        "has_toilet": cafe.has_toilet,
        "has_wifi": cafe.has_wifi,
        "id": cafe.id,
        "img_url": cafe.img_url,
        "location": cafe.location,
        "map_url": cafe.map_url,
        "name": cafe.name,
        "seats": cafe.seats
    }

    prev_list = all_cafes_dict['cafes']
    prev_list.append(local_dict)
    all_cafes_dict['cafes'] = prev_list


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/route", methods=["GET"])
def get_random_cafe():
    return "Hello"


@app.route("/all", methods=["GET"])
def get_all_cafes():
    return all_cafes_dict


@app.route('/search')
def search_cafe():
    result_cafes_dict = {}
    arg_location = request.args.get('loc')
    for cafe_dict in all_cafes_dict['cafes']:
        if cafe_dict['location'].lower() == arg_location.lower():
            result_cafes_dict['cafe'] = cafe_dict

    if result_cafes_dict == {}:
        return {
            'error': f'No cafes found in {arg_location}'
        }
    else:
        return result_cafes_dict


## HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return {
        'Result': 'Success'
    }


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=['PATCH'])
def update_cafe_price(cafe_id):
    new_price = request.args.get("coffee_price")
    selected_cafe = db.session.query(Cafe).get(cafe_id)
    if selected_cafe:
        selected_cafe.coffee_price = new_price
        db.session.commit()
        ## Just add the code after the jsonify method. 200 = Ok
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        # 404 = Resource not found
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})


## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        selected_cafe = db.session.query(Cafe).get(cafe_id)
        if selected_cafe:
            db.session.delete(selected_cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."})
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."})


if __name__ == '__main__':
    app.run(debug=True)
