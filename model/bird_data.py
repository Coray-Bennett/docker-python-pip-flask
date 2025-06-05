from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class BirdData(db.Model):
    __tablename__ = 'bird_data'
    id = db.Column(db.Integer, primary_key=True)
    name_common = db.Column(db.String(100))
    name_scientific = db.Column(db.String(100))
    images = db.relationship('BirdImage', backref='bird_data')
    audio = db.relationship('BirdAudio', backref='bird_data')

class BirdImage(db.Model):
    __tablename__ = 'bird_image'
    id = db.Column(db.Integer, primary_key=True)
    bird_data_id = db.Column(db.Integer, db.ForeignKey('bird_data.id'))
    image_url = db.Column(db.String(200))

class BirdAudio(db.Model):
    __tablename__ = 'bird_audio'
    id = db.Column(db.Integer, primary_key=True)
    bird_data_id = db.Column(db.Integer, db.ForeignKey('bird_data.id'))
    audio_url = db.Column(db.String(200))


def from_request_form(request_form) -> BirdData | None:
    """Create a BirdData instance from an HTTP request form.

    request_form -- ImmutableMultiDict[str, str], the raw request form from the HTTP request.
    """
    common = request_form.get("name_common")
    scientific = request_form.get("name_scientific")
    bird_images = request_form.get("images")
    bird_audio = request_form.get("audio")

    if(common == None or scientific == None):
        return None
    
    new_bird_data = BirdData(
        name_common=common, 
        name_scientific=scientific
    )

    db.session.add(new_bird_data)
    db.session.flush()

    if bird_images:
        image_urls = bird_images if isinstance(bird_images, list) else [bird_images]
        for image_url in image_urls:
            image_obj = BirdImage(bird_data_id=new_bird_data.id, image_url=image_url)
            db.session.add(image_obj)

    if bird_audio:
        audio_urls = bird_audio if isinstance(bird_audio, list) else [bird_audio]
        for audio_url in audio_urls:
            audio_obj = BirdAudio(bird_data_id=new_bird_data.id, audio_url=audio_url)
            db.session.add(audio_obj)

    db.session.commit()
    return new_bird_data