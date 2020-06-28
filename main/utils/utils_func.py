import pathlib
import os
import json


def validate_folder_existence(path):
    if not os.path.exists(path):
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)


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
