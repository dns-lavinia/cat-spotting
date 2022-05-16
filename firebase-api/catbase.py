import pyrebase

from dotenv import load_dotenv
from datetime import datetime
from os import getenv

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
        self.storage = self.firebase.storage()
        self.db = self.firebase.database()

        self.cloud_filename = getenv("CLOUD_FILENAME")
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

        self.db.child(table_name).push(data)


    def store_img(self, img, img_name):
        """ Add to firebase storage an image

        Parameters
        ----------
            img should be a path to a cat image from storage
        """

        img_path = 'images/' + img_name

        # build path to image to be added
        self.storage.child(img_path).put(img)

    # def delete_from_table(self, table_name, data):

    def download_file(self , src_filename, dst_filename):
        cld_filename = self.cloud_filename + src_filename

        self.storage.child(cld_filename).download(src_filename, dst_filename)


    def len_for_table(self, table_name, start_time=None, end_time=None):
        """ If start_time and end_time are given, return the number of entries
        only for the given time interval"""

        if not table_name:
            print('table_name is invalid')
            return

        if (start_time is not None) and (end_time is not None):
            rows = self.db.child(table_name).get()
            r_count = 0

            for r in rows.each():
                r_time = datetime.strptime(r.val()['timestamp'], '%Y-%m-%d %H:%M:%S.%f')

                if start_time < r_time < end_time:
                    r_count += 1

            return r_count

        return len(self.db.child(table_name).get().val())

    # def query(self):
    # def get_img_from_storage():
