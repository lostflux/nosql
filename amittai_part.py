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
            commentBody: string
        }
    ]
}

We may want to track an index on blogName.
Since we need to find posts by blogName when showing a blog.
"""

from pymongo import MongoClient, ASCENDING    # For MongoDB
import re                                     # For regular expressions.
import shlex                                  # For splitting strings.
from sys import stderr                        # For printing to stderr.
from datetime import datetime                 # For timestamps.

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
        self.client = MongoClient()
        self.db = self.client.blog
        self.collection = self.db.posts

        # clear the collection (just in case)
        self.db.posts.drop()

        # create index on blogName
        self.db.posts.create_index([('blogName', ASCENDING)])

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
        print(f"args: {args}", file=stderr)
        if len(args) == 0:
            print("ERROR: No command given.", file=stderr)
            return

        command = args[0]

        if command == "post":

            if len(args) != 6:
                print("ERROR: Not enough arguments.", file=stderr)
                return

            blog_name = args[1]
            user_name = args[2]
            title = args[3]
            post_body = args[4]
            tags = args[5].split(",")
            time_stamp = str(datetime.now())

            # DEBUG
            print(
                f"""
                    blog_name: {blog_name}
                    user_name: {user_name}
                    title: {title}
                    post_body: {post_body}
                    tags: {tags}
                    time_stamp: {time_stamp}
                """
            )
            self.add_post(blog_name, user_name, title, post_body, tags, time_stamp)
        
        elif command == "show":
            if len(args) != 2:
                print("ERROR: Not enough or too many arguments.\nPlease only provide the blog name.", file=stderr)
                return

            blog_name = args[1]
            self.show_posts(blog_name)

        elif command == "comment":
            pass

        elif command == "delete":
            pass

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

        print(f"post: {post}")
        # insert post
        try:
            self.db.posts.insert_one(post)
            print(f"Count of posts: {self.db.posts.count_documents()}") # DEBUG
        except Exception as e:
            print(f"ERROR: {e}", file=stderr)

    def show_posts(self, blog_name):
        """
            Shows all posts in a blog.
        """
        
        # Find all posts for the given blog name.
        posts = self.db.posts.find({"blogName": blog_name})
        print(f"Found {posts.count()} posts for blog {blog_name}") # DEBUG

        if posts is None:
            print("No posts found.", file=stderr)
            return
        
        message = f"""\n\nin {blog_name.title()}\n\n"""
        print(posts) # DEBUG

        for post in posts:
            print(post) #DEBUG

            message += f"""

                \t - - - -

                \t\t title: \t{post['title']}
                \t\t userName: \t{post['userName']}
                \t\t timestamp: \t{post['timestamp']}
                \t\t permalink: \t{post['permalink']}
                \t\t body:
                \t\t\t {post['postBody']}


                \t\t - - - -
            """

            for comment in post['comments']:
                message += f"""
                    \t\t\t userName: \t{comment['userName']}
                    \t\t\t permalink: \t{comment['permalink']}
                    \t\t\t comment:
                    \t\t\t\t {comment['commentBody']}
                """

        print(message)

        

def main():
    server = MongoBlogServer()
    while True:
        request = input("Enter request: ")
        server.handle_request(request)

if __name__ == "__main__":
    main()
