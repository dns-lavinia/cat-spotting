import firebase_admin
import pyrebase
import urllib

from firebase_admin import credentials, storage
from firebase_admin import firestore
from dotenv import load_dotenv
from datetime import datetime, timedelta
from os import getenv

# load the variables that keep credentials to connect to firebase
load_dotenv()

class Catbase:
    def __init__(self):
        # init the firebase configuration
        cred = credentials.Certificate(getenv("CERTIFICATE"))
        firebase_admin.initialize_app(cred, {
            'projectId': getenv('PROJECT_ID'),
            "storageBucket": getenv("STORAGE_BUCKET")
        })

        self.db = firestore.client()
        self.bucket = storage.bucket()

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


    def push_to_table(self, collection_name, data):
        if not collection_name:
            print('collection_name is invalid')
            return

        if not data:
            print('data is empty')
            return

        cat_doc = 'cat-' + str(datetime.utcnow())

        doc_ref = self.db.collection(collection_name).document(cat_doc)
        doc_ref.set(data)


    def store_img(self, img, img_name):
        """ Add to firebase storage an image

        Parameters
        ----------
            img should be a path to a cat image from storage
        """
        # build path to image to be added
        img_path = 'images/' + img_name

        blob = self.bucket.blob(img_path)
        blob.upload_from_filename(img)

    # def delete_from_table(self, table_name, data):

    def download_file(self , src_filename, dst_filename):
        cld_filename = self.cloud_filename + src_filename

        blob = self.bucket.blob(cld_filename)

        urllib.request.urlretrieve(blob.generate_signed_url(timedelta(seconds=300),
                                                            method='GET'), dst_filename)


    def len_for_table(self, collection_name, start_time=None, end_time=None):
        """ If start_time and end_time are given, return the number of entries
        only for the given time interval"""

        if not collection_name:
            print('collection_name is invalid')
            return

        if (start_time is not None) and (end_time is not None):
            ref = self.db.collection(collection_name)
            docs = ref.where('timestamp', '>=', start_time).where('timestamp', '<=', end_time)

            return len(docs.get())

        return len(list(self.db.collection(collection_name).get()))


    def query_interval(self, collection_name, start_time, end_time):
        if start_time is None:
            print('expected starting time for query')
            return

        if end_time is None:
            print('expected ending time for query')
            return

        ref = self.db.collection(collection_name)
        docs = ref.where('timestamp', '>=', start_time).where('timestamp', '<=', end_time).stream()

        return {doc.id: doc.to_dict() for doc in docs}

    # def get_img_from_storage():
