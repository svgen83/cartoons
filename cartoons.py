import logging
import os
import requests

from dotenv import load_dotenv
from random import randint
from textwrap import dedent


def download_image(image_response, file_name, params=None):
    image_url = image_response["img"]
    response = requests.get(image_url, params)
    response.raise_for_status()
    with open(file_name, "wb") as file:
        file.write(response.content)


def get_number():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url, params=None)
    response.raise_for_status()
    min_number = 1
    max_number = response.json()["num"]
    return randint(min_number, max_number)


def get_comics_response_stuff(number_loading_file):
    comics_url = "https://xkcd.com/{}/info.0.json".format(number_loading_file)
    comics_response = requests.get(comics_url, params=None)
    comics_response.raise_for_status()
    return comics_response.json()


def handle_vk_response(response):
    response.raise_for_status()
    response_stuff = response.json()
    if "error" in response_stuff:
        error_msg = dedent(f"""error code:{response_stuff["error"]
["error_code"]}.\n{response_stuff["error"]["error_msg"]}""")
        logging.error(error_msg)
        raise requests.HTTPError
    return response_stuff


def get_vk_upload_urL(vk_params):
    vk_endpoint = "https://api.vk.com/method/photos.getWallUploadServer"
    response = requests.get(vk_endpoint, vk_params)
    response_stuff = handle_vk_response(response)
    return response_stuff["response"]["upload_url"]


def upload_file(vk_upload_url, vk_params, file_name):
    with open(file_name, "rb") as file:
        files = {"photo": file}
        response = requests.post(vk_upload_url,
                                 files=files,
                                 params=vk_params)
    save_params = handle_vk_response(response)
    save_params.update(vk_params)
    return save_params


def get_publishing_params(VK_ACCESS_TOKEN, GROUP_ID, save_params, comics_response_stuff):
    vk_endpoint = "https://api.vk.com/method/photos.saveWallPhoto"
    response = requests.post(vk_endpoint, params=save_params)
    response.raise_for_status()
    response_stuff = handle_vk_response(response)
    owner_id = response_stuff["response"][0]["owner_id"]
    media_id = response_stuff["response"][0]["id"]
    description = comics_response_stuff["alt"]
    title = comics_response_stuff["title"]
    return {
            "access_token": VK_ACCESS_TOKEN,
            "v": "5.131",
            "owner_id": f"-{GROUP_ID}",
	    "from_group": "1",
	    "attachments": f"photo{owner_id}_{media_id}",
	    "message": dedent(f"{title}\n{description}")}
        
        
def publish_comics(publishing_params):
    vk_endpoint = "https://api.vk.com/method/wall.post"
    response = requests.post(vk_endpoint, params=publishing_params)
    response.raise_for_status()
    response_stuff = handle_vk_response(response)
	

def main():
    load_dotenv()

    VK_ACCESS_TOKEN = os.getenv("VK_ACCESS_TOKEN")
    GROUP_ID = os.getenv("GROUP_ID")
    
    file_name = "comics.jpg"

    vk_params = {
        "access_token": VK_ACCESS_TOKEN,
        "v": "5.131",
        "group_id": GROUP_ID
    }

    number_loading_file = get_number() 
    comics_response_stuff = get_comics_response_stuff(number_loading_file)
    download_image(comics_response_stuff, file_name)

    try:
        vk_upload_url = get_vk_upload_urL(vk_params)
        save_params = upload_file(vk_upload_url, vk_params, file_name)
        publishing_params = get_publishing_params(VK_ACCESS_TOKEN, GROUP_ID, save_params, comics_response_stuff)
        publish_comics(publishing_params)
    except requests.HTTPError:
        pass
    finally:
        os.remove(file_name)


if __name__ == "__main__":
    main()
