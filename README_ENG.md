# Сartoons

This program is designed to download comics [Randel Munro](https://xkcd.com) and their subsequent publication in the social network Vkontakte. 

### How to setup

Python3 should already be installed.
Then use `pip` (or `pip3` if there is a conflict with Python2) to install the dependencies:

```
pip install -r requirements.txt
```

### Vkontakte group and application settings
Before starting the program, you must create a group on the Vkontakte social network in which the comic will be published. To work with the program, you need `group_id`,
you can find it on [this site](https://regvk.com/id/).
Then you should create an application on the [Vkontakte developers page] (https://vk.com/dev) so that this program interacts with the API.
Specify `standalone` as the application type. Once the application has been created, get its `client_id` by clicking the "Edit" button for the new application.
Then get the application access key using the [Implicit Flow procedure](https://vk.com/dev/implicit_flow_user). You will need the following rights: `photos`,
`groups`, `wall`, `offline`.

### Program settings

In order for the program to work correctly, create an .env file in the program folder containing `client_id`, `group_id` and the application access key.
Write its contents like this:

```
CLIENT_ID="client_id приложения Вконтакте"
GROUP_ID="group_id группы Вконтакте"
VK_ACCESS_TOKEN="номер ключа доступа приложения"
```

### How to run

The program is launched from the command line. To run the program using the cd command, you first need to go to the folder with the program.
To run the program on the command line, write:
```
python cartoons.py
```
After the program is completed, a randomly selected comic will be published on the wall of the group you created.
If the program has published a comic, the downloaded picture will not be saved on your computer.

### Goal of project

Code written for educational purposes in an online course for web developers[dvmn.org](https://dvmn.org/).
