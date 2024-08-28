from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by('created_at').all()

        response = make_response(
            jsonify([message.to_dict() for message in messages]),
            200,
        )
    elif request.method == 'POST':
        data = request.get_json()
        #structure of our message
        message = Message(
            body= data['body'],
            username= data['username']
        )

        db.session.add(message)
        db.session.commit()

        response = make_response(
            jsonify(message.to_dict()),
            201,
        )

    return response

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    # Retrieve the message from the db
    message = Message.query.filter_by(id=id).first()

    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    # Handle the PATCH method
    if request.method == 'PATCH':
        data = request.get_json()
        # Loop to iterate over the key values
        for attr in data:
            setattr(message, attr, data[attr])

        # Add message to the db
        db.session.add(message)
        db.session.commit() 

        response = make_response(
            jsonify(message.to_dict()),
            200,
        )

    elif request.method == 'DELETE':
        # Ensure we delete it in the db
        db.session.delete(message)
        db.session.commit()

        # Return a response indicating successful deletion
        response = make_response('', 204)

    return response

if __name__ == '__main__':
    app.run(port=5000)
