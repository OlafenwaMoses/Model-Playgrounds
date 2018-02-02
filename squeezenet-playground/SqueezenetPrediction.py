"""

#AUTHORS
*** Moses Olafenwa
*** John Olafenwa
>> January, 2018

"""

from imagenet_utils import preprocess_input,decode_predictions
import numpy as np
from keras.preprocessing import image
from squeezenet import SqueezeNet
import wx
from wx.lib.pubsub import pub, setupkwargs



def predict(path, model_path, index_file_path, MainUI):

    try:
        result_string = " Detected Object : Probability \n \n"

        if (MainUI.squeezenet_model_loaded == False):
            wx.CallAfter(pub.sendMessage, "report101",
                         message="Loading SqueezeNet model for the first time. This may take few minutes or less than a minute. Please wait. \nLoading.....")
            model = SqueezeNet(model_path=model_path)
            wx.CallAfter(pub.sendMessage, "report101",
                         message="SqueezeNet model loaded.. Picture about to be processed.. \nLoading......")
            MainUI.model_collection_squeezenet.append(model)
            MainUI.squeezenet_model_loaded = True
        else:
            wx.CallAfter(pub.sendMessage, "report101", message="Retrieving loaded model. \nLoading........")
            model = MainUI.model_collection_squeezenet[0]
            wx.CallAfter(pub.sendMessage, "report101",
                         message="ResNet model loaded.. Picture about to be processed.. \nLoading......")

        img = image.load_img(path, target_size=(227, 227))
        img = image.img_to_array(img, data_format="channels_last")
        img = np.expand_dims(img, axis=0)

        img = preprocess_input(img, data_format="channels_last")
        wx.CallAfter(pub.sendMessage, "report101", message="Picture is transformed for prediction. \nLoading........")


        prediction = model.predict(img, steps=1)
        wx.CallAfter(pub.sendMessage, "report101",
                     message="Picture prediction is done. Sending in results. \nLoading......")

        predictiondata = decode_predictions(prediction, top=10, index_file_path=index_file_path)

        for results in predictiondata:
            countdown = 0
            for result in results:
                countdown += 1
                result_string += "(" + str(countdown) + ") " + str(result[1]) + " : " + str(100 * result[2])[
                                                                                        0:4] + "% \n"

        return result_string
    except Exception as e:
        return getattr(e, "message", repr(e))


