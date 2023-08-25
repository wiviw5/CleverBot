"""
This file is a part of the module "RSS Feed"

All Files related to this module:
cogs/rss_feed.py
modules/rss_feeds/rss_feed_reader_utils.py
modules/rss_feeds/rss_feeds.json

If you do not want the rss feeds module, a future release will have a toggle within a config file. (otherwise just remove the files related to the module.)

This relies on the RSS feed having unique titles to find out what posts are older.
"""
import json
import os
import time

import discord
import feedparser

from utils.utils import formatTimestamp

# This is time to wait between posting threads on discord, to avoid rate limits.
sleep_time = 2.5


async def updateAllFeeds(interaction: discord.Interaction):
    jsondata = getJsonDataFromFile()
    await interaction.followup.send(f"Updating all posts for {len(jsondata.keys())} RSS feeds.", ephemeral=True)
    for key in jsondata:
        jsondata = await updateFeed(interaction=interaction, json_data=jsondata, feed_name=key)
    updateJsonDataFile(jsondata)
    await interaction.followup.send(f"Finished updating all posts.", ephemeral=True)


async def updateFeed(interaction: discord.Interaction, json_data: dict, feed_name) -> dict:
    # This updates the last date it was checked for posts.
    json_data = updateLastUpdate(json_data=json_data, feed_name=feed_name)
    # Gets the newest feed data.
    feed_data = getFromURL(json_data=json_data, feed_name=feed_name)
    # Gets the last known post from the existing json data.
    last_known_post = getLastPost(json_data=json_data, feed_name=feed_name)
    # First, we check the first post, see if it is the last known post, if it is, then we report that and end this.
    if last_known_post == feed_data['entries'][0]['title']:
        await interaction.followup.send(f"Checked: {len(feed_data['entries'])}\nNo new posts found for: `{feed_name}`\n{formatTimestamp(int(time.time()), flag='F')}", ephemeral=True)
        return json_data
    # We update the last known post here, so when we return json data later, it is up-to-date with the latest post.
    json_data = updateLastPost(json_data=json_data, feed_name=feed_name, new_post=feed_data['entries'][0]['title'])
    # Gets the ID of the channel it should be sent in.
    channel_id = getChannelID(json_data=json_data, feed_name=feed_name)
    # Gets the ID of the channel it should be sent in.
    home_page = getHomePageURL(json_data=json_data, feed_name=feed_name)
    # Gets the profile URL for later use.
    icon_url = getIconURL(json_data=json_data, feed_name=feed_name)
    # Prepares the channel for sending the posts.
    channel = interaction.guild.get_channel(channel_id)
    # Next, we go through all posts, if we don't have any known posts in the list, we post them all.
    list_of_titles = []
    for post in feed_data['entries']:
        list_of_titles.append(post['title'])
    if last_known_post not in list_of_titles:
        await interaction.followup.send(f"Checked: {len(feed_data['entries'])}\nLast known post not found, sending all for: `{feed_name}`\n{formatTimestamp(int(time.time()), flag='F')}", ephemeral=True)
        feed_data['entries'].reverse()
        for feed in feed_data['entries']:
            time.sleep(sleep_time)
            await sendPost(channel=channel, post_title=feed['title'], post_url=feed['link'], home_page=home_page, feed_name=feed_name, icon_url=icon_url)
        return json_data

    # Now that we know that the post must exist in this list, we check this list
    found_post = False
    # First reversing the list, getting the oldest posts to the newest posts.
    feed_data['entries'].reverse()
    for feed in feed_data['entries']:
        # While we've not found the post yet, remove it from the entries, otherwise, we will "post it"
        if found_post:
            time.sleep(sleep_time)
            await sendPost(channel=channel, post_title=feed['title'], post_url=feed['link'], home_page=home_page, feed_name=feed_name, icon_url=icon_url)
        # Checking for the post to match, once we've found it, we mark it as true, and continue on.
        if feed['title'] == last_known_post:
            await interaction.followup.send(f"Checked: {len(feed_data['entries'])}\nFound latest post, posting all new posts for: `{feed_name}`\n{formatTimestamp(int(time.time()), flag='F')}", ephemeral=True)
            found_post = True
    return json_data


def updateLastUpdate(json_data: dict, feed_name: str) -> dict:
    json_data[feed_name]["last_update"] = int(time.time())
    return json_data


def getLastUpdate(json_data: dict, feed_name: str) -> str:
    return json_data[feed_name]["last_update"]


def updateLastPost(json_data: dict, feed_name: str, new_post: str) -> dict:
    json_data[feed_name]["last_post"] = new_post
    return json_data


def getLastPost(json_data: dict, feed_name: str) -> str:
    return json_data[feed_name]["last_post"]


def getHomePageURL(json_data: dict, feed_name: str) -> str:
    return json_data[feed_name]["homepage_url"]


def getChannelID(json_data: dict, feed_name: str) -> int:
    return json_data[feed_name]["discord_channel"]


def getIconURL(json_data: dict, feed_name: str) -> str:
    return json_data[feed_name]["profile_url"]


def getURL(json_data: dict, feed_name: str) -> str:
    return json_data[feed_name]["url"]


def getFromURL(json_data: dict, feed_name: str) -> feedparser.FeedParserDict:
    output = feedparser.parse(getURL(json_data=json_data, feed_name=feed_name))
    return output


async def sendPost(channel: discord.TextChannel, post_title: str, post_url: str, home_page: str, feed_name: str, icon_url: str):
    embed = discord.Embed(color=6230803, description=f"New upload!\n[{post_title}]({post_url})")
    embed.set_author(name=feed_name, url=home_page, icon_url=icon_url)
    embed.set_footer(text=home_page)
    await channel.send(embed=embed)


FILE_NAME = f"modules{os.sep}rss_feeds{os.sep}rss_feeds.json"


def getJsonDataFromFile() -> dict:
    with open(FILE_NAME) as file:
        data = json.load(file)
        file.close()
    return data


def updateJsonDataFile(json_data: dict):
    with open(FILE_NAME, "w") as file:
        file.write(json.dumps(json_data, indent=4))
        file.close()
