# -*- coding: utf-8 -*-
import praw
import datetime
from utils.tools import tools
import json
import traceback

class RedditAPI():
    def __init__(self,db=None):
        self.reddit = praw.Reddit(
                                  client_id=, #your stuff here
                                  client_secret=,
                                  password=,
                                  user_agent=,
                                  username=
                                )
        self.db = db

    def get_submissions(self,r_sub='news'):
        rows = []

        for submission in self.reddit.subreddit(r_sub).new(limit=256):
            if not submission.is_self and not submission.is_video:
              row = self.extract_submission_data(submission)
              rows.append(row)

        for submission in self.reddit.subreddit(r_sub).hot(limit=256):
            if not submission.is_self and not submission.is_video:
              row = self.extract_submission_data(submission)
              rows.append(row)

        return rows

    def extract_submission_data(self,submission):

      author = None

      if submission.author is not None:
        author = submission.author.name


      row  = {
              'url':submission.url.replace('\\','/'),
              'title': submission.title,
              'submitted_at': datetime.datetime.fromtimestamp(submission.created),
              'updated_at':datetime.datetime.now(),
              'domain': submission.domain,
              'ups': submission.ups,
              'downs': submission.downs,
              'score': submission.score,
              'reddit_id': submission.id,
              'reddit_permalink': submission.permalink,
              'subreddit_name_prefixed':submission.subreddit_name_prefixed,
              'num_comments': submission.num_comments,
              'author': author,
              'num_crossposts': submission.num_crossposts
            }

      return row

    def get_user_submissions(self,user):
        rows = []

        for submission in self.reddit.redditor(user).submissions.new(limit=256):
            if not submission.is_self and not submission.is_video:
              row = self.extract_submission_data(submission)
              rows.append(row)


        return rows

    def get_domain_submissions(self,domain):
        rows = []

        for submission in self.reddit.domain(domain).new(limit=256):
            #print json.dumps(submission,indent=1)
            if not submission.is_self and not submission.is_video:
              row = self.extract_submission_data(submission)
              rows.append(row)
        # for submission in self.reddit.domain(domain).top(limit=256):
        #     #print json.dumps(submission,indent=1)
        #     if not submission.is_self and not submission.is_video:
        #       row = self.extract_submission_data(submission)
        #       rows.append(row)


        return rows

    def scrape_all_tracked_subreddits(self):
      subs_to_check = self.get_tracked_subreddits()
      for sub in subs_to_check:
        try:
          if sub[1]=='subreddit':
            print "checking r/"+ sub[0]
            data = self.get_submissions(r_sub=sub[0])
            self.write_to_articles(data,sub[0])
          elif sub[1]=='user':
            print "checking u/"+ sub[0]
            data = self.get_user_submissions(sub[0])
            self.write_to_articles(data,sub[0])
          elif sub[1]=='domain':
            print "checking domain: "+ sub[0]
            data = self.get_domain_submissions(sub[0])
            self.write_to_articles(data,sub[0])

        except Exception as e:
          print e.message
          traceback.print_exc()






