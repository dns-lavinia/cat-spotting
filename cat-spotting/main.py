import numpy as np
import asyncio
import sys
import cv2

from datetime import datetime, timedelta
from dotenv import load_dotenv
from os import getenv
from PIL import Image

sys.path.append('../firebase-api/')

import catbase


def rgb_to_hexa(cat_colors):
    """rgb_to_hexa receives a list of colors in hexadecimal format and returns
    a list with r, g, b correspondent colors"""
    top_hex_colors = []

    if len(cat_colors) != 3:
        print('expected rgb format')
        return

    for r, g, b in cat_colors:
        top_hex_colors.append(('{:X}{:X}{:X}').format(r, g, b))

    return top_hex_colors


def get_env_stats():
    """This function will gather data from sensors and return a dict with all
    of the information"""
    return 25


def get_cat_colors():
    cat_img = Image.open(getenv("CAT_IMG_PATH"))

    # convert to web palete
    reduced_img = cat_img.convert("P", palette=Image.Palette.WEB)
    palette = reduced_img.getpalette()
    palette = [palette[3*n:3*n+3] for n in range(256)]

    top_cat_colors = [(n, palette[m]) for n,m in reduced_img.getcolors()]
    top_cat_colors.sort(key=lambda y: y[0], reverse=True)

    return top_cat_colors[:3]


async def spot_cats():
    """spot_cats will try to detect cat faces that are captured by the video
    stream.

    Additionally, it will yield a cat face image every time a cat is detected
    every x minutes. The x minutes time frame to send the data is employed as to
    not send a lot of spam to firebase"""

    # additionally, or optionally, the extended frontalcatface model can be used
    frontal_face_cascade = cv2.CascadeClassifier(getenv('FRONTAL_CATFACE_MODEL'))

    # make sure not to send more than one (set of) entry to the db every x mins
    time_later = datetime.utcnow()

    # get frames from camera
    cap = cv2.VideoCapture(0)

    while 1:
        # read frames from camera
        ret, img = cap.read()

        # to gray scale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # detect faces
        faces = frontal_face_cascade.detectMultiScale(gray, 1.3, 5)

        # draw a rectangle for detected faces
        for (x,y,w,h) in faces:
            # if two minutes since last push to db did not pass, break
            if datetime.utcnow() < time_later:
                break
            else:
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,0),2)
                roi_color = img[(y+2):y+h-2, (x+2):x+w-2]

                # reset time_later
                time_later = datetime.utcnow() + timedelta(minutes=2)

                yield img, roi_color

        # uncomment this for debugging
        cv2.imshow('img',img)

        # stop if esc was pressed
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


async def gather_send_data(fb, img, cat_face):
    """gather_send_data will upload the detected cat image alongside a few more
    information to firebase

    Parameters
    ----------
    fb
        Catbase object used to manipulate firebase data
    img
        uncropped image with a detected cat
    cat_face
        cropped image with a cat face in it

    Data to upload
    --------------
    - image of cat face
    - timestamp
    - cat colors
    - temperature for given location (default = Timisoara) or from sensor"""
    cat_img_path = getenv('CAT_IMG_PATH')
    uc_cat_path = getenv('UC_CAT_IMG_PATH')

    # write cat picture
    cv2.imwrite(cat_img_path, cat_face)

    # write uncropped cat picture
    cv2.imwrite(uc_cat_path, img)

    # timestamp
    time_now = datetime.utcnow()

    # cat colors
    cat_colors = [y for (x,y) in get_cat_colors()]

    # temperature
    temp = get_env_stats()

    # create the name of image file to be stored on firebase
    img_filename = 'img' + str(time_now) + '.jpg'

    data = {
        'timestamp': time_now,
        'cat_colors': rgb_to_hexa(cat_colors),
        'temperature': temp,
        'img_filename': img_filename
    }

    # upload to firebase
    # upload the image
    fb.store_img(uc_cat_path, img_filename)

    # upload data to instants table
    fb.push_to_table(getenv('INSTANTS_TABLE'), data)


async def main():
    # load the variable from .env
    load_dotenv()

    fb = catbase.Catbase()

    async for img, cat_img in spot_cats():
        await gather_send_data(fb, img, cat_img)


if __name__ == "__main__":
    asyncio.run(main())
