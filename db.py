"""
This module contains everything needed to interface with the mongodb database.
"""

from pymongo import MongoClient
import datetime
import os

"""Credentials are needed to log into the database"""
user = "discord_user"
pswd = os.environ['MONGO_PASS']

"""
The databse name is the same as the guild name
(except spaces are replaced with underscores)
"""
db_name = "Test_Server"

"""user_data will be used in the future once we add more features"""
collections = ["keywords", "users", "messages", "messages_all"]

"""
This document is a sample of how message docs will look.
The keyword field is for the keyword that caused the message to be flagged.
The timestamp field is the time the message was sent, and will be used to
periodically clear out the database.
"""
message_document_schema = {
  "user": "Charles",
  "keyword": "sir",
  "content": "Hello, there sir",
  "timestamp": datetime.datetime(1954, 6, 7, 11, 40)
}

"""
This document is a sample of how keyword docs will look.
The keywords are what the on_message will actually search for, the category is
just a clever way to organize words to make slang detection easier.
"""
keyword_document_schema = {
  "category": "Homework",
  "keywords": ["hw", "homework", "HW", "Homework"]
}

def connect_to_mongo(user, pswd):
  """
  Returns a client object that can be used to access all data.

  NOTE: This function is slow. Authenticating takes a few seconds at least.
  """
  link = f"mongodb+srv://{user}:{pswd}@discorddata.cmilw.mongodb.net"
  client = MongoClient(link)
  print("Connected successfully to mongodb!")
  return client

def get_db(client_obj, db_name):
  """
  Returns a database object which is used to get data for each guild

  db_name -- is the name of the desired guild with _'s instead of spaces
  """
  return client_obj[db_name]

def get_collection(db_obj, collection_name):
  """Returns a collection contained in a database."""
  return db_obj[collection_name]

def get_messages(collection_obj, user_name):
  """
  Returns the messages flagged by the keywords, with the exception of
  messages authored by the given user.

  This method should be used when creating the newsletter
  """
  return collection_obj.find({"user": {"$ne": user_name}})

def add_all_messages(collection_all_messages, user_name, timestamp, message, message_guild, message_channel):
     document = {
        "user": user_name,
        "content": message,
        "guild": message_guild,
        "channel": message_channel,
        "timestamp": timestamp
     }

     collection_all_messages.insert_one(document)

def add_message(collection_obj, collection_user, user_name, keyword_flagged, message, message_guild, message_channel, timestamp):
  """
  Adds a message document to the database.
  Adds message to the users that contain the keyword that the message was flagged for.
  Returns the timestamp of the document if the transaction was successful.
  """
  document = {
    "user": user_name,
    "keyword": keyword_flagged,
    "content": message,
    "guild": message_guild,
    "channel": message_channel,
    "timestamp": timestamp
  }
  x = collection_obj.insert_one(document)

  '''
  check_if_message_contains_keyword_of_user(collection_user, message)
  '''

def check_if_user_in_db(collection_users, user_name):
    """
    Returns a boolean based on if the user already has a document in the users
    collection

    collection_users -- users collection containing all their keywords and specific messages contaning those keywords

    user_name -- the name of the user who typed the message
    """
    if(collection_users.count_documents({"user": user_name}) > 0):
        return True
    else:
        return False

def update_user_collection_keyword(collection_users, collection_keywords, user_name, guild_id, keyword_category, first_keyword):
    """
    Updates the keywords of a user if they add a keyword into a newly created category or an existing category

    collection_users -- user collection containing each user's documents

    collection_keywords -- keyword collection used to update the user collection everytime a new keyword is created

    user_name -- name of user who wrote the message

    keyword_category -- the category the keywords being added to users keyword list
    """

    if(check_if_user_in_db(collection_users, user_name)):
        collection_users.update_one(
          {"user": user_name, "guild": guild_id},
          {"$push": { "keywords": first_keyword}}
        )
    else:
        document = {
          "user": user_name,
          "guild": guild_id,
          "keywords": [first_keyword]
        }
        collection_users.insert_one(document)

def check_if_message_contains_keyword_of_user(collection_users, message):
    """
    Checks if the message sent contains a keyword of any user in the user collection.
    If it does, add the message to the messages list in that specific user's document
    """
    cursor_user = collection_users.find({})
    for document in cursor_user:
        for keyword in document["keywords"]:
            if keyword in message:
                collection_users.update_one(
                  {"keywords": keyword},
                  {"$push": { "messages": message}}
                )

