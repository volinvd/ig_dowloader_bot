from datetime import datetime
from itertools import dropwhile, takewhile
import instaloader
import logging


logger = logging.getLogger('download_ig')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

L = instaloader.Instaloader()


class GetLinksIG:
    def __init__(self):
        L.load_session_from_file("ig_downloader_bot",
                                 filename="data\session-ig_downloader_bot")

    def shortcode_from_link(self, link):
        """
        Gets the following link as input similar as www.instagram.com/p/shortcode/.
        Returns a shortcode (str type).
        :param link:
        :return shortcode:
        """
        logger.debug("Photo link is %s", link)
        data = link.split("/")
        index = data.index("p")
        shortcode = data[index + 1]
        logger.debug("Shorcode is %s", shortcode)

        return shortcode

    def username_from_link(self, link):
        """
        Gets the following link as input similar as www.instagram.com/username/.
        Returns a username (str type).
        :param link:
        :return username:
        """
        logger.debug("User account link is %s", link)
        data = link.split("/")
        if "www.instagram.com" in data:
            index = data.index("www.instagram.com")
            username = data[index + 1]
        elif "instagram.com" in data:
            index = data.index("instagram.com")
            username = data[index + 1]
        else:
            return None
        logger.debug("Username is %s", username)

        return username

    def get_photo_urls(self, link):
        """
        Makes a request to get the shortcode, then creates an object of the type
        instaloader.Post, gets the type of the post.
        Returns a list with post type, list of link/links to the original image/images, post's owner.
        :param link:
        :return list with
            type - str (can be GraphImage (single image) or GraphSidecar (media carousel))
            urls - list with links to the original images
            author - post's owner username
        """
        logger.debug("Post link is %s", link)
        try:
            shortcode = self.shortcode_from_link(link)
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            author = post.profile
            type = post.typename
            logger.debug("Post info %s", {"shorcode": shortcode, "author": author, "type": type})

            if type == "GraphImage":
                urls = self.get_link_from_single_photo(shortcode)
            elif type == "GraphSidecar":
                urls = self.get_link_from_carousel(shortcode)
            else:
                return None
            logger.debug("Urls: %s", urls)

            return [type, urls, author]
        except:
            return None

    def get_link_from_single_photo(self, shortcode):
        """
        Gets the shortcode as input.
        Returns a link to original photo (str type).
        :param shortcode:
        :return post url:
        """
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        return post.url

    def get_link_from_carousel(self, shortcode):
        """
        Gets the shortcode as input.
        Returns a list of links to original photos (str type).
        :param shortcode:
        :return list with post urls:
        """
        urls = []
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        for node in post.get_sidecar_nodes():
            urls.append(node.display_url)

        return urls

    def get_story_urls(self, username):
        """
        Gets the username as input.
        Returns a list with links to original photos/videos (str type).
        :param username:
        :return list with
            "Story" - str (type of media)
            urls - list with links to the original images and videos
            username - post's owner username
        """
        logger.debug("Username is %s", username)
        profile = instaloader.Profile.from_username(L.context, username)
        id = [profile.userid]
        urls = []
        for story in L.get_stories(id):
            # story is a Story object
            for item in story.get_items():
                if item.is_video:
                    link = item.video_url
                else:
                    link = item.url
                urls.append(link)

        logger.debug("Post info %s", {"urls": urls, "username": username, "username_id": id})

        return ["Story", urls, username]

    def get_profile_photo_link(self, link):
        """
        Gets the shortcode as input.
        Returns the link to user profile image (str type).
        :param shortcode:
        :return url:
        """
        logger.debug("Profile username is %s", link)
        profile = instaloader.Profile.from_username(L.context, link)
        profile_picture = profile.profile_pic_url
        logger.debug("Profile picture url is %s", profile_picture)

        return profile_picture

    def is_private_account(self, username):
        """
        Gets the username as input.
        Returns is private account (bool).
        :param username:
        :return boolean:
        """
        profile = instaloader.Profile.from_username(L.context, username)

        return profile.is_private

    def get_profile_info(self, link):
        """
        Gets the shortcode as input.
        Returns the dict with account information.
        :param shortcode:
        :return dict with info:
        """
        logger.debug("Username is %s", link)
        profile = instaloader.Profile.from_username(L.context, link)
        username = profile.full_name

        if profile.is_private:
            is_private = "Закрытый"
        else:
            is_private = "Открытый"

        followers = profile.followers
        followees = profile.followees

        count_of_media = profile.mediacount
        count_of_igtv = profile.igtvcount

        if profile.is_business_account:
            account_type = "Бизнес аккаунт"
        else:
            account_type = "Личный"

        info = {"username": username, "profile_type": is_private,
                "count_of_followers": followers, "count_of_followees": followees,
                "count_of_posts": count_of_media, "count_of_igtv": count_of_igtv,
                "type": account_type}

        logger.debug("Post info %s", info)

        return info

# ig = GetLinksIG()
# print(ig.get_profile_photo_link("instagram"))
