import os
import requests

from dotenv import load_dotenv
from random import randint
from textwrap import dedent


def download_image(json_comics_response, file_name, params=None):
    image_url = json_comics_response["img"]
    response = requests.get(image_url, params)
    response.raise_for_status()
    with open(file_name, "wb") as file:
        file.write(response.content)


def get_number_file(url):
    response = requests.get(url, params=None)
    response.raise_for_status()
    min_number_file = 1
    max_number_file = response.json()["num"]
    return randint(min_number_file, max_number_file)


def get_json_comics_response(number_loading_file):
    comics_url = "https://xkcd.com/{}/info.0.json".format(number_loading_file)
    comics_response = requests.get(comics_url, params=None)
    comics_response.raise_for_status()
    return comics_response.json()


def handle_vk_response(response):
    response.raise_for_status()
    json_stuff = response.json()
    if 'error' in json_stuff:
    raise requests.HTTPError
    return json_stuff


def get_vk_upload_urL(vk_params):
    vk_endpoint_template = "https://api.vk.com/method/{}"
    response = requests.get(
        vk_endpoint_template.format("photos.getWallUploadServer"),
        vk_params)
    json_stuff = handle_vk_response(response)
    return json_stuff["response"]["upload_url"]


def upload_file(vk_upload_url, vk_params, file_name):
    with open(file_name, 'rb') as file:
        files = {"photo": file}
        uploaded_file_response = requests.post(vk_upload_url,
                                               files=files,
                                               params=vk_params)
    save_params = handle_vk_response(uploaded_file_response)
    save_params.update(vk_params)
    return save_params


def get_issue_params(vk_access_token, group_id, save_params, json_comics_response):
    vk_endpoint_template = "https://api.vk.com/method/{}"
    savewall_response = requests.post(
        vk_endpoint_template.format("photos.saveWallPhoto"),
        params=save_params)
    savewall_stuff = handle_vk_response(savewall_response)
    owner_id = savewall_stuff["response"][0]["owner_id"]
    media_id = savewall_stuff["response"][0]["id"]
    description = json_comics_response["alt"]
    title = json_comics_response["title"]
    return {
        'access_token': vk_access_token,
        'v': "5.131",
        "owner_id": f"-{group_id}",
        "from_group": "1",
        "attachments": f"photo{owner_id}_{media_id}",
        "message": dedent(f"{title}\n{description}")}
        
        
def publishing_comics(publishing_params):
    vk_endpoint_template = "https://api.vk.com/method/{}"
    publishing_response = requests.post(vk_endpoint_template.format("wall.post"), params=issue_params)
    handle_vk_response(publishing_response)


if __name__ == "__main__":

    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    vk_access_token = os.getenv("VK_ACCESS_TOKEN")
    group_id = os.getenv("GROUP_ID")

    file_name = "comics.jpg"

    vk_params = {
        'access_token': vk_access_token,
        'v': "5.131",
        "group_id": group_id
    }

    number_loading_file = get_number_file(current_comics_url) 
    json_comics_response = get_json_comics_response(number_loading_file)
    download_image(json_comics_response, file_name)

    try:
        vk_upload_url = get_vk_upload_urL(vk_params)
        save_params = upload_file(vk_upload_url, vk_params, file_name)
        publishing_params = get_issue_params(vk_access_token, group_id, save_params, json_comics_response)
        publishing_comics(issue_params)
    except requests.HTTPError:
        print("error code:", json_stuff['error']['error_code'])
        print(json_stuff['error']['error_msg'])
    finally:
        os.remove(file_name)
