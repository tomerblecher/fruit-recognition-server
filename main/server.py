
import sys
import time
from io import BytesIO
import re

from main.config import Config
import uvicorn
from PIL import Image
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.responses import Response
from main.utils.utils_func import *

config = Config()
app = Starlette(debug=True)


def is_token_valid(request):
    """
        Validates the existence of a token from the client request with saved tokens list.
        :param Request request : Request Incoming request from client.
        :return bool: Token existence will return true, false otherwise
    """

    return 'token' in request.headers and request.headers['token'] in config.tokens


@app.route("/status/token")
async def check_token(request):
    """
    Validates the client token.
    :param request:
    :param Request request : Request Incoming request from client.
    :return Response|JSONResponse: In case of an error in validation, an error response will be returned.
                                   In case of a success,
                                   200 status response will be sent.
    """
    if not is_token_valid(request):
        return Response(status_code=404)
    return Response(status_code=200)


@app.route("/client/config")
async def fetch_client_config(request):
    """
    Fetch updated client configuration.
    :param request:
    :param Request request : Request Incoming request from client.
    :return Response|JSONResponse: In case of an error in validation, an error response will be returned.
                                   In case of a success,
                                   200 status response will be sent.
    """
    if not is_token_valid(request):
        return Response(status_code=404)
    return JSONResponse(load_json(config.path['client_config']))


@app.route("/classify", methods=["POST"])
async def classify(request):
    """
        Predicts the classes for a given image.
        The function will emit the predict method on the learner object and return the result.
        Nutrition data will be added if the user flagged the 'extended' parameter as true.

        :param Request request : Request Incoming request from client.
        :return Response|JSONResponse: In case of an error in validation, an error response will be returned.
                                       In case of a success,
                                       a json response will be returned with the predicted classes & nutrition facts.
    """
    if not is_token_valid(request):
        return Response(status_code=404)
    data = await request.form()
    print(request.headers)

    print(data['file'].filename)
    imgBytes = await (data['file'].read())
    print("Image size: {}".format(len(imgBytes)))
    response = config.learn.predict(imgBytes, 2)
    if 'extended' in data and data['extended'].lower() == "true":
        print("Need extra data")
        for item in response:
            item['extra'] = [d for d in config.nutrition if d['info']['id'] == item['label']['nutrition_id']][0]
    res = {
        "timestamp": int(time.time()),
        "results": response
    }
    print(res)
    return JSONResponse(res)


@app.route('/class/fetch/all')
async def fetch_all_labels(request):
    """
        Fetch label list from the configured Json file.

        :param Request request : Request Incoming request from client.

        :return Response|JSONResponse: In case of an error in validation, an error response will be returned.
                                       In case of a success, a json response will be returned with the labels list.
    """

    if not is_token_valid(request):
        return Response(status_code=404)
    return JSONResponse(load_json(config.path['labels']))


@app.route('/nutrition/{class_id:int}')
async def fetch_nutrition(request):
    """
        Fetch nutrition data for given class id.

        :param Request request : Request Incoming request from client.

        :return Response|JSONResponse: In case of an error in validation, an error response will be returned.
                                       In case of a success, a json response will be returned with the labels list.
    """

    if not is_token_valid(request):
        return Response(status_code=404)
    label = config.learn.fetch_label(request.path_params['class_id'])
    if label is None:
        return Response(status_code=404)
    item = {}
    item['label'] = label
    item['extra'] = [d for d in config.nutrition if d['info']['id'] == label['nutrition_id']][0]
    return JSONResponse(item)


@app.route('/label/fetch', methods=["POST"])
async def fetch_label(request):
    """
        Fetch Label information for array of ids.

        :param Request request : Request Incoming request from client.

        :return Response|JSONResponse: In case of an error in validation, an error response will be returned.
                                       In case of a success, a json response will be returned with the labels list.
    """

    if not is_token_valid(request):
        return Response(status_code=404)

    data = await request.form()
    id_list = data.getlist('id_list[]')
    final_items = []

    for id in id_list:
        label = config.learn.fetch_label(int(id))
        if label is not None:
            item = {'label': label, 'extra': [d for d in config.nutrition if d['info']['id'] == label['nutrition_id']][0]}
            final_items.append(item)
    return JSONResponse(final_items)


@app.route('/')
async def default_route(request):
    """
        Since we are exposing the server to the world, lets try to hide it from unwanted visitors.
    """
    return Response(status_code=404)


@app.route('/learn/add', methods=["POST"])
async def save_img(request):
    """
        Save a new incoming image on the server.
        Request will go through validation before saving.

        :param Request request : Request Incoming request from client.
        :return Response|JSONResponse: In case of an error in validation, an error response will be returned.
                                       In case of a success, a json response will be returned with status 200.
    """
    if not is_token_valid(request):
        return Response(status_code=404)
    data = await request.form()
    for f in data.getlist('files'):
        bytes = await (f.read())
        file_name = f.filename
        label = data["label"]
        if re.search(r'[^A-Za-z0-9_\.]{1,50}', file_name) or re.search(r'[^0-9]', label):
            return Response(status_code=502)
        try:
            folder_path = os.path.join(config.path['img_folder'], label)  # Generate folder in case it does not exist.
            validate_folder_existence(folder_path)
            img = Image.open(BytesIO(bytes))
            img.save(os.path.join(folder_path, file_name))
        except:
            print('test')
            return Response(status_code=500)
    return JSONResponse({
        "status": 200
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
