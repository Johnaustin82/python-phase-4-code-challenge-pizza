#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify, abort
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)


class RestaurantListResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants])


class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get_or_404(id)
        return jsonify(restaurant.to_dict(only=('id', 'name', 'address', 'restaurant_pizzas')))

    def delete(self, id):
        restaurant = Restaurant.query.get_or_404(id)
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204


class PizzaListResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas])


class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return jsonify(new_restaurant_pizza.to_dict()), 201
        except Exception as e:
            return jsonify({"errors": [str(e)]}), 400


api.add_resource(RestaurantListResource, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:id>')
api.add_resource(PizzaListResource, '/pizzas')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')


@app.route('/')
def index():
    return "<h1>Code challenge</h1>"


if __name__ == "__main__":
    app.run(port=5555, debug=True)
