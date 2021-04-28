from selenium import webdriver
import time
from config import *
import cv2
import requests
import json
import shutil
import os
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.discovery import build
import io

class OcrOtomation():

    def __init__(self):
        self.executable_path = r"C:\Users\binbi\PycharmProjects\OcrOtomation\chromedriver.exe"
        self.ocr_url = "https://www.onlineocr.net/"
        self.images_dir = r"C:\Users\binbi\PycharmProjects\OcrOtomation\Images"
        self.thresholded_images_dir = r"C:\Users\binbi\PycharmProjects\OcrOtomation\ThresholdedImages"
        self.text_converted_dir = r"C:\Users\binbi\PycharmProjects\OcrOtomation\TextConverted"
        self.text_converted_gdrive_dir = r"C:\Users\binbi\PycharmProjects\OcrOtomation\TextConvertedGdrive"

    def get_logged_in(self):
        self.browser = webdriver.Chrome(executable_path=self.executable_path)
        login_page = r"https://www.onlineocr.net/account/login"
        self.browser.get(login_page)
        mail_adress = self.browser.find_element_by_xpath('//*[@id="MainContent_txtUserName"]').send_keys(ocr_mail_adress)
        password = self.browser.find_element_by_xpath('//*[@id="MainContent_txtPassword"]').send_keys(ocr_mail_password)
        get_logged_in_button = self.browser.find_element_by_xpath('//*[@id="MainContent_btnLogin"]').click()
        time.sleep(1)

    def recognize(self,file_url):
        img = cv2.imread(file_url)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        adaptive_threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 81, 11)
        save_path = os.path.join(self.thresholded_images_dir,file_url)
        cv2.imwrite(save_path,adaptive_threshold)
        return save_path

    def get_request(self,thresholded_file_path,which_account=1):

        request_url = "http://www.ocrwebservice.com/restservices/processDocument?language=turkish&outputformat=docx"
        file_absolute_path = thresholded_file_path
        with open(file_absolute_path, "rb") as image_file:
            image_data = image_file.read()
        if which_account == 1:
            posted_request = requests.post(request_url,data=image_data,auth=(ocr_username,ocr_licence_code))
        else:
            posted_request = requests.post(request_url, data=image_data, auth=(ocr_username2, ocr_licence_code2))

        if posted_request.status_code == 401:
            print("Unauthorizded user informations")

        else:
            response = json.loads(posted_request.content)
            file_response = requests.get(response["OutputFileUrl"], stream=True)
            filename_without_jpg =  thresholded_file_path.split("\\")[-1].replace(".jpeg","")
            save_path = f"{os.path.join(self.text_converted_dir, filename_without_jpg)}.docx"
            with open(save_path, 'wb') as output_file:
                shutil.copyfileobj(file_response.raw, output_file)
                print("Dosya docx formatına başarıyla dönüştürüldü.")

    def path_images(self,return_file_names=False):
        paths = [os.path.join(self.images_dir,name) for name in os.listdir(self.images_dir)]
        if return_file_names:
            file_names = [file_name.replace(".jpeg","").replace(".jpg","") for file_name in os.listdir(self.images_dir)]
            paths_and_names = zip(paths,file_names)
            return paths_and_names
        else:
            return paths

    def upload_file_to_gdrive(self,file_name,file_path):
        SCOPES = ['https://www.googleapis.com/auth/drive']

        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            service = build("drive", "v3", credentials=creds)
            mime = "image/jpeg"
            file_metadata = {"name":file_name,"mimeType": "application/vnd.google-apps.document"}
            media = MediaFileUpload(file_path,mimetype= mime)
            file = service.files().create(
                body=file_metadata,
                media_body= media,
                fields = "id").execute()

            file_id = file.get("id")

            return file_id

    def download_file_from_gdrive(self,file_id,file_name):
        SCOPES = ['https://www.googleapis.com/auth/drive']

        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            service = build("drive", "v3", credentials=creds)
            mime = "application/pdf"
            request = service.files().export_media(fileId = file_id, mimeType= mime)
            file_name = os.path.join(self.text_converted_gdrive_dir,file_name + ".pdf")
            fh = io.FileIO(file_name, 'wb')

            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))

    def run(self,google_drive=True):
        file_ids = []
        for path,file_name in self.path_images(return_file_names=True):
            recognized_path = self.recognize(path)

            # try:
            #     self.get_request(recognized_path)
            # except Exception:
            #     self.get_request(recognized_path,which_account=2)

            if google_drive:
                file_id = self.upload_file_to_gdrive(file_path=path,file_name=file_name)
                self.download_file_from_gdrive(file_id=file_id,file_name=file_name)


if __name__ == "__main__":
    ocr = OcrOtomation()
    ocr.run()
