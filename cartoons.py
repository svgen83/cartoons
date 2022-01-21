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


def get_json_stuff(url, params):
    response = requests.get(url, params)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":

    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    vk_access_token = os.getenv("VK_ACCESS_TOKEN")
    group_id = os.getenv("GROUP_ID")

    file_name = "comics.jpg"
    min_number_file = 1
    max_number_file = 2564
    number_loaded_file = randint(min_number_file, max_number_file)

    comics_url = "https://xkcd.com/{}/info.0.json".format(number_loaded_file)
    vk_endpoint_template = "https://api.vk.com/method/{}"
    vk_params = {
        'access_token': vk_access_token,
        'v': "5.131",
        "group_id": group_id
    }

    comics_response = get_json_stuff(comics_url, params=None)

    description = comics_response["alt"]
    title = comics_response["title"]
    image_url = comics_response["img"]

    download_image(image_url, file_name)

    for_upload_response = get_json_stuff(
        vk_endpoint_template.format("photos.getWallUploadServer"),
        vk_params)
    upload_url = for_upload_response["response"]["upload_url"]

    with open(file_name, 'rb') as file:
        files = {"photo": file}
        files.update(vk_params)
        uploaded_file_response = requests.post(upload_url, files=files)
        uploaded_file_response.raise_for_status()
    save_params = uploaded_file_response.json()
    save_params.update(vk_params)

    saveWall_response = requests.post(vk_endpoint_template.format(
        "photos.saveWallPhoto"), params=save_params)
    saveWall_response.raise_for_status()
    saveWall_stuff = saveWall_response.json()
    owner_id = str(saveWall_stuff["response"][0]["owner_id"])
    media_id = str(saveWall_stuff["response"][0]["id"])

    issue_params = {
        'access_token': vk_access_token,
        'v': "5.131",
        "owner_id": f"-{group_id}",
        "from_group": "1",
        "attachments": f"photo{owner_id}_{media_id}",
        "message": dedent(f"""{title}
                          {description}""")
    }

    issue_response = requests.post(vk_endpoint_template.format("wall.post"),
                                   params=issue_params)
    issue_response.raise_for_status()

    os.remove(file_name)
