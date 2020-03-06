# async def get_bytes(url):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             return await response.read()
#
import pathlib
import os

def validate_folder_existence(path):
    if not os.path.exists(path):
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)