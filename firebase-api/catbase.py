import pyrebase
from os import getenv
from dotenv import load_dotenv
from datetime import datetime

# load the variables that keep credentials to connect to firebase
load_dotenv()

class Catbase:
    def __init__(self):
        # init the firebase configuration
        firebaseConfig = {
          "apiKey": getenv("API_KEY"),
          "authDomain": getenv("AUTH_DOMAIN"),
          "databaseURL": getenv("DATABASE_URL"),
          "projectId": getenv("PROJECT_ID"),
          "storageBucket": getenv("STORAGE_BUCKET"),
          "messagingSenderId": getenv("MESSAGING_SENDER_ID"),
          "appId": getenv("APP_ID")
        }

        self.firebase = pyrebase.initialize_app(firebaseConfig)
        self.fire_email = getenv("FIREBASE_EMAIL")
        self.fire_passw = getenv("FIREBASE_PASS")

    # This method will probably not be used
    def connect(self):
        auth = self.firebase.auth()

        try:
            auth.sign_in_with_email_and_password(self.fire_email, self.fire_passw)
            print("Signed in successfully")
        except:
            print("Invalid username or password")


    def push_to_table(self, table_name, data):
        if not table_name:
            print('table_name is invalid')
            return

        if not data:
            print('data is empty')
            return

        db = self.firebase.database()
        db.child(table_name).push(data)


    def store_img(self, img):
        """ Add to firebase storage an image

        Parameters
        ----------
            img should be a path to a cat image from storage
        """

        storage = self.firebase.storage()
        img_path = 'images/img' + str(datetime.utcnow()) + '.jpg'

        # build path to image to be added
        storage.child(img_path).put(img)

    # def query(self):
    # def delete_from_table(self, table_name, data)
    # def get_img_from_storage():
