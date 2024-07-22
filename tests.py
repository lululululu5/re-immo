import unittest
from app import create_app, db
from app.models import User
from config import Config

class TestConfig(Config):
    Testing=True
    SQLALCHEMY_DATABASE_URI = "sqlite://"

class UserModelCase(unittest.TestCase):
    def setUp(self): 
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_password_hashing(self):
        u = User(name="susan", email="susan@mail.com")
        u.set_password("cat")
        self.assertFalse(u.check_password("dog"))
        self.assertTrue(u.check_password("cat"))
        
    def test_user_generation(self):
        pass
    
    def test_user_deletion(self):
        pass
    
    def test_building_creation(self):
        pass
    
    def test_building_update(self):
        pass
    
    def test_building_deletion(self):
        pass
        
if __name__ == "__main__":
    unittest.main(verbosity=2)
    
