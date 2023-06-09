""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
from datetime import date, datetime, timedelta
import os
import sqlite3
import image_lib
import inspect
import sys
import requests
import re
from urllib.parse import urlparse

# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database

def main():
    ## DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()    

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # Set the APOD as the desktop background image
    if apod_id != 0:
        image_lib.set_desktop_background_image(apod_info['file_path'])

def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.

    Returns:
        date: APOD date
    """
    if len(sys.argv) > 1:
        apod_date = sys.argv[1]

    # TODO: Complete function body
        try:
            apod_date = datetime.strptime(apod_date,'%Y-%m-%d').date()
        except ValueError:
            print("Error: Invalid date format!")
            sys.exit(1)
    else:
        apod_date = date.today()
    return apod_date

def get_script_dir():
    """Determines the path of the directory in which this script resides

    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    return os.path.dirname(script_path)

def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.

    Args:
        parent_dir (str): Full path of parent directory    
    """
    global image_cache_dir
    global image_cache_db
    # TODO: Determine the path of the image cache directory
    # TODO: Create the image cache directory if it does not already exist
    # TODO: Determine the path of image cache DB
    # TODO: Create the DB if it does not already exist
    cache_dir = os.path.join(parent_dir, "image_cache")
    db_path = os.path.join(cache_dir, "image_cache.db")

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS image_cache (
            url TEXT,
            filepath TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    return cache_dir, db_path

def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """
    print("APOD date:", apod_date.isoformat())
    # TODO: Download the APOD information from the NASA API
    # TODO: Download the APOD image
    # TODO: Check whether the APOD already exists in the image cache
    # TODO: Save the APOD file to the image cache directory
    # TODO: Add the APOD information to the DB
    api_endpoint = "https://api.nasa.gov/planetary/apod"
    api_key = "api_key"
    param = {
        "date": apod_date,
        "api_key": api_key
    }

    response = requests.get(api_endpoint, params=param)

    if response.status_code != 200:
        print("Error: Request returned status code.")
        return 0

    # APOD information from response
    apod_info = response.json()
    apod_url = apod_info["url"]
    apod_title = apod_info["title"]
    apod_explain = apod_info["explaination"]

    parent_dir = "C:\Users\dhava\Documents\GitHub\COMP593_FinalProject"
    cache_dir = os.path.join(parent_dir, "image_cache")
    db_path = os.path.join(cache_dir, "image_cache.db")

    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filepath FROM image_cache WHERE url = ?", (apod_url))
    result = cursor.fetchone()
    if result is not None:
        conn.close()
        return result[0]
    
    response = requests.get(apod_url)
    if response.status_code != 200:
        print("Error: Request returned status code.")
        conn.close()
        return 0
    

    filename = os.path.basename(apod_url)
    filepath = os.path.join(cache_dir,filename)
    with open(filename, "wb") as file:
        file.write(response.content)

    cursor.execute("INSERT INTO image_cache (url, filepath, title, explaination) VALUES (?, ?, ?, ?)", (apod_url, filepath, apod_title, apod_explain))
    conn.commit()
    apod_id = cursor.lastrowid
    conn.close()

    return apod_id


def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful.  Zero, if unsuccessful       
    """
    conn = sqlite3.connect('image_cache/image_cache.db')
    c = conn.cursor()

    try:
        c.execute("INSERT INTO apod_cache (title, explaination, file_path, sha256) VALUES (?, ?, ?, ?)", (title, explanation, file_path, sha256))
        conn.commit()
        apod_id = c.lastrowid
    except sqlite3.Error as e:
        print(f"ERROR inserting APOD information into cache database: {e}")
        conn.close
    # TODO: Complete function body
    return 0

def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    # TODO: Complete function body
    conn = sqlite3.connect('image_cache/image_cache.db')
    c = conn.cursor()

    c.execute("SELECT id FROM apod_cache WHERE sha256 = ?", (image_sha256))
    resutlt = c.fetchone()
    if resutlt :
        apod_id = resutlt[0]
    else:
        apod_id = 0
    conn.close()
    return apod_id

def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    # TODO: Complete function body
    url_parts = urlparse(image_url)
    file_extension = os.path.splitext(url_parts.path)[1]

    file_name = re.sub(r'[^\w\s', ' ', image_title).strip().replace(' ','_')

    file_path = os.path.join('image_cache', f'{file_name}{file_extension}')

    return file_path

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """
    # TODO: Query DB for image info
    # TODO: Put information into a dictionary
    conn = sqlite3.connect('image_cache/apod_cache.db')
    cursor = conn.cursor()

    cursor.execute("SELECT title, explaination, file_path FROM apod_cache WHERE id=?", (image_id))
    result = cursor.fetchone()
    apod_info = {
        'title': result[0], 
        'explanation': result[1] ,
        'file_path': result[2],
    }
    conn.close()

    return apod_info

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """
    # TODO: Complete function body
    # NOTE: This function is only needed to support the APOD viewer GUI
    conn = sqlite3.connect('image_cache/apod_cache.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM apod_cache")
    result = cursor.fetchall()
    title = [result[0] for result in result]
    conn.close
    return title

if __name__ == '__main__':
    main()