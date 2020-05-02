import re

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse
from learner import Learner
from io import BytesIO
import uvicorn
from utils_func import *
import sys
import json
from starlette.responses import Response
import time
from PIL import Image

app = Starlette(debug=True)
PATH = {
    'tokens': 'data/tokens.json',
    'labels': 'data/lable_json.json',
    'nutrition_db': 'data/nutrition_db.json'
}

# Path for the images.
img_folder = "data/imgs"

tokens = []
nutrition = []


def is_token_valid(request):
    """
        Validates the existence of a token from the client request with saved tokens list.

        :param Request request : Request Incoming request from client.
        :return bool: Token existence will return true, false otherwise
    """

    return 'token' in request.headers and request.headers['token'] in tokens


def load_json(path):
    """
        Loads a Json file and returns the deserialized object of that json.

        :param string path: requested file path
        :return dictionary json:  Deserialized representation of the json file
    """

    f = open(path, 'r')
    json_file = json.load(f)
    f.close()
    return json_file


learn = Learner('data', load_json(PATH['labels']))


@app.route("/classify", methods=["POST"])
async def upload(request):
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
    response = learn.predict(imgBytes, 2)
    if 'extended' in data and data['extended'].lower() == "true":
        print("Need extra data")
        for item in response:
            item['extra'] = [d for d in nutrition if d['id'] == item['label']['nutrition_id']]
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
    return JSONResponse(load_json(PATH['labels']))


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
            folder_path = os.path.join(img_folder, label)  # Generate folder in case it does not exist.
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
    tokens = load_json(PATH['tokens'])
    nutrition = load_json(PATH['nutrition_db'])
    print(tokens)
    if len(sys.argv) > 1:
        if sys.argv[1] == "live":
            # uvicorn.run(app, host="0.0.0.0", port=8000,
            #             ssl_keyfile="/home/anaconda/.local/share/mkcert/xxx-key.pem",
            #             ssl_certfile="/home/anaconda/.local/share/mkcert/xxx.pem")
            uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        uvicorn.run(app, port=8000, ssl_keyfile="/home/anaconda/.local/share/mkcert/localhost-key.pem",
                    ssl_certfile="/home/anaconda/.local/share/mkcert/localhost.pem")
