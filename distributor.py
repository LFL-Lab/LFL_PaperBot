#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 9 14:36:24 2019
Updated on Jan 2 2024

@author: James Farmer, Sadman Ahmed Shanto

Version 2.0
ChangeLog:
    
Calls an instance of printing_press.Editor and sends the articles to the Slack
channel ID specified in the accompanying text file 'channel.txt'

#### IMPORTANT ####
This code requires you to have already registered a new Slack App, and added
the bot user token to your system environment variables. See documentation at
"""
nKeywordMatches = 2
files = {
        'authors':'authors.txt',
        'channel':'channel.txt',
        'feeds':'feeds.txt',
        'keywords':'keywords.txt'
        }
txtpath = 'userTextFiles/'

kwargs = dict((v,txtpath+files[v]) for v in files)
kwargs.update({'nLow':nKeywordMatches})





import os
import ssl as ssl_lib

import certifi
import slack

from printing_press import Editor


def truncate_text(text, max_length=2990):
    """
    Truncate the text to the specified maximum length, adding an ellipsis if truncated.
    
    Args:
    text (str): The text to be truncated.
    max_length (int): The maximum allowed length of the text.
    
    Returns:
    str: The truncated text with ellipsis if necessary.
    """
    return text if len(text) <= max_length else text[:max_length] + "..."

def process_blocks(blocks):
    """
    Process each block in the Slack message to ensure text length is within allowed limits.
    
    Args:
    blocks (list): A list of blocks in the Slack message.
    
    Returns:
    list: A list of processed blocks with text truncated if necessary.
    """
    for block in blocks:
        if 'text' in block and isinstance(block['text'], dict) and 'text' in block['text']:
            block['text']['text'] = truncate_text(block['text']['text'])
    return blocks

def send_message(article):
    """
    Send a message to Slack, ensuring no block's text exceeds the maximum length.
    
    Args:
    article (dict): The article data to send.
    
    Returns:
    slack.web.client.WebClient.chat_postMessage: The response from the Slack API.
    """
    # Process blocks to ensure text length is within limits
    if 'blocks' in article:
        article['blocks'] = process_blocks(article['blocks'])

    response = client.chat_postMessage(**article)
    return response

if __name__ == "__main__":
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    editor = Editor(**kwargs)
    slack_token = os.environ['SLACK_TOKEN']
    client = slack.WebClient(token=slack_token,ssl=ssl_context)
    results = [send_message(art) for art in editor.articles]
