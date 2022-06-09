from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

# Import kivy UX components
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label

# Import other kivy stuff
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.config import Config

import mysql.connector
import cv2
import os
import face_recognition
import datetime
import playsound

class CamApp(App):

    def build(self):
        # Main layout components
        self.web_cam = Image(size_hint=(1, .7))
        self.button = Button(text="Xác minh", on_press=self.recognition, size_hint=(1, .15))
        self.verification_label = Label(text="", size_hint=(1, .15))

        # Add items to layout
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.web_cam)
        layout.add_widget(self.button)
        layout.add_widget(self.verification_label)

        # Setup video capture device
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 33.0)

        return layout

    def update(self, *args):
        # Read frame from opencv
        ret, frame = self.capture.read()
        frame = frame[120:120 + 250, 200:200 + 250, :]

        # Flip horizontall and convert image to texture
        buf = cv2.flip(frame, 0).tostring()
        img_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        img_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.web_cam.texture = img_texture

    def insertDate(self, id, date):
        conn = mysql.connector.connect(
            host="localhost", user="root",
            password="", database="web-gymphp")

        cursor = conn.cursor()

        query = "Select * from host_quanlynguoidung Where ID= " + str(id)

        cursor.execute(query)

        isRecordExist = 0

        for row in cursor:
            isRecordExist = 1

        if (isRecordExist == 0):
            query = "Insert into host_quanlynguoidung(Date_of_issue) values(" + str(date) + "')"
        else:
            query = "Update host_quanlynguoidung Set Date_of_issue= '" + str(date) + "' Where ID= " + str(id)

        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()

    def getProfile(self, id):
        conn = mysql.connector.connect(
            host="localhost", user="root",
            password="", database="web-gymphp")

        cursor = conn.cursor()

        query = "Select * from host_quanlynguoidung Where ID= " + str(id)

        cursor.execute(query)

        profile = None
        for row in cursor:
            profile = row
        cursor.close()
        conn.close()
        return profile

    def getDate(self):
        date = datetime.datetime.now().date()
        return date

    def verification(self, frame):
        cv2.imwrite(os.path.join('input_image', 'input_image.jpg'), frame)
        img = face_recognition.load_image_file("input_image/input_image.jpg")
        face_locations = face_recognition.face_locations(img)
        if (face_locations == []):
            print("Hãy để toàn bộ gương mặt vào máy ảnh")
            playsound.playsound("voice/4.mp3")
            return None
        picture_of_me = face_recognition.load_image_file("input_image/input_image.jpg")
        my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]
        list = os.listdir('verification_image')
        number_files = 0
        for image in os.listdir(os.path.join('verification_image')):
            unknown_picture = face_recognition.load_image_file("verification_image/" + image)
            unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]
            results = face_recognition.compare_faces([my_face_encoding], unknown_face_encoding)
            number_files += 1
            if number_files > len(list):
                return None
            if results[0] == True:
                return image.strip('User..jpg')

    def check_expiry(self, id):
        profile = self.getProfile(id)
        date = datetime.date(int(profile[6][0:4]), int(profile[6][5:7]), int(profile[6][8:10]))
        if (self.getDate() <= date):
            self.verification_label.text = profile[1] + " Còn thời hạn"
            playsound.playsound("voice/1.mp3")

        else:
            self.verification_label.text = profile[1] + " Đã hết hạn"
            playsound.playsound("voice/2.mp3")

    def recognition(self, *args):
        ret, frame = self.capture.read()
        frame = frame[120:120 + 250, 200:200 + 250, :]
        id = self.verification(frame)
        if (id == None):
            self.verification_label.text = "Không thể nhận diện gương mặt"
            playsound.playsound("voice/3.mp3")
        else:
            # print(id)
            self.check_expiry(id)
        
if __name__ == '__main__':
    Config.set('graphics', 'width', '250')
    Config.set('graphics', 'height', '350')
    Config.write()
    CamApp().run()