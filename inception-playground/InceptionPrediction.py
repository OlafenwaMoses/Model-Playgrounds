"""

#AUTHORS
*** Moses Olafenwa
*** John Olafenwa
>> January, 2018


"""

from keras.preprocessing import image
from inceptionv3 import InceptionV3
from inceptionv3 import preprocess_input,decode_predictions
import numpy as np
import wx
from wx.lib.pubsub import pub



def run(path, model_path, index_file_path, MainUI):
    try:
        result_string = " Detected Object : Probability \n \n"

        image_to_predict = image.load_img(path,
                                          grayscale=False, target_size=(299, 299))
        image_to_predict = image.img_to_array(image_to_predict, data_format="channels_last")
        wx.CallAfter(pub.sendMessage, "report101", message="Picture is transformed for prediction. \nLoading........")
        image_to_predict = np.expand_dims(image_to_predict, axis=0)

        image_to_predict = preprocess_input(image_to_predict)

        # Making check to load Model
        if (MainUI.inception_model_loaded == False):
            wx.CallAfter(pub.sendMessage, "report101",
                         message="Loading Inception V3 model for the first time. This may take few minutes or less than a minute. Please wait. \nLoading.....")
            model = InceptionV3(include_top=True, weights="imagenet", model_path=model_path)
            wx.CallAfter(pub.sendMessage, "report101",
                         message="Inception V3 model loaded.. Picture about to be processed.. \nLoading......")
            MainUI.model_collection_inception.append(model)  # Loading model if not loaded yet
            MainUI.inception_model_loaded = True
        else:
            wx.CallAfter(pub.sendMessage, "report101", message="Retrieving loaded model. \nLoading........")
            model = MainUI.model_collection_inception[0]  # Getting Model from model array if loaded before
            wx.CallAfter(pub.sendMessage, "report101",
                         message="Inception V3 model loaded.. Picture about to be processed.. \nLoading......")



        prediction = model.predict(x=image_to_predict, steps=1)
        wx.CallAfter(pub.sendMessage, "report101",
                     message="Picture prediction is done. Sending in results. \nLoading......")


        prediction_result = decode_predictions(prediction, top=10, index_file_path=index_file_path)

        for results in prediction_result:
            countdown = 0
            for result in results:
                countdown += 1
                result_string += "(" + str(countdown) + ") " + str(result[1]) + " : " + str(100 * result[2])[
                                                                                       0:4] + "% \n"

        return result_string

    except Exception as e:
        return getattr(e, "message", repr(e))

