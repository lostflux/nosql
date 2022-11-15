#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MongoDB Schema:
{
    _id: int (auto increment) # blog post id,
    *blogName : string,
    userName : string,
    title: string,
    postBody: string,
    tags: [string],
    timestamp: date? (auto generated),
    permalink: string (auto generated),
    comments: [
        { 
            permalink: date? (auto generated),
            postBody: string
        }
    ]
}

We may want to track an index on blogName.
Since we need to find posts by blogName when showing a blog.

MongoDB Schema for Comments:
{
    "ObjectId": "ObjectId",
    "userName": "username",
    "permalink": "permalink", (index this)
    "commentBody": "comment",
    "comments (permalink reference)": [],
}

"""

from pymongo import MongoClient, ASCENDING    # For MongoDB
import re                                     # For regular expressions.
import shlex                                  # For splitting strings.
from sys import stderr                        # For printing to stderr.
from datetime import datetime                 # For timestamps.
import time
from dbconfig import read_db_config           # For reading in mongodb config.

"""
  NOTE: collection name = "blog"
"""

class MongoBlogServer:
    """
        A MongoDB-backed blog server.
    """

    def __init__(self):
        """
            Connect to the MongoDB server.
        """
        self.config = read_db_config()
        self.client = MongoClient(self.config['host'])
        self.db = self.client.blog
        self.collection = self.db.posts

        # clear the collection (just in case)
        self.db.posts.drop()

        # create index on blogName
        self.db.posts.create_index([('blogName', ASCENDING)])
        self.db.posts.create_index([('permalink', ASCENDING)])

    def handle_request(self, request: str):
        """
            Handles a request from the client.

            Parameters
            ----------
            `request` : str
                The request from the client.

                Valid requests:

                    `post blogName userName title postBody tags timestamp`

                    `show blogName`

                    `comment blogName permalink userName commentBody timestamp`

                    `delete blogName permalink userName timestamp`
        """
        args = shlex.split(request)
        # print(f"args: {args}", file=stderr)
        if len(args) == 0:
            print("ERROR: No command given.", file=stderr)
            return

        command = args[0]

        if command == "post":

            if len(args) != 7:
                print("ERROR: Not enough arguments.", file=stderr)
                return

            blog_name = args[1].lower()
            user_name = args[2]
            title = args[3]
            post_body = args[4]
            tags = args[5].split(",")
            time_stamp = args[6]
            self.add_post(blog_name, user_name, title, post_body, tags, time_stamp)
        
        elif command == "show":
            if len(args) != 2:
                print("ERROR: Not enough or too many arguments.\nPlease only provide the blog name.", file=stderr)
                return

            blog_name = args[1]
            self.show_posts(blog_name)

        elif command == "comment":
            if len(args) != 6:
                print("ERROR: Not enough or too many arguments.", file=stderr)
                return
            blog_name = args[1].lower()
            post_perma_link = args[2]
            user_name = args[3]
            comment_body = args[4]
            time_stamp = args[5]
            self.add_comment(post_perma_link, user_name, comment_body, time_stamp)

        elif command == "delete":
            if len(args) != 5:
                print("ERROR: Not enough or too many arguments.", file=stderr)
                return
            blog_name = args[1].lower()
            permalink = args[2]
            user_name = args[3]
            time_stamp = args[4]
            self.delete_post(blog_name, permalink, user_name, time_stamp)
        
        elif command == "exit":
            print("Exiting...")
            exit(0)

        else:
            return "Invalid request: " + request

    def add_post(self, blog_name, user_name, title, post_body, tags, time_stamp):
        """
            Adds a post to the blog.
        """
        # create permalink
        permalink = blog_name + "." + re.sub(r"[^0-9a-zA-Z]+", "_", title)

        # create post
        post = {
            'blogName': blog_name,
            'userName': user_name,
            'title': title,
            'postBody': post_body,
            'tags': tags,
            'timestamp': time_stamp,
            'permalink': permalink,
            'comments': [ ]
        }
        # insert post
        try:
            self.db.posts.insert_one(post)
        except Exception as e:
            print(f"ERROR: {e}", file=stderr)

    def show_posts(self, blog_name):
        """
            Shows all posts in a blog.
        """
        
        # Find all posts for the given blog name.
        posts = self.db.posts.find({"blogName": blog_name})

        if posts is None:
            print("No posts found.", file=stderr)
            return
        
        message = f"""\n\nin {blog_name.title()}\n\n"""

        for post in posts:
            print(post.__class__.__name__)
            message += f"""

                - - - -

                  title: \t{post['title']}
                  userName: \t{post['userName']}
                  timestamp: \t{post['timestamp']}
                  permalink: \t{post['permalink']}
                  body:
                      {post['postBody']}


                  - - - -
            """

            for comment_permalink in post['comments']:
                # comment = self.db.posts.find_one({"permalink": comment_permalink})
                message += self.show_comment(comment_permalink)
                # message += f"""
                #         userName: \t{comment['userName']}
                #         permalink: \t{comment['permalink']}
                #         comment:
                #            {comment['commentBody']}
                # """

        print(message)
    def show_comment(self, comment_permalink: str, shift=3):
        """
            Shows all comments for a post.
        """
        
        comment = self.db.posts.find_one({"permalink": comment_permalink})
        comment_string = f"""
                      userName: \t{comment['userName']}
                      permalink: \t{comment['permalink']}
                      comment:
                          {comment['commentBody']}
        """

        # shift 
        if len(comment["comments"]) > 0:
            for comment_permalink in comment["comments"]:
                sub_comment = ("\n" + (' ' * shift)).join(self.show_comment(comment_permalink, shift+3).split("\n"))
                comment_string += f"""
                        - - - -
                             {sub_comment}
                    """

        return comment_string
                

    # def generate_comment_permalink(self, time_stamp):
    #     """Generate a permanent link for a comment."""
    #     ts = time.time()
    #     date_time = datetime.fromtimestamp(ts)
    #     date_times = str(date_time).split()
    #     date_permalink = date_times[0] + 'T' + date_times[1][:-3]+ 'Z'
    #     return date_permalink

    def add_comment(self, post_permalink, user_name, comment_body, time_stamp):
        """Add a comment to a post."""
        # create permalink
        permalink = time_stamp

        # create comment
        comment = {
            'userName': user_name,
            'permalink': permalink,
            'postBody': comment_body,
            'comments': []
        }

        try:
            # insert comment into the posts
            self.db.posts.insert_one(comment)
            # insert permalink of this comment to the post using post_perma_link
            self.db.posts.update_one({"permalink": post_permalink}, {"$push": {"comments": permalink}})
        except Exception as e:
            print(f"ERROR: {e}", file=stderr)

    def delete_post(self, blogname, permalink, user_name, timestamp):
        """
            Delete a post from a blog.
            delete blogname permalink userName timestamp
        """
        message = "deleted by " + user_name

        try:
            # delete the post by update the postbody
            # for both the post and the comment in the postBody
            self.db.posts.update_one({"permalink": permalink},{"$set":{"postBody": message}})
        except Exception as e:
            print(f"ERROR: {e}", file=stderr)