def create_keyword_category(collection_keywords, collection_users, commands_author, new_keyword_category, first_keyword, guild_id):
  """
  Creates a new keyword document populated with an intital keyword. More can be added later
  Also adds the keyword to the keywords list of the user that called on the command

  commands_author -- refers to the user name who called on the command

  new_keyword_category -- refers to the general idea (i.e. "Homework").

  first_keyword -- is the first keyword to populate the document (i.e. "hw" and "homework").

  Returns the timestamp of the document if the transaction was successful.
  """

  document = {
    "category": new_keyword_category,
    "guild": guild_id,
    "keywords": [first_keyword]
  }
  x = collection_keywords.insert_one(document)

  update_user_collection_keyword(collection_users, collection_keywords, commands_author, guild_id, new_keyword_category, first_keyword)

  return x.inserted_id.generation_time

def add_keyword(collection_keywords, collection_users, user_name, existing_keyword_category, new_keyword, guild_id):
  """
  Adds a keyword to an existing keyword document.
  Also adds keyword to the keyword list of the user that called on the command

  new_keyword -- the keyword you want to add (i.e. "hw" and "homework").

  Returns nothing.
  """
  collection_keywords.update_one(
    {"category": existing_keyword_category, "guild": guild_id},
    {"$push": { "keywords": new_keyword}}
  )

  update_user_collection_keyword(collection_users, collection_keywords, user_name, guild_id, existing_keyword_category, new_keyword)

'''
Adds every keyword from a category to a user's keyword list

collection_keywords - collection containing all the keywords

collection_users - user collection with each users keywords and messages corresponding to those keywords

user_name - name of the user

category - The category that they want to add the keywords from
'''
def add_all_keywords_from_category_to_user_keywords_list(collection_keywords, collection_users, user_name, category, guild_id):
    keywords_in_category = []
    keywords_in_user = []
    keyword_list = []
    category_keywords = collection_keywords.find({"category": category, "guild": guild_id})
    user_keywords = collection_users.find({"user": user_name, "guild": guild_id})

    if(check_if_user_in_db(collection_users, user_name)):
        for document in category_keywords:
            for kw in document["keywords"]:
                keywords_in_category.append(kw)

        for document2 in user_keywords:
            for ukw in document2["keywords"]:
                keywords_in_user.append(ukw)

        for kw2 in keywords_in_category:
            if(kw2 not in keywords_in_user):
                collection_users.update_one(
                    {"user": user_name},
                    {"$push": { "keywords": kw2}}
                )
    else:
        for document in category_keywords:
            for word in document["keywords"]:
                keyword_list.append(word)
        document = {
          "user": user_name,
          "keywords": keyword_list
        }
        collection_users.insert_one(document)

'''
Returns a list of the keyword categories
'''
def get_existing_keyword_categories(collection_keywords, guild_id):
    cursor = collection_keywords.find({"guild": guild_id})
    categories = []
    for document in cursor:
        categories.append(document["category"])
    return categories

'''
Returns the list of keywords in a specific category_keywords
'''
def get_existing_keywords_in_specific_category(collection_keywords, category, guild_id):
    cursor = collection_keywords.find({"category": category, "guild": guild_id})

    keywords = []
    for document in cursor:
        for word in document["keywords"]:
            keywords.append(word)
    return keywords

'''
Returns keywords of the user
'''
def get_keywords_of_user(collection_users, user_name, guild_id):
  """
  Returns the list of keywords for each user.
  """
  cursor = collection_users.find({"user": user_name, "guild": guild_id})
  keywords = []
  for document in cursor:
    for word in document["keywords"]:
      keywords.append(word)
  return keywords

def get_keywords(collection_keywords, guild_id):
  """
  Returns the list of all keywords to search for.
  """
  cursor = collection_keywords.find({"guild": guild_id})
  keywords = []
  for document in cursor:
    for word in document["keywords"]:
      keywords.append(word)
  return keywords

'''
Returns all the messages from a specific message_channel

collection_all_messages - messages collection that stores every message

guild_id - id of guild used to make sure the correct messages are sent to the user

channel - the channel they want the messages to be from
'''
def get_all_messages(collection_all_messages, guild_id, channel):
    message = ""
    day = get_current_day(collection_all_messages, guild_id, channel)
    month = get_current_month(collection_all_messages, guild_id, channel)
    year = get_current_year(collection_all_messages, guild_id, channel)

    documents = collection_all_messages.find({"channel": channel, "guild": guild_id})
    documents = collection_all_messages.find({"guild": guild_id, "channel": channel})

    for document in documents:
        if(document["timestamp"].strftime("%Y") == year):
            if(document["timestamp"].strftime("%m") == month):
                if(document["timestamp"].strftime("%d") == day):
                    message += document["content"]
                    message += " "

    return message

