"""

#AUTHORS
*** Moses Olafenwa
*** John Olafenwa
>> January, 2018

#NOTES
Please remember to replace the string "PROGRAM_INSTALL_FULLPATH" with the full path
of your program install folder in every instance that it is used in the code below.
You may use relative purpose for debugging, but please note that you should keep and
maintain an absolute path for the "model_path" and "index_file_path" as once a picture
is selected in the UI for prediction, the program execution folder will migrate
to the folder of the selected picture, making the model file and index file
unreadable by the program.

"""

# Import WxPython, os and Thread classes
import wx
import wx.adv
from wx.lib.wordwrap import wordwrap
import os
from wx.lib.pubsub import pub, setupkwargs
import threading






# Function to initiate image prediction in a separate thread and accepts the image path, as sent from the dialog
class actionThreadDenseNet(threading.Thread):
    def __init__(self, path, model_path, index_file_path, main_ui):
        threading.Thread.__init__(self)
        self.path = path
        self.model_path = model_path
        self.main_ui = main_ui
        self.index_file_path = index_file_path


    def run(self):
        wx.CallAfter(pub.sendMessage, "report101",
                     message="Prediction process started. \nLoading........")  # Sending report to the Text Box
        import DensenetPrediction
        result = DensenetPrediction.predict(self.path, self.model_path, self.index_file_path, self.main_ui) # This calls the DenseNet Prediction Class
        wx.CallAfter(pub.sendMessage, "report101", message=result) # A call to update the report Text Box after image recognition



