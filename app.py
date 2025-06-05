from flask import Flask, request, Response, jsonify
from model.bird_data import db, from_request_form, BirdData

app = Flask(__name__)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route("/")
def check():
    return Response(status=200)

@app.route("/create", methods=["POST"])
def create():
    new_bird_data = from_request_form(request.form)

    if new_bird_data == None:
        return Response(status=400)
    
    # Build response JSON
    images = []
    if new_bird_data.images:
        for image in new_bird_data.images:
            images.append(image.image_url)

    audio = []
    if new_bird_data.audio:
        for clip in new_bird_data.audio:
            audio.append(clip.audio_url)

    return jsonify({
            "id": new_bird_data.id,
            "name_common": new_bird_data.name_common,
            "name_scientific": new_bird_data.name_scientific,
            "images": images,
            "audio": audio
        })

@app.route("/bird-data-upload", methods=["POST"])
def bird_data_upload():
    # TODO: implement, create multiple bird data entries from a single JSON file
    raise NotImplementedError
    
@app.route("/get-all", methods=["GET"])
def get_all():
    # TODO: implement, get all birds from database
    raise NotImplementedError

@app.route("/get-random", methods=["GET"])
def get_random():
    # TODO: implement, get a random bird from database
    raise NotImplementedError

@app.route("/create-group", methods=["POST"])
def create_group():
    # TODO: implement, creates a new bird group
    raise NotImplementedError

@app.route("/add-to-group", methods=["POST"])
def add_to_group():
    # TODO: implement, add one or multiple birds to a group given a list of names
    raise NotImplementedError

@app.route("/get-group", methods=["GET"])
def get_group():
    # TODO: implement, get group by name
    raise NotImplementedError

@app.cli.command("init_db")
def init_db():
    """Initialize the database."""
    db.init_app(app)
    db.create_all()
    print("Initialized the database.")

if __name__ == "__main__":
    app.run(debug=True)
