import goodreads_api_client as gr 
import os
import json
import requests
import sqlite3
import plotly.graph_objs as go
from os import path

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict, CACHE_FILENAME):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

    
def make_request(book_name):
#     '''Make a request to the Web API using the baseurl and params
    
#     Parameters
#     ----------
#     baseurl: string
#         The URL for the API endpoint
#     params: dictionary
#         A dictionary of param:value pairs
    
#     Returns
#     -------
#     dict
#         the data returned from making the request in the form of 
#         a dictionary
#     '''
    # response = requests.get(baseurl, params=params, auth=oauth)
    
    params= {'key':Goodreads['key'], 'v': 2, 'id': myuserid}
    response = requests.Request('GET', base_url, params=params).prepare().url

def load_cache():
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()

    except:
        cache = {}
    return cache

CACHE_DICT = load_cache()

def make_url_request_using_cache_json(url, cache):
    ''' read the cache file to find the content or make url request using url from API and add json of the web page to the cache

    Parameters
    ----------
    url
        str:the url will be reading content from or use to find the content in cache file
    cache
        dic:the cache content

    Returns
    -------
    cache[url]
        str:the content of the url
    ''' 
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]     # we already have it, so return it
    else:
        print("Fetching")
        response = requests.get(url) # gotta go get it
        cache[url] = response.json() # add the json of the web page to the cache
        save_cache(cache)          # write the cache to disk
        return cache[url]          # return the text, which is now in the cache
    

    if __name__ == "__main__":
        bk = gbooks()
        bk.search("Harry Potter")
        print(bk)
        create_db()

#Caching goodreads data
list_book = []
def get_gr_data():
    '''  make url request using goodreads url from API and add json of the web page to the cache

    Parameters
    ----------
    url
        str:the url will be reading content from or use to find the content in cache file
    cache
        dic:the cache content

    Returns
    -------
    cache[url]
        str:the content of the url
    ''' 
    CACHE_FILENAME = 'gr_books_cache.json'
    CACHE_DICT = {}

    client = gr.Client(developer_key = 'dSWuUFXOI6o5AquwRM2gew')
    keys_wanted = ['title', 'average_rating']

    if not path.exists(CACHE_FILENAME):
        for i in range(1, 200):
            try: 
                book = client.Book.show(i)
                reduced_book = {k:v for k, v in book.items() if k in keys_wanted}
                # list_book.append(reduced_book)
                CACHE_DICT[reduced_book.get("title","")] = reduced_book.get("average_rating", "")
            except Exception as e: print(e)
            # print(list_book)
        with open(CACHE_FILENAME, 'w') as outfile:
            json.dump(CACHE_DICT, outfile)
        save_cache(CACHE_DICT, CACHE_FILENAME)


    #Caching Google Books data
def get_google_data():
    '''  make url request using google books url from API and add json of the web page to the cache

    Parameters
    ----------
    url
        str:the url will be reading content from or use to find the content in cache file
    cache
        dic:the cache content

    Returns
    -------
    cache[url]
        str:the content of the url
    ''' 
    # url = "https://www.googleapis.com/books/v1/volumes?q=flowers+inauthor:keyes&key=AIzaSyAyl9F9FiNS8krGJJEQZZ357UlFwTORXVo"

    CACHE_DICT = {}
    payload = {}
    headers= {}
    CACHE_FILENAME = "google_books_cache.json"

    if not path.exists(CACHE_FILENAME):
        # go from 0 - 200 in increments of 5. This will be used in the end of the url as str(i) to make this number the start index
        for i in range(0,200,5):
            url="https://www.googleapis.com/books/v1/volumes?q=a&key=AIzaSyAu0Y1TqBO60ucW3B1al9Yberfk-6ML9Zs&startIndex="+str(i)

            try:
                response = requests.request("GET", url, headers=headers, data = payload)
                ParsedJson = json.loads(response.text)

                for book in ParsedJson["items"]:
                    volumeInfo = book["volumeInfo"]

                        # In this line we are checking to see if the book actually has a title and an average rating
                    if "title" in volumeInfo.keys() and "averageRating" in  volumeInfo.keys():
                        CACHE_DICT[volumeInfo["title"]] =  volumeInfo["averageRating"]  # This line adds the title as the key of the dictionary and the authors as that key
            except Exception as e: print(e)

        save_cache(CACHE_DICT, CACHE_FILENAME)

DB_NAME="sqlLite.sql"
def create_gr_db():
    '''  Creates table to store goodread data 

    Parameters
    ----------
    None

    Returns
    -------
    Returns table headings
    ''' 
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    drop_book_sql = 'DROP TABLE IF EXISTS "Goodreads_Books_info"'
    create_book_sql = '''
        CREATE TABLE IF NOT EXISTS "Goodreads_Books_info" (
            "ID"INTEGER NOT NULL,
            "Average_Rating" REAL NOT NULL,
            "Title" TEXT NOT NULL,
            PRIMARY KEY("ID","Title"))'''
    cur.execute(drop_book_sql)
    cur.execute(create_book_sql)
    conn.commit()
    conn.close()

