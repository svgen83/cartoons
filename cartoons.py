import os
import requests

from dotenv import load_dotenv
from random import randint
from textwrap import dedent


def download_image(url, file_name, params=None):
    response = requests.get(url, params)
    response.raise_for_status()
    with open(file_name, "wb") as file:
        file.write(response.content)


def get_number_file(url):
    response = requests.get(url, params=None)
    response.raise_for_status()
    min_number_file = 1
    max_number_file = response.json()["num"]
    return randint(min_number_file, max_number_file)


def handle_vk_response(response):
    try:
        response.raise_for_status()
        if 'error' in response.json():
            raise requests.HTTPError
        return response.json()
    except requests.HTTPError:
        print("error code:", response.json()['error']['error_code'])
        print(response.json()['error']['error_msg'])
        os._exit(0)


def get_vk_upload_urL(vk_endpoint_template, vk_params):
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
    savewall_response = requests.post(
        vk_endpoint_template.format("photos.savewallPhoto"),
        params=save_params)
    savewall_stuff = handle_vk_response(savewall_response)
    owner_id = str(savewall_stuff["response"][0]["owner_id"])
    media_id = str(savewall_stuff["response"][0]["id"])
    description = json_comics_response["alt"]
    title = json_comics_response["title"]
    return {
        'access_token': vk_access_token,
        'v': "5.131",
        "owner_id": f"-{group_id}",
        "from_group": "1",
        "attachments": f"photo{owner_id}_{media_id}",
        "message": dedent(f"""{title}
                        {description}""")
    }


if __name__ == "__main__":

    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    vk_access_token = os.getenv("VK_ACCESS_TOKEN")
    group_id = os.getenv("GROUP_ID")
    current_comics_url = "https://xkcd.com/info.0.json"
    file_name = "comics.jpg"

    number_loading_file = get_number_file(current_comics_url)
    vk_endpoint_template = "https://api.vk.com/method/{}"
    vk_params = {
        'access_token': vk_access_token,
        'v': "5.131",
        "group_id": group_id
    }

    comics_url = "https://xkcd.com/{}/info.0.json".format(number_loading_file)

    comics_response = requests.get(comics_url, params=None)
    comics_response.raise_for_status()
    json_comics_response = comics_response.json()
    image_url = json_comics_response["img"]

    download_image(image_url, file_name)

    vk_upload_url = get_vk_upload_urL(vk_endpoint_template, vk_params)
    save_params = upload_file(vk_upload_url, vk_params, file_name)

    issue_params = get_issue_params(vk_access_token, group_id, save_params, json_comics_response)

    issue_response = requests.post(vk_endpoint_template.format("wall.post"), params=issue_params)
    handle_vk_response(issue_response)

    os.remove(file_name)
