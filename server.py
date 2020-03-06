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
# app.mount('/static', StaticFiles(directory='statics'), name='static')

# Path for the images.
img_folder = "data/imgs"

print(__name__)
tokens = []


def load_tokens():
    f = open('data/tokens.json', 'r')
    data = json.load(f)
    f.close()
    return data


def is_token_valid(request):
    return 'token' in request.headers and request.headers['token'] in tokens


def get_model_classes():
    f = open('data/lable_json.json', 'r')
    json_file = json.load(f)
    f.close()
    return json_file


learn = Learner('data', get_model_classes())


@app.route("/classify", methods=["POST"])
async def upload(request):
    if not is_token_valid(request):
        return Response(status_code=404)
    data = await request.form()
    print(request.headers)
    bytes = await (data["file"].read())
    print(data['file'].filename)
    response = learn.predict(bytes)
    res = {
        "timestamp": int(time.time()),
        "results": response
    }
    print(res)
    return JSONResponse(res)


@app.route('/class/fetch/all')
async def fetch_all_labels(request):
    if not is_token_valid(request):
        return Response(status_code=404)
    return JSONResponse(get_model_classes())


@app.route('/')
async def default_route(request):
    return Response(status_code=404)


@app.route('/learn/add', methods=["POST"])
async def save_img(request):
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
    tokens = load_tokens()
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
