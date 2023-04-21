import requests
from datetime import datetime
'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''

def main():
    # TODO: Add code to test the functions in this module
    return

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.
    Args:
        apod_date (date): APOD date (Can also be a string formatted as YYYY-MM-DD)
    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """
    try:
        apod_date = datetime.strptime(apod_date, '%M-%m-%d').date()
    except ValueError:
        print("Invalid format for the date provided.")
        return None

    first_apod_date = datetime.strptime('1995-06-16', '%Y-%m-%d').date()
    if apod_date < first_apod_date:
        print("The provided date cannot be before the first APOD date.")
        return None

    today_date = datetime.today().date()
    if apod_date > today_date:
        print("Provided date cannot be from future.")
        return None


    url = f"https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&date={apod_date}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None   

def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.
    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.
    Args:
        apod_info_dict (dict): Dictionary of APOD info from API
    Returns:
        str: APOD image URL
    """
    if apod_info_dict["media_type"] == "image":
        apod_url = apod_info_dict['hdurl'] if "hdurl" in apod_info_dict else apod_info_dict["url"]
    elif apod_info_dict["media_type"] == "video":
        apod_url = apod_info_dict["thumbnail_url"]
    else:
        apod_url = ""

    return apod_url

if __name__ == '__main__':
    main()