def get_all_messages_from_specific_day(collection_all_messages, guild_id, channel, day):
    message = ''
    year = get_current_year(collection_all_messages, guild_id, channel)
    month = get_current_month(collection_all_messages, guild_id, channel)

    documents = collection_all_messages.find({"guild": guild_id, "channel": channel})
    for document in documents:
        if(document["timestamp"].strftime("%Y") == year):
            if(document["timestamp"].strftime("%m") == month):
                if(document["timestamp"].strftime("%d") == day):
                    message += document["content"]
                    message += " "

    return message


def get_messages_with_keyword(collection_messages_keywords, guild_id, channel, keyword):
    message = ''
    day = get_current_day(collection_messages_keywords, guild_id, channel)
    year = get_current_year(collection_messages_keywords, guild_id, channel)
    month = get_current_month(collection_messages_keywords, guild_id, channel)

    documents = collection_messages_keywords.find({"guild": guild_id, "channel": channel, "keyword": keyword})
    for document in documents:
        if(document["timestamp"].strftime("%Y") == year):
            if(document["timestamp"].strftime("%m") == month):
                if(document["timestamp"].strftime("%d") == day):
                    message += document["content"]
                    message += " "

    return message

def get_messages_with_keyword_specific_day(collection_messages_keywords, guild_id, channel, keyword, day):
    message = ''
    year = get_current_year(collection_messages_keywords, guild_id, channel)
    month = get_current_month(collection_messages_keywords, guild_id, channel)

    documents = collection_messages_keywords.find({"guild": guild_id, "channel": channel, "keyword": keyword})
    for document in documents:
        if(document["timestamp"].strftime("%Y") == year):
            if(document["timestamp"].strftime("%m") == month):
                if(document["timestamp"].strftime("%d") == day):
                    message += document["content"]
                    message += " "

    return message


def get_messages_with_category(collection_messages_keywords, collection_keywords, guild_id, channel, category):
    message = ''
    day = get_current_day(collection_messages_keywords, guild_id, channel)
    year = get_current_year(collection_messages_keywords, guild_id, channel)
    month = get_current_month(collection_messages_keywords, guild_id, channel)

    keyword_list = get_existing_keywords_in_specific_category(collection_keywords, category, guild_id)

    documents = collection_all_messages.find({"guild": guild_id, "channel": channel})
    for document in documents:
        if(document["timestamp"].strftime("%Y") == year):
            if(document["timestamp"].strftime("%m") == month):
                if(document["timestamp"].strftime("%d") == day):
                    for key in keyword_list:
                        if key in document["content"]:
                            message += document["content"]
                            message += " "

    return message


def get_messages_with_category_specific_day(collection_messages_keywords, collection_keywords, guild_id, channel, category, day):
    message = ''
    year = get_current_year(collection_messages_keywords, guild_id, channel)
    month = get_current_month(collection_messages_keywords, guild_id, channel)

    keyword_list = get_existing_keywords_in_specific_category(collection_keywords, category, guild_id)

    documents = collection_messages_keywords.find({"guild": guild_id, "channel": channel})
    for document in documents:
        if(document["timestamp"].strftime("%Y") == year):
            if(document["timestamp"].strftime("%m") == month):
                if(document["timestamp"].strftime("%d") == day):
                    for key in keyword_list:
                        if key in document["content"]:
                            message += document["content"]
                            message += " "

    return message

def get_current_day(collection_all_messages, guild_id, channel):
    now = datetime.datetime.now()
    day = now.strftime("%d")

    return day

def get_current_month(collection_all_messages, guild_id, channel):
    now = datetime.datetime.now()
    month = now.strftime("%m")

    return month

def get_current_year(collection_all_messages, guild_id, channel):
    now = datetime.datetime.now()
    year = now.strftime("%Y")

    return year

def main():
  # Connects to database and gets collection (slow)
  client = connect_to_mongo(user, pswd)
  # Gets a database (fast)
  test_server_db = get_db(client, db_name)
  # Gets a collection of data (fast)
  keywords_collection = get_collection(test_server_db, "keywords")
  # Gets and prints out the messages in the collection (fast)
  keywords = get_keywords(keywords_collection)
  for w in keywords:
    print(w)

"""
This is just some code for testing.
If you want to test anything, just uncomment main()
"""

# main()
