import logging
import os
import requests

from dotenv import load_dotenv
from random import randint
from textwrap import dedent


def download_image(url, file_name):
    response = requests.get(url)
    response.raise_for_status()
    with open(file_name, "wb") as file:
        file.write(response.content)


def get_random_comics_number():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    min_number = 1
    max_number = response.json()["num"]
    return randint(min_number, max_number)


def get_comics_response_stuff(number_loading_file):
    url = "https://xkcd.com/{}/info.0.json".format(number_loading_file)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def handle_vk_response(response):
    response.raise_for_status()
    response_stuff = response.json()
    if "error" in response_stuff:
        error_msg = dedent(f"""\
        error code:{response_stuff["error"]["error_code"]}.
        {response_stuff["error"]["error_msg"]}""")
        logging.error(error_msg)
        raise requests.HTTPError
    return response_stuff


def get_vk_upload_url(vk_params):
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
    savewall_method_params = handle_vk_response(response)
    savewall_method_params.update(vk_params)
    return savewall_method_params


def get_publishing_params(vk_access_token, group_id,
                          savewall_method_params, comics_response_stuff):
    vk_endpoint = "https://api.vk.com/method/photos.saveWallPhoto"
    response = requests.post(vk_endpoint, params=savewall_method_params)
    response.raise_for_status()
    response_stuff = handle_vk_response(response)
    owner_id = response_stuff["response"][0]["owner_id"]
    media_id = response_stuff["response"][0]["id"]
    description = comics_response_stuff["alt"]
    title = comics_response_stuff["title"]
    return {
            "access_token": vk_access_token,
            "v": "5.131",
            "owner_id": f"-{group_id}",
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

    vk_access_token = os.getenv("VK_ACCESS_TOKEN")
    group_id = os.getenv("GROUP_ID")

    file_name = "comics.jpg"

    vk_params = {
        "access_token": vk_access_token,
        "v": "5.131",
        "group_id": group_id
    }

    number_loading_file = get_random_comics_number()
    comics_response_stuff = get_comics_response_stuff(number_loading_file)
    download_image(comics_response_stuff["img"], file_name)

    try:
        vk_upload_url = get_vk_upload_url(vk_params)
        savewall_method_params = upload_file(vk_upload_url, vk_params,
                                             file_name)
        publishing_params = get_publishing_params(vk_access_token, group_id,
                                                  savewall_method_params,
                                                  comics_response_stuff)
        publish_comics(publishing_params)
    except requests.HTTPError:
        pass
    finally:
        os.remove(file_name)


if __name__ == "__main__":
    main()