def main():
    server = MongoBlogServer()
    while True:
        try:
            request = input("Request? ")
            if (len(request)) == 0:
                print()     # force a new line before next prompt
                continue
            print(f"\nUser Request: {request}")
            server.handle_request(request)
        except EOFError as e:
            server.handle_request("exit")
        except Exception as e:
            print(f"{e.__class__.__name__}: {str(e)}", file=stderr)
            exit()

def test_main(file=None):
    """
        Same as `main`, but allows you to paste multiple lines in the terminal.

        Also allows you to specify file to read.

        After processing the file, it will enter the main terminal loop.
    """
    server = MongoBlogServer()
    try:
        if file:
            print(f"Reading from file: {file}")
            with open(file, 'r') as f:
                for request in f:
                    print(f"\nUser Request: {request}")
                    server.handle_request(request)

        print("Reading from terminal.")
        while True:
            request = input("Request? ")
            if (len(request)) == 0:
                print()     # force a new line before next prompt
                continue
            print(f"\nUser Request: {request}")
            server.handle_request(request)
    except EOFError as e:
        server.handle_request("exit")
    except Exception as e:
        print(f"{e.__class__.__name__}: {str(e)}", file=stderr)
        exit()

if __name__ == "__main__":
    test_main(file="tests.in")
    # main()
