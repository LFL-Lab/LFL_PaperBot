#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 8 09:12:38 2019
Updated on Jan 2 2020

@author: James Farmer, Sadman Ahmed Shanto

Version: 2.0
ChangeLog:

Two classes are defined below, Journalist and Editor.

The Journalist pulls RSS feeds, searches their contents, and generates a list 
of the articles which match our interest.

The Editor reviews the list of articles provided by the Journalist and generates
a list of those articles, less any repeated content, formatted as Slack message contents.
"""

import sys
from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from re import search, sub

#imports
from feedparser import parse


class Journalist:
    '''Searches the RSS feeds and passes relevant articles'''
    
    def __init__(self,feeds='feeds.txt',keywords='keywords.txt',authors='authors.txt',nLow=1):
        '''Journalist.drafts is a list of dictionaries with fields 
           'quality': number of keywords matched
           'matches': list of matching words
           'entry': dictionary of article details'''
        with open(feeds) as f:
            self.urls = self._get_strings(f.read())
        with open(keywords)as f:
            self.words = self._get_strings(f.read())
        with open(authors) as f:
            self.words += self._get_strings(f.read())
        self.errors = []
        notes = self._collect_feeds()
        self.titles = []
        reviews = [self._review_note(note,self.words) for note in notes if note['title'] not in self.titles]
        self.drafts = list(filter(lambda x: x['quality'] >= nLow, reviews))
        
    def _get_strings(self,text):
        '''returns a list of each line in text'''
        return text.strip().splitlines()
            
    def _collect_feeds(self,):
        '''Pulls the RSS feeds and returns summary as list of dictionaries'''
        with ThreadPoolExecutor() as e:
            raw_material = [e.submit(parse,url) for url in self.urls]
        notes_list = sum([M.result().entries for M in raw_material], [])
        notes = [self._clean_notes(i,note) for i,note in enumerate(notes_list)]
        self.nArticles = len(notes)
        return notes
        
    def _clean_notes(self, i, entry):
        """ returns a dict from entry containing article content and link """
        summary = reduce(lambda x,y: sub(y,' ',x),
                        [entry.summary,'Author[^>]+>','<[^>]+>','\n'])

        # Include abstract if available
        abstract = getattr(entry, 'abstract', '')
        full_text = summary + ' ' + abstract  # Combine summary and abstract
        
        try:
            data = {'text': entry.title +'\n'+ sub('\.','',entry.author) +'\n'+ full_text, 
                    'link': entry.link,
                    'title': entry.title, 
                    'authors': sub('<[^>]+>','',entry.author),
                    'summary': summary,
                    'abstract': abstract
                    }
        except AttributeError:
            data = {'text': entry.title +'\n'+ full_text, 
                    'link': entry.link,
                    'title': entry.title, 
                    'authors': 'No Author found in RSS',
                    'summary': summary,
                    'abstract': abstract
                    }
        except:
            e = sys.exc_info()[0]
            data = {'text': None}
            self.errors.append('Error: {}'.format(e) +'\n'+ entry.link)
        finally:
            return data

    def _review_note(self, note, words):
        """checks the note for any keywords"""
        self.titles.append(note['title'])

        # Search in both summary and abstract
        match_list = [self._search_note(note['text'], word) for word in words]
        match_words = [x for x, y in zip(words, match_list) if y == 1]
        dictionary = {'quality': sum(match_list), 'matching': match_words,
                    'entry': note}
        return dictionary
    
    def _search_note(self,note,word):
        """ checks the note for given string """
        if search(r'\b'+word.lower()+r'\b', note.lower()):
            return True
        else:
            return False
    
        
class Editor:
    '''retrieves the drafts from Journalist and formats them into
       JSON message payloads'''
       
    DIVIDER = {"type": "divider"}
       
    def __init__(self,feeds='feeds.txt',keywords='keywords.txt',authors='authors.txt',channel='channel.txt',nLow=1):
        journalist = Journalist(feeds,keywords,authors,nLow)
        self.timestamp = ""
        with open(channel) as f:
            self.channel = journalist._get_strings(f.read())[0]
        self.username = 'PaperBoy'
        self.icon = ":robot_face:"
        with open('previous_titles.txt') as f:
            self.titles = journalist._get_strings(f.read())
        self.new_titles = []
        self.articles = [self.get_payload(draft) for draft in journalist.drafts if draft['entry']['title'] not in self.titles]
        if self.new_titles:
            with open('previous_titles.txt','a') as f:
                f.write('\n'.join(str(title) for title in self.new_titles))
                f.write('\n')
        
    def get_payload(self,draft):
        E = draft['entry']
        self.new_titles.append(E['title'])
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon,
            "blocks": [
                self.DIVIDER,
                self.DIVIDER,
                self._get_title(E['title']),
                self._get_authors(E['authors']),
                self._get_link(E['link']),
                self.DIVIDER,
                self._get_summary(E['summary']),
                self._get_matched(draft['matching'])
                ],
            }
    
    def _get_title(self,title):
        return {
                "type": "section",
                "text": {"type": "mrkdwn","text": ("*{}*".format(title))}
                }
    def _get_authors(self,authors):
        return {
                "type": "section",
                "text": {"type": "mrkdwn","text": (authors)}
                }
    def _get_summary(self,summary):
        return {
                "type": "section",
                "text": {"type": "mrkdwn","text": (summary)}
                }
        
    def _get_matched(self,matches):
        return {
                "type": "section",
                "text": {"type": "mrkdwn","text": ('keyword matches: {}'.format(matches))}
                }
        
    def _get_link(self,link):
        return {
                "type": "context",
                "elements": [{"type": "mrkdwn","text": " :information_source: *<{}|Go to source>*".format(link)}]
                }
        
    
           