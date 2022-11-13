import re
import time
from datetime import datetime  

# {
#     "ObjectId": "ObjectId",
#     "userName": "username",
#     "permalink": "permalink",
#     "comment": "comment",
#     "following_comments (permalink reference)": [], "(need to index permalink)"
# }


def generate_permalink(blogname, title):
    """Generate a permanent link for a blog entry."""
    permalink  = blogname+'.'+re.sub('[^0-9a-zA-Z]+', '_', title)
    return permalink

def generate_comment_permalink():
    """Generate a permanent link for a comment."""
    ts = time.time()
    date_time = datetime.fromtimestamp(ts)
    date_times = str(date_time).split()
    date_permalink = date_times[0] + 'T' + date_times[1]+ 'Z'
    return date_permalink

def process_comment(input):
    """Process a comment and return a list of words."""
    """comment blogname permalink userName commentBody timestamp"""
    words = input.split()
    blogname = words[1]
    permalink = words[2]
    userName = words[3]
    commentBody = words[4]
    timestamp = words[5]
    return blogname, permalink, userName, commentBody, timestamp

def process_delete(input):
    """Process a delete and return a list of words."""
    """delete blogname permalink userName timestamp"""
    words = input.split()
    blogname = words[1]
    permalink = words[2]
    userName = words[3]
    timestamp = words[4]
    return blogname, permalink, userName, timestamp

if __name__ == "__main__":
    # line = input()
    # blogname, permalink, userName, commentBody, timestamp= process_comment(line)
    # print(blogname, " ", permalink, " ", userName, " ", commentBody, " ", timestamp)
    # permalink = generate_perma_link(blogname, title)
    pass