class Mainapp(wx.Frame):


    def __init__(self, parent):
        super(Mainapp, self).__init__(parent)

        self.densenet_model_loaded = False  # Value to make checks, as the image prediction Model should loaded only once
        self.model_collection_densenet = []  # An Array to hold the Loaded model for use for subsequent calls for image prediction
        self.magic_collection = []  # A collection to hold the containing UI objects and its children

        pub.subscribe(self.reportPrediction, "report101" ) # Subscribe the function to the call coming from the thread

        # Set the User interface properties
        self.Action()
        self.SetBackgroundColour("green")
        self.SetSize((1000,600))
        self.SetTitle("DenseNet Playground")

        icon =  wx.Icon("PROGRAM_INSTALL_FULLPATH\\playground.png")
        self.SetIcon(icon)

        self.Centre()
        self.Show()





    def Action(self):


        # Set a background for the UI
        ui_bitmap = wx.Image("PROGRAM_INSTALL_FULLPATH\\background.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.under = wx.StaticBitmap(self, -1, ui_bitmap, (0, 0))

        # Image Banner
        banner_bitmap1 = wx.Bitmap("PROGRAM_INSTALL_FULLPATH\\DenseNet.png")
        banner_image1 = banner_bitmap1.ConvertToImage()
        banner_image1 = banner_image1.Scale(285, 200, wx.IMAGE_QUALITY_HIGH)
        banner_bitmap2 = banner_image1.ConvertToBitmap()
        ui_banner_bitmap = wx.StaticBitmap(self, -1, banner_bitmap2 ,(0,2) )





        # The Left menu below the banner, which contains the File dialog button, report text box and about button
        left_menu = wx.StaticBox(self.under, -1, "" )
        left_menu.SetSize((285,370))
        left_menu.SetPosition((0,200))
        left_menu.SetBackgroundColour(wx.WHITE)


        # The right region to display the picture selected from the dialog.
        right_region = wx.StaticBox(self, -1, "Picture")
        right_region.SetSize((650,510))
        right_region.SetBackgroundColour(wx.WHITE)
        right_region.SetPosition((300, 10))
        self.magic_collection.append(right_region) # Adding the right region object to the UI object array

        # The report text box, to report prediction results
        report_box = wx.TextCtrl(left_menu, -1, "1. Click the Button Above \n \n"
                                                   "2.Select your picture. \n \n"
                                                   "3. Wait till the Program studies the picture and display the result here",
                                  size= (285, 200), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER, pos=(5, 80) )
        font = wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        report_box.SetFont(font)

        self.magic_collection.append(report_box) # Adding the report text box to the UI objects array


        # A Sample picture in the right region
        modification_bitmap1 = wx.Bitmap("PROGRAM_INSTALL_FULLPATH\\sample.jpg")
        modification_image1 = modification_bitmap1.ConvertToImage()
        modification_image1 = modification_image1.Scale(650, 490, wx.IMAGE_QUALITY_HIGH)
        modification_bitmap2 = modification_image1.ConvertToBitmap()
        report_bitmap = wx.StaticBitmap(right_region, -1, modification_bitmap2, (0, 20) )
        self.magic_collection.append(report_bitmap)

        # Text label
        image_dialog_label = wx.StaticText(left_menu, -1, "Select Picture")
        image_dialog_label.SetPosition((20, 20))
        image_dialog_label.SetForegroundColour(wx.BLUE)
        image_dialog_label.SetBackgroundColour(wx.WHITE)

        # The button to call the file dialog function
        dialog_button = wx.Button(left_menu, -1, "Click to Select")
        dialog_button.SetPosition((20, 40))
        dialog_button.SetSize((120, 30))
        dialog_button_bitmap = wx.Bitmap("PROGRAM_INSTALL_FULLPATH\\select-file.png")
        dialog_button_bitmap_pressed = wx.Bitmap("PROGRAM_INSTALL_FULLPATH\\select-file-hover.png")
        dialog_button.SetBitmap(dialog_button_bitmap, wx.LEFT)
        dialog_button.SetBitmapPressed(dialog_button_bitmap_pressed)
        self.Bind(wx.EVT_BUTTON, self.launchFileDialog, dialog_button )

        # The button to call the About DenseNet dialog
        about_densenet = wx.Button(left_menu, -1, "About DenseNet")
        about_densenet.SetPosition((20, 285))
        about_densenet.SetSize((200, 30))
        about_densenet_bitmap = wx.Bitmap("PROGRAM_INSTALL_FULLPATH\\info.png")
        about_densenet.SetBitmap(about_densenet_bitmap, wx.LEFT)
        self.Bind(wx.EVT_BUTTON, self.aboutDensenet, about_densenet)

        # The button to call the About dialog
        about_button = wx.Button(left_menu, -1, "About DenseNet Playground")
        about_button.SetPosition((20, 320))
        about_button.SetSize((200, 30))
        about_button_bitmap = wx.Bitmap("PROGRAM_INSTALL_FULLPATH\\info.png")
        about_button.SetBitmap(about_button_bitmap, wx.LEFT)
        self.Bind(wx.EVT_BUTTON, self.aboutApplication, about_button)




    def launchFileDialog(self, evt):
        # defining wildcard for suppported picture formats
        wildcard = "JPEG (*.jpg)|*.jpg|" \
                   "PNG (*.png)|*.png|" \
                   "GIF (*.gif)|*.gif"
        # defining the dialog object
        dialog = wx.FileDialog(self, message="Select Picture", defaultDir=os.getcwd(), defaultFile="",
                               wildcard=wildcard,
                               style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)
        # Function to retrieve file dialog response and return the full path of the first image (it is a multi-file selection dialog)
        if dialog.ShowModal() == wx.ID_OK:
            self.magic_collection[1].SetValue(
                "You have selected a Picture. It will now be processed!, Please wait! \nLoading.....")
            paths = dialog.GetPaths()

            # This adds the selected picture to the Right region. Right region object is retrieved from UI object array
            modification_bitmap1 = wx.Bitmap(paths[0])
            modification_image1 = modification_bitmap1.ConvertToImage()
            modification_image1 = modification_image1.Scale(650, 490, wx.IMAGE_QUALITY_HIGH)
            modification_bitmap2 = modification_image1.ConvertToBitmap()
            report_bitmap = wx.StaticBitmap(self.magic_collection[0], -1, modification_bitmap2, (0, 20))

            self.processPicture(paths[0],
                                "PROGRAM_INSTALL_FULLPATH\\DenseNet-BC-121-32.h5",
                                "PROGRAM_INSTALL_FULLPATH\\imagenet_class_index.json")

    def processPicture(self, path, model_path, index_file_path):

        # Report text box is updated with a message
        self.magic_collection[1].SetValue("Picture is currently being processed. May take a few minutes. Wait for the result! \n Loading.....")
        self.prediction_ongoing = True

        # Thread to initiate image prediction is called
        action = actionThreadDenseNet(path, model_path, index_file_path, self)
        action.start()

    def reportPrediction(self, message):
        # This adds the prediction report into the report text box
        self.magic_collection[1].SetValue(message)
        self.prediction_ongoing = False

    # The About Application Dialog Function
    def aboutApplication(self, evt):
        about_details = wx.adv.AboutDialogInfo()
        about_details.Name = "DenseNet Playground"
        about_details.Version = "1.0"
        about_details.Description = wordwrap("        DenseNet Playground is a software that enables users to perform average "
                                             "recognition and classification on pictures on computer systems. Powered by "
                                             "the Convolutional Neural Network Architecture, DenseNet model, trained on the ImageNet "
                                             "dataset which comprises of 1000 different objects in its 1.2 million pictures "
                                             "collection, this software can recognize on average most everyday objects based on "
                                             "the capability of the DenseNet + ImageNet model shipped with it. \n "
                                             "        This software is part of a series of programs that is meant to let "
                                             "non-programmers and average computer users to experience Artificial Intelligence "
                                             "in which machines and software programs can identify picture/objects in pictures. \n"
                                             "        These series of Artificial Intelligence playgrounds is built by Specpal "
                                             "with Moses Olafenwa as its Chief programmer and John Olafenwa as the Technical Adviser.  \n"
                                             "        This program is free for anyone to use for both commercial and non-commercial purposes.  "
                                             " We do not guarantee the accuracy or consistency of this program and we shall not be "
                                             "responsible for any consequence or damage to your computer system that may arise in the "
                                             " use of this program. \n"
                                             "        You can reach to Moses Olafenwa via an email to \"guymodscientist@gmail.com\", or John Olafenwa via an email to \"johnolafenwa@gmail.com\" . ", 500, wx.ClientDC(self))
        about_details.Copyright = "Specpal"
        about_details.SetWebSite("http://www.specpal.science", "Specpal's Official Website")

        about_dialog = wx.adv.AboutBox(about_details)

    # About DenseNet dialog function
    def aboutDensenet(self, evt):
        about_details = wx.adv.AboutDialogInfo()
        about_details.Name = "DenseNet"
        about_details.Version = "121"
        about_details.Description = wordwrap("      DenseNet is a Convolutional Neural Network that has considerable depth"
                                             " with improved accuracy, efficiency and reduced parameters. In this network, "
                                             "the output of each layer is connected to every other layer in a feed-forward "
                                             "fashion. It is developed by a team of researchers from Cornell University, "
                                             "Facebook AI Research and Tsinghua University.  "
                                             " ", 500, wx.ClientDC(self))
        about_details.Copyright = "Cornell University | Facebook AI Research | Tsinghua University"
        about_details.SetWebSite("https://github.com/liuzhuang13/DenseNet", "DenseNet GitHub page")
        about_details.SetDevelopers(["Gao Huang","Zhuang Liu", "Laurens van der Maaten", "Kilian Q. Weinberger"])

        about_dialog = wx.adv.AboutBox(about_details)









def Main():
    app = wx.App()
    Mainapp(None)
    app.MainLoop()

if __name__=="__main__":
    Main()
