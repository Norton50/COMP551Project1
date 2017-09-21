#groupname_fre.xml
#Matthew Cooke
#McGill University COMP551 2017
#Project 1

import praw
import pathlib
import os
import argparse
from langdetect import detect_langs, DetectorFactory

class mainRedditParser():
    def __init__(self):
        self._commentCache = [] #where we cache the comments
        self.allComments = [] #we store a list of comments in order they appear for each comment block i.e. Top level, 2nd level, 3rd level etc
        self._userCache = [] #where we cache the user information and assign each user a unique id
        self.reddit = praw.Reddit(client_id='O0PCNBUhEfBr2A',
                             client_secret='HjTCmkLhpM4oOjjSeyYK2KOoMhw',
                             user_agent='Downloading reddit comments',
                             ) #this authenticates my reddit account, do not change
        self.getComments() #call the getcomments function on init

    def find_element_in_list(self, element): #this function returns either the user id of the user if previously indexed, or a new id
        try:
            index_element = self._userCache.index(element)
            return index_element
        except ValueError:
            self._userCache.append(element)
            return self.find_element_in_list(element)

    def getComments(self): #this gets all the comments in the france subreddit
        for submission in self.reddit.subreddit('france').hot(limit=10): #limit is how many threads to explore, use a low number for testing
            self.getAllCommentsRec(submission) #get all comments recursively
            for comment in self._commentCache: #for every toplevel comment
                self.allComments = [] #resent out list
                self.getSubComments(comment,self.allComments) #get all lower level comments, add to list
                print("<s>",end='')
                for aComment in self.allComments:#for each of the comments in our list, print them according to XML style
                    theComment = aComment.body.replace('\r', ' ').replace('\n', ' ')
                    if (self.detect_language(theComment)):
                        print("<utt uid=\"", self.find_element_in_list(aComment.author), "\">", theComment, "</utt>", end='')
                print("</s>")


    def getAllCommentsRec(self, subm): #get all toplevel comments recursively
        subm.comments.replace_more(limit=0)
        for comment in subm.comments.list():
            self._commentCache.append(comment)


    def getSubComments(self, comment, allComments):#recursively get all child comments
        allComments.append(comment)
        if not hasattr(comment, "replies"):
            replies = comment.comments()
        else:
            replies = comment.replies
        for child in replies:
            self.getSubComments(child, allComments)

    def detect_language(self, text):
        try:
            langlist = str(detect_langs(text))
            if (langlist.find('fr') != -1 ):
                return True
            else:
                return False
        except:
            return True


DetectorFactory.seed = 0
print("<dialog>")
mainRedditParser()
print("</dialog>")