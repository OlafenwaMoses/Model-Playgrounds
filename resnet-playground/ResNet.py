"""

#AUTHORS
*** Moses Olafenwa
*** John Olafenwa
>> January, 2018


"""


# Import needed keras, tensorflow and resnet50 classes
from keras.preprocessing import image
from resnet50 import ResNet50
from imagenet_utils import preprocess_input,decode_predictions
import numpy as np
import wx
from wx.lib.pubsub import pub, setupkwargs




# Image Prediction function
def predict(path, model_path, index_file_path, MainUI):
    try:
        result_string = " Detected Object : Probability \n \n"

        # Making check to load Model
        if (MainUI.resnet_model_loaded == False):
            wx.CallAfter(pub.sendMessage, "report101", message="Loading ResNet model for the first time. This may take a few minutes or less than a minute. Please wait. \nLoading.....")
            model = ResNet50(include_top=True, weights="imagenet", model_path=model_path)
            wx.CallAfter(pub.sendMessage, "report101", message="ResNet model loaded.. Picture about to be processed.. \nLoading......")
            MainUI.model_collection_resnet.append(model)  # Loading model if not loaded yet
            MainUI.resnet_model_loaded = True
        else:
            wx.CallAfter(pub.sendMessage, "report101", message="Retrieving loaded model. \nLoading........")
            model = MainUI.model_collection_resnet[0]  # Getting Model from model array if loaded before
            wx.CallAfter(pub.sendMessage, "report101", message="ResNet model loaded.. Picture about to be processed.. \nLoading......")

        # Image prediction processing
        target_image = image.load_img(path, grayscale=False, target_size=(224, 224))
        target_image = image.img_to_array(target_image, data_format="channels_last")
        target_image = np.expand_dims(target_image, axis=0)

        target_image = preprocess_input(target_image, data_format="channels_last")
        wx.CallAfter(pub.sendMessage, "report101", message="Picture is transformed for prediction. \nLoading........")
        prediction = model.predict(x=target_image, steps=1)
        wx.CallAfter(pub.sendMessage, "report101", message="Picture prediction is done. Sending in results. \nLoading......")

        # Retrieving prediction result and sending it back to the thread
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




