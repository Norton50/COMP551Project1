#groupname_fre.xml
#Matthew Cooke
#McGill University COMP551 2017
#Project 1

import praw
import time
import pathlib
import os
import argparse
from langdetect import detect_langs, DetectorFactory

class mainRedditParser():
    def __init__(self):
        self.commentCache = [] #where we cache the first comment of a sequence/conversation
        self.commentSequence = [] #we store a list of comments in order they appear for each comment block i.e. Top level, 2nd level, 3rd level etc
        self.userCache = [] #where we cache the user information and assign each user a unique id
        self.reddit = praw.Reddit(client_id='O0PCNBUhEfBr2A',
                             client_secret='HjTCmkLhpM4oOjjSeyYK2KOoMhw',
                             user_agent='Downloading reddit comments',
                             ) #this authenticates my reddit account, do not change
        self.stringSequences = '' # XML string of all comment sequences in a thread
        self.numSequences = 0 # the number of lines we expect to see in our XML file
        self.output_file = open('mxdvmc_fre.xml', 'w', encoding='utf-8')
        self.getComments() #call the getcomments function on init

    def find_element_in_list(self, element): #this function returns either the user id of the user if previously indexed, or a new id
        try:
            index_element = self.userCache.index(element)
            return index_element
        except ValueError:
            index_element = len(self.userCache)
            self.userCache.append(element)
            return index_element

    def getComments(self): #this gets all the comments in the france subreddit
        print("<dialog>", file=self.output_file)
        
        for submission in self.reddit.subreddit('france').hot(limit=100):      #limit is how many threads to explore, use a low number for testing
            self.getTopLevelComments(submission)                                #get all toplevel comments
            self.stringSequences = ''                                            #clear for each submission
            for comment in self.commentCache:                                   #for every toplevel comment
                self.userCache = []                                             #reset users for each conversation
                self.commentSequence = []                                       #reset out list
                newSequence = ''
                self.getSubComment(comment,self.commentSequence)                #get the first sequence of replies to the comment
                for aComment in self.commentSequence:                           #for each of the comments (utterances) in the sequence, append in XML format to string
                    theComment = aComment.body.replace('\r', ' ').replace('\n', ' ')
                    if (self.detect_language(theComment)):
                        newSequence += ''.join(["<utt uid=\"", str(self.find_element_in_list(aComment.author)), "\">", theComment, "</utt>"])
                    else:
                        self.commentSequence = []                               #ignore the rest of the comments after the french comment
                if newSequence:
                    newSequence = "<s>" + newSequence + "</s>\n"
                    self.stringSequences += newSequence
            print(self.stringSequences, end='', file=self.output_file)           #call print once for each thread
            self.numSequences += len(self.commentCache)                        #track number of comment sequences we should end up with
        
        print("</dialog>", file=self.output_file)
    
    def getTopLevelComments(self,subm):
        subm.comments.replace_more(limit=0)
        self.commentCache = list(subm.comments)
        
    def getSubComment(self, comment, commentSequence):
        commentSequence.append(comment)
        if comment.replies:
            self.getSubComment(comment.replies[0], commentSequence)
            # if we want to include subsequent replies to the comment in their own comment sequence starting with the reply:
            # add all replies except for the first to the comment queue
            self.commentCache.extend(comment.replies[1:])

    '''def getAllCommentsRec(self, subm): #note that this gets all comments, starting with root, then level 1, level 2...
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
            self.getSubComments(child, allComments)'''

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
start_time = time.time()
a = mainRedditParser()
print(time.time() - start_time)
print(a.numSequences)