def add_gr_data_to_sqlite():
    ''' Populates the table using the goodread cache file

    Parameters
    ----------
    None

    Returns
    -------
    Returns populated table with the cache content
    ''' 

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    insert_books_sql = '''
        INSERT INTO Goodreads_Books_info
        VALUES (?,?,?)'''
    ID = 0
    with open('gr_books_cache.json') as data_file:
        list_book = json.load(data_file)
        for title in list_book:
            average_rating = list_book[title]
            ID += 1
        # cur.execute(insert_books_sql,[ID,title,average_rating])

        # title = i["title"]
        # try:
        #     average_rating = i["averageRating"]
        # except: 
        #     continue
        # ID += 1
        # cur.execute(insert_books_sql,[ID,average_rating,title])

    conn.commit()
    conn.close()
add_gr_data_to_sqlite()
def create_google_books_db():
    '''  Creates table to store google data 

    Parameters
    ----------
    None

    Returns
    -------
    Returns table headings
    ''' 
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    drop_book_sql = 'DROP TABLE IF EXISTS "Books_info"'
    create_book_sql = '''
        CREATE TABLE IF NOT EXISTS "Books_info" (
            "ID"INTEGER NOT NULL,
            "Average_Rating" REAL NOT NULL,
            "Title" TEXT NOT NULL,
            PRIMARY KEY("ID","Title"))'''
    cur.execute(drop_book_sql)
    cur.execute(create_book_sql)
    conn.commit()
    conn.close()

def add_google_data_to_sqlite():
    ''' Populates the table using the goodread cache file

    Parameters
    ----------
    None

    Returns
    -------
    Returns populated table with the cache content
    ''' 
    google_book = []
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    insert_books_sql = '''
        INSERT INTO Books_info
        VALUES (?,?,?)'''
    ID = 0
    with open('google_books_cache.json') as data_file:
        list_book = json.load(data_file)
        # google_book.append(list_book)
        for title in list_book:
            gr_rating = list_book[title]
            average_rating = gr_rating
            # average_rating = [float(i) for i in average_rating]
            ID += 1
    cur.execute(insert_books_sql,[ID,average_rating,title])
    conn.commit()
    conn.close()

def scatter_plotly(v_1):
    ''' Assigns variables to varies ratings

    Parameters
    ----------
    Average Rating: float

    Returns
    -------
    Returns scatter plot with number of books per rating
    ''' 
    c1 = 0
    c2=0
    c3=0
    c4=0
    xvals = ['1-2','2-3','3-4','4-5']
    for score in v_1:
        if 1<=score<2:
            c1 +=1
        elif 2<=score<3:
            c2 +=1
        elif 3<=score<4:
            c3 += 1
        else:
            c4 +=1
    yvals = [c1,c2,c3,c4]
    scatter_data = go.Scatter(x=xvals, y=yvals)
    basic_layout = go.Layout(title="A Scatter(Line) Plot")
    fig = go.Figure(data=scatter_data, layout=basic_layout)
    fig.show()

# if __name__ == "__main__":
def get_split(v):
    ''' Assigns variables to varies ratings to build the bar chart

    Parameters
    ----------
    Average Rating: float

    Returns
    -------
    Returns bar chart with number of books per rating
    '''
    xvals = ['1-2','2-3','3-4','4-5']
    c1 = 0
    c2=0
    c3=0
    c4=0
    for score in v:
        if 1<=score<2:
            c1 +=1
        elif 2<=score<3:
            c2 +=1
        elif 3<=score<4:
            c3 += 1
        else:
            c4 +=1
    yvals = [c1,c2,c3,c4]
    bar_data = go.Bar(x=xvals, y=yvals)
    basic_layout = go.Layout(title="A Bar Graph")
    fig = go.Figure(data=bar_data, layout=basic_layout)
    fig.show()


def main():
    ''' Prompts the user to enter information
    
    Parameters
    ----------
    NONE

    Returns
    -------
    Returns bar chart and scatter chart according to the user input 
    '''
    gr_rating = []
    google_rating = []
    user_input=input("Enter a database (Goodreads or Google Books) or 'exit': ")
    print(user_input)
    if user_input =="exit":
        print ("Goodbye!")
            # break
    elif user_input == "Google Books":
        get_google_data()
        ID = 0
        with open('google_books_cache.json') as data_file:
            book_list = json.load(data_file)
            for title in book_list:
                average_rating = book_list[title]
                google_rating.append(average_rating)
                ID += 1
                print(ID, title, average_rating)
            while True:
                new_input=input("Type rating for detail graph or 'exit' or 'back': ")
                print(new_input)
                if new_input=="exit":
                    print("Godbye!")
                    status=False
                    break
                elif new_input=="back":
                    print()
                    break
                elif new_input=="rating":
                    get_split(google_rating)
                    scatter_plotly(google_rating)
    elif user_input == "Goodreads":
        get_gr_data()
        ID = 0
        with open('gr_books_cache.json') as data_file:
            list_book = json.load(data_file)
            for title in list_book:
                average_rating = list_book[title]
                ID += 1
                print(ID, title, average_rating)
                gr_rating.append(average_rating)
                gr_rating = [float(i) for i in gr_rating]
        while True:
            print()
            new_input=input("Type rating for detail graph or 'exit' or 'back': ")
            if new_input=="exit":
                print("Godbye!")
                status=False
                break
            elif new_input=="back":
                print()
                break
            elif new_input=="rating":
                get_split(gr_rating)
                scatter_plotly(gr_rating)
    elif not user_input == "Goodreads":
        print ("Error! Please enter a valid name")
    elif not user_input == "Google Books":
        print ("Error! Please enter a valid name")
    else:
        print ("Error! Please enter the correct name")
main()