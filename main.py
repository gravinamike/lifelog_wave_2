#!/usr/bin/env python


import os
import sys
import time
import datetime
import string
import Tkinter
import tkMessageBox
import smtplib
import logging

from ctypes import windll
from PIL import Image, ImageTk
from win32api import GetSystemMetrics

import settings
import transfer



def show_pics_in_subfolder(subfolder):
    # Displays images in subfolder in order, advancing upon user click.

    root = Tkinter.Tk()
    root.bind("<Button>", button_click_exit_mainloop)
    root.geometry('+%d+%d' % (100,100))
    subfolder_path = os.path.dirname(os.path.abspath(__file__)) + subfolder
    dirlist = os.listdir(subfolder_path)
    old_label_image = None

    for f in dirlist:
        try:
            image1 = Image.open(subfolder_path + f)
            root.geometry('%dx%d' % (image1.size[0],image1.size[1]))
            root.attributes('-fullscreen', True)
            tkpi = ImageTk.PhotoImage(image1)
            label_image = Tkinter.Label(root, image=tkpi)
            label_image.place(x=GetSystemMetrics(0)/2, y=GetSystemMetrics(1)/2, width=image1.size[0],
                              height=image1.size[1], anchor='center')
            root.title(f)
            if old_label_image is not None:
                old_label_image.destroy()
            old_label_image = label_image
            root.mainloop() # Wait until user clicks the window
        # This is used to skip anything not an image. Other exceptions will be logged passively.
        except Exception, e:
            logging.exception(str(Exception), str(e))

    root.destroy()

def button_click_exit_mainloop (event):
    # This method is necessary to advance images in the above method.
    event.widget.quit() # This will cause mainloop to unblock.

def get_drives():
    # Returns a list of the current drives (for checking if thumb drives were
    # plugged in correctly).
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1
    return drives

def send_email_report(text):
    # Sends an email report for logging purposes.

    # Setup
    username = 'lifelogging.osu@gmail.com'
    password = 'Con08Text'
    fromaddr = 'lifelogging.osu@gmail.com'
    toaddrs  = 'lifelogging.osu@gmail.com'
    msg = 'Subject: ' + settings.subject_id + ' ' + datetime.datetime.now().strftime("%Y%m%d %H%M") + ' log report\n\n' + text

    # Send the mail
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()





#------------------------------------------
if __name__ == "__main__":

    # Configure logging.
    home_folder = os.path.dirname(os.path.abspath(__file__))
    datetime_string = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    log_path = home_folder + '/logs/' + datetime_string + '_lifelogging.log'
    logging.basicConfig(filename=log_path, level=logging.DEBUG,
                        format='%(asctime)s %(message)s')

    # Initialize error list.
    error_list = []

    # Routine is based on whether it is morning or evening.
    am_or_pm = 'am' if datetime.datetime.now().hour < 12 else 'pm'
    am_or_pm = 'am'#####################################################################################################################
    logging.info(am_or_pm + ' operation')

    if am_or_pm == 'am':
        # Morning routine includes wearables setup and CogBat.

        # Instruct subject to prepare for CogBat.
        show_pics_in_subfolder('/pics_am_1/')

        print 'CogBat goes here' # PLACEHOLDER
        # CHECK COGBAT OUTPUT FOLDER FOR NEW FILES AND REPORT IF THEY ARE MISSING

        # Instruct subject in putting on wearables and reminders for day.
        show_pics_in_subfolder('/pics_am_2/')

    else:
        # Evening routine includes wearables breakdown, CogBat, and transfer.

        # Instruct subject in taking off and plugging in wearables.
        show_pics_in_subfolder('/pics_pm_1/')

        # Check for camera drives. If not found, prompt subject to re-insert
        # pendant until drives are found.
        drives = set(get_drives())
        while not ('D' in drives):
        #while not ('E' in drives and 'F' in drives):#########################################
            show_pics_in_subfolder('/pics_error/')
            logging.warning('Camera drives not found. Prompted for retry.')
            drives = set(get_drives())

        # Instruct subject to prepare for CogBat.
        show_pics_in_subfolder('/pics_pm_2/')

        print 'CogBat goes here' # PLACEHOLDER
        # CHECK COGBAT OUTPUT FOLDER FOR NEW FILES AND REPORT IF THEY ARE MISSING

        # Say goodnight!
        show_pics_in_subfolder('/pics_pm_3/')

        # Begin transfer of files from camera drives to data drive.
        try:
            transfer.transfer_stick(configuration=1)
        except:
            logging.warning('Data transfer from cameras failed.')
            error_list.append('Data transfer from cameras failed.')


    # Send email report based on log file.
    try:
        with open(log_path, 'r') as my_file:
            email_body=my_file.read().replace('\n', '')
        send_email_report(email_body)
    except:
        logging.warning('Email attempt failed. '
                        'Info saved to log but not emailed.')

    # Report any critical errors to the screen and alert subject to call us.
    if len(error_list):
        message = ("Some errors happened. Please get in contact with us at the "
                   "contact number written on the computer, and tell us what is"
                   " listed below. Thank you!")
        tkMessageBox.showerror("Errors!", message + "\n\n"
                               +'\n\n: '.join(error_list))


#------------------------------------------
