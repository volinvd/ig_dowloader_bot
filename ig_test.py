from instabot import Bot
import os
import shutil
import requests

bot = Bot()
bot.login(username="ig_downloader_bot", password="sd89dg46fgd", use_cookie=False)


def get_original_photo_link(media_id):
    print(bot.get_media_info(media_id))

    if ("image_versions2" in media.keys()):
        url = media["image_versions2"]["candidates"][0]["url"]
        response = requests.get(url)
        # with open(filename + ".jpg", "wb") as f:
        #     response.raw.decode_content = True
        #     f.write(response.content)^sd89dg46fgd

        return url

    elif("carousel_media" in media.keys()):
        urls = []
        for e, element in enumerate(media["carousel_media"]):
            url = element['image_versions2']["candidates"][0]["url"]
            response = requests.get(url)
            # with open(filename + str(e) + ".jpg", "wb") as f:
            #     response.raw.decde_content = True
            #     f.write(response.content)
            urls.append(url)

        return urls


def get_photo(link):
    media_link = link
    media_id = bot.get_media_id_from_link(media_link)

print(get_original_photo_link("https://www.instagram.com/p/CLSIfODgRJq/"))