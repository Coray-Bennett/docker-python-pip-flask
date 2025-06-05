import unittest, json
from app import app
from model.bird_data import BirdData, from_request_form, db
from model.bird_group import BirdGroup, GroupCategory, BirdGroupEntry

class BirdDataTestCase(unittest.TestCase):
    bird_list = [
       {"name_common": "Bird 1", "name_scientific": "S Bird 1", "images": ["S1.png", "S1alt.jpg"], "audio": ["S1.wav"]},
       {"name_common": "Bird 2", "name_scientific": "S Bird 2", "images": ["S2.png"], "audio": ["S2.wav", "S2-cry.wav"]},
       {"name_common": "Bird 3", "name_scientific": "S Bird 3", "images": [], "audio": ["S3.wav"]},
       {"name_common": "Bird 4", "name_scientific": "S Bird 4", "images": [], "audio": []},
       {"name_common": "Bird 5", "name_scientific": "S Bird 5", "images": ["image.png", "image2.png", "image3.png"], "audio": ["S5.wavv"]}
    ]

    def setUp(self):
        # Configure the app for testing
        app.config['TESTING'] = True
        # Use an in-memory SQLite database for tests
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        # Create the test client
        self.app = app.test_client()
        # Push the application context and create all tables
        self.ctx = app.app_context()
        self.ctx.push()
        
        try:
            db.init_app(app)
        except RuntimeError:
            ...

        db.create_all()
        for bird in self.bird_list:
            from_request_form(bird)

        db.session.add(BirdGroup(name="Test Group", category=GroupCategory.BEHAVIOR, description="test group"))
        db.session.commit()

    def tearDown(self):
        # Cleanup the database and remove the app context
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
    
    def test_from_request_form(self):
        request_form = {
            "name_common": "American Crow",
            "name_scientific": "Corvus brachyrhynchos",
            "images": ["https://fake_image_url.com/crow.png"],
            "audio": ["https://fake_audio_url.com/crow.wav", "https://fake_audio_url.com/crow2.wav"]
        }

        data = from_request_form(request_form)
        self.assertIsNotNone(data)
        self.assertEqual(data.name_common, request_form["name_common"])
        self.assertEqual(data.name_scientific, request_form["name_scientific"])
        
        self.assertEqual(len(data.images), 1)
        self.assertEqual(data.images[0].image_url, "https://fake_image_url.com/crow.png")
        
        self.assertEqual(len(data.audio), 2)
        audio_urls = [audio.audio_url for audio in data.audio]
        self.assertIn("https://fake_audio_url.com/crow.wav", audio_urls)
        self.assertIn("https://fake_audio_url.com/crow2.wav", audio_urls)

        db_data = BirdData.query.filter_by(name_common="American Crow").first()
        self.assertIsNotNone(db_data)

    def test_from_request_form_missing_key(self):
        request_form = {
            "name_scientific": "Corvus brachyrhynchos",
            "images": ["https://fake_image_url.com/crow.png"],
            "audio": ["https://fake_audio_url.com/crow.wav", "https://fake_audio_url.com/crow2.wav"]
        }

        data = from_request_form(request_form)
        self.assertIsNone(data)

    # Bird Data Creation Tests
    def test_create(self):
        request_data = {
            "name_common": "American Crow",
            "name_scientific": "Corvus brachyrhynchos",
            "images": ["https://fake_image_url.com/crow.png"],
            "audio": ["https://fake_audio_url.com/crow.wav", "https://fake_audio_url.com/crow2.wav"]
        }
        response = self.app.post("/create", data=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name_common"], "American Crow")

    def test_create_existing_name_common(self):
        request_data = {
            "name_common": "Bird 1",
            "name_scientific": "Corvus brachyrhynchos",
            "images": ["https://fake_image_url.com/crow.png"],
            "audio": ["https://fake_audio_url.com/crow.wav", "https://fake_audio_url.com/crow2.wav"]
        }
        response = self.app.post("/create", data=request_data)
        self.assertEqual(response.status_code, 409)

    def test_create_existing_name_scientific(self):
        request_data = {
            "name_common": "American Crow",
            "name_scientific": "S Bird 1",
            "images": ["https://fake_image_url.com/crow.png"],
            "audio": ["https://fake_audio_url.com/crow.wav", "https://fake_audio_url.com/crow2.wav"]
        }
        response = self.app.post("/create", data=request_data)
        self.assertEqual(response.status_code, 409)

    def test_bird_data_upload(self):
        request_data = [
            {
                "name_common": "American Crow",
                "name_scientific": "Corvus brachyrhynchos",
                "images": ["https://fake_image_url.com/crow.png"],
                "audio": ["https://fake_audio_url.com/crow.wav", "https://fake_audio_url.com/crow2.wav"]
            },
            {
                "name_common": "Common Grackle",
                "name_scientific": "Quiscalus quiscula",
                "images": ["https://fake_image_url.com/grackle.png", "https://fake_image_url.com/grackle2.png"],
                "audio": ["https://fake_audio_url.com/grackle.wav"]
            },
        ]
        response = self.app.post("/bird-data-upload", data=request_data)
        self.assertEqual(response.status_code, 200)

        crow_data = BirdData.query.filter_by(name_common="American Crow").first()
        self.assertIsNotNone(crow_data)

        grackle_data = BirdData.query.filter_by(name_common="Common Grackle").first()
        self.assertIsNotNone(grackle_data)

    # GET Bird Data Tests
    def test_get_all(self):
        response = self.app.get("/get-all")
        data = json.loads(response.json)
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), 5)
    
    def test_get_random(self):
        response = self.app.get("/get-random")
        self.assertIsNotNone(response.json["name_common"])

        db_data = BirdData.query.filter_by(name_common=response.json["name_common"]).first()
        self.assertIsNotNone(db_data)

    # Group Tests
    def test_create_group(self):
        request_data = {
            "name": "Favorite Birds",
            "category": "other",
            "description": "This is a collection of the creator's personal favorite birds!"
        }
        response = self.app.post("/create-group", data=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json["name"])

        db_data = BirdGroup.query.filter_by(name=response.json["name"]).first()
        self.assertIsNotNone(db_data)

    def test_add_to_group(self):
        request_data = {
            "group_name": "Test Group",
            "bird_names": ["Bird 1", "S Bird 2"]
        }
        response = self.app.post("/add-to-group", data=request_data)
        self.assertEqual(response.status_code, 200)
        
        db_group = BirdGroup.query.filter_by(name="Test Group").first()
        db_data = BirdGroupEntry.query.filter_by(bird_group_id=db_group.id).all()

        self.assertEqual(len(db_data), 2)

    def test_add_to_group_invalid_bird(self):
        request_data = {
            "group_name": "Test Group",
            "bird_names": ["Bird 1", "Bird Does Not Exist"]
        }
        response = self.app.post("/add-to-group", data=request_data)
        self.assertEqual(response.status_code, 200)
        
        db_group = BirdGroup.query.filter_by(name="Test Group").first()
        db_data = BirdGroupEntry.query.filter_by(bird_group_id=db_group.id).all()

        self.assertEqual(len(db_data), 1)

    def test_get_group(self):
        request_data = {"group_name": "Test Group"}
        response = self.app.get("/get-group", data=request_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["description"], "test group")
        self.assertEqual(response.json["category"], "behavior")

if __name__ == "__main__":
    unittest.main()