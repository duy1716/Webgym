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
import playsound


class CamApp(App):

    def build(self):
        # Main layout components
        self.web_cam = Image(size_hint=(1, .7))
        self.button = Button(text="Chụp ảnh", on_press=self.take_photo, size_hint=(1, .15))
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

    def insertOrUpdate(self, id):
        conn = mysql.connector.connect(
            host="localhost", user="root",
            password="", database="web-gymphp")

        cursor = conn.cursor()

        query = "Select * from host_quanlynguoidung Where ID= " + str(0)

        cursor.execute(query)

        isRecordExist = 0

        for row in cursor:
            isRecordExist = 1

        if (isRecordExist == 0):
            query = "Insert into host_quanlynguoidung(ID) values(" + str(id) + "')"
        else:
            query = "Update host_quanlynguoidung Set ID = '" + str(id) + "' Where ID= " + str(0)

        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()

    def generate_id(self):
        conn = mysql.connector.connect(
            host="localhost", user="root",
            password="", database="web-gymphp")

        cursor = conn.cursor()

        query = "Select * from host_quanlynguoidung "

        cursor.execute(query)

        max = 0

        for row in cursor:
            if (row[0] > max):
                max = row[0]
        cursor.close()
        conn.close()
        return max + 1

    def check(self, frame):
        cv2.imwrite(os.path.join('input_image', 'input_image.jpg'), frame)
        img = face_recognition.load_image_file("input_image/input_image.jpg")
        face_locations = face_recognition.face_locations(img)
        if (face_locations == []):
            return False
        else:
            return True     

    def close_application(self):
        App.get_running_app().stop()
        Window.close()

    def take_photo(self, *args):
        sampleNum = 0
        ret, frame = self.capture.read()
        frame = frame[120:120 + 250, 200:200 + 250, :]
        self.verification_label.text = 'Chưa thể lấy dữ liệu' if self.check(frame) == False else ''
        if self.check(frame) == False:
            playsound.playsound("voice/4.mp3")
            sampleNum = 0
        else:
            id = self.generate_id()
            self.insertOrUpdate(id)
            cv2.imwrite('verification_image/User.' + str(id) + '.jpg', frame)
            playsound.playsound("voice/5.mp3")
            sampleNum += 1
        if (sampleNum == 1):
            self.close_application()

if __name__ == '__main__':
    Config.set('graphics', 'width', '250')
    Config.set('graphics', 'height', '350')
    Config.write()
    CamApp().run()