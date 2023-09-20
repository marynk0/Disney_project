#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#import libraries
from bs4 import BeautifulSoup as bs
import requests 
import time
import datetime
import pandas as pd
import pprint

import smtplib


# In[ ]:


page = requests.get("https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films")

#convert to beautiful soup object
soup = bs(page.content)

#print out the HTML
contents = soup.prettify()
print(contents)


# In[ ]:


#find all elements in the page
td_elements = soup.find_all('td')
print(td_elements)


# In[ ]:


#Just checking
# iterate over each <td> element and extract the title
for td in td_elements:
    title_element = td.find('a')
    if title_element:
        title = title_element.get('title')
        print(title)


# In[ ]:


# iterate over each <td> element
for td in td_elements:
    # find the first <a> element within the <td> element
    link_element = td.find('a')

    # check if <a> element exists
    if link_element:
        # get the title and href attributes
        title = link_element.get('title')
        href = link_element.get('href')

        # print the title and link
        print("Title:", title)
        print("Link:", href)


# In[ ]:


# Function to extract actual content value
def actual_content_value(row_data):
    # Remove all sup tags
    for sup in row_data.find_all("sup"):
        sup.decompose()
    # Check if row has a list <li> in the HTML
    if row_data.find("li"):
        return [li.get_text(strip=True).replace('\n', ' ') for li in row_data.find_all("li")]
    #check for <br> and split accordingly
    elif row_data.find("br"):
        return [text for text in row_data.stripped_strings]
    else:
        return row_data.find("td").get_text(strip=True).replace('\n', '').replace('\xa0', ' ')
def get_info_box(url):
    page = requests.get(url)

    # convert to beautiful soup object
    soup = bs(page.content)

    # extract all the rows
    info_box = soup.find(class_="infobox vevent")
    info_rows = info_box.find_all("tr")

    # Create an empty dictionary to store the data
    movie_info = {}

    for index, row in enumerate(info_rows):
        if index == 0:
            movie_info['title'] = row.find("th").get_text().strip()
        elif index == 1:
            continue
        else:
            content_key = row.find("th").get_text(" ", strip=True).replace('\n', ' ')
            content_value = actual_content_value(row)
            movie_info[content_key] = content_value

            
                # Replace '\xa0' with a space in the release date value
        release_date_key = 'Release date' if 'Release date' in movie_info else 'Release dates'
        modified_release_date = movie_info.get(release_date_key, [''])[0].replace('\xa0', ' ')

        # Update the release date value in the dictionary
        movie_info[release_date_key] = [modified_release_date]

        # Check if the key is 'Production company' or 'Production companies'
        production_key = 'Production company' if 'Production company' in movie_info else 'Production companies'

        # Remove the space between the items in 'Production companies' list
        production_value = movie_info.get(production_key, [])
        if isinstance(production_value, list):
            production_companies = [company.replace(' ', '') for company in production_value]
            movie_info[production_key] = production_companies
    pprint.pprint(movie_info)
    return movie_info


# In[ ]:


page = requests.get("https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films")
soup = bs(page.content)
all_td_elements = soup.find_all('td')

base_path = "https://www.wikipedia.org/"

movie_info_list = []

for td in all_td_elements:
    link_element = td.find('a')

    if link_element:
        title = link_element.get('title')
        href = link_element.get('href')

        if title and title != 'None' and title != '20th Digital Studio' and not title.startswith('List') and not title.startswith('Walt'):
            print("Title:", title) 
            print("Link:", href)
            try:
                relative_path = href
                full_path = base_path + relative_path

                movie_info_list.append(get_info_box(full_path))

            except Exception as e:
                print(href)
                print(e)


# In[ ]:


len(movie_info_list)


# In[ ]:


save_path = r"G:\my_projects\disney\disney_data_cleaned.json"
load_path = r"G:\my_projects\disney\disney_data_cleaned.json"


# In[ ]:


#save and reload data
import json

def save_data(title, data):
    with open(title, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
# Saving data to the specified location
save_path = r"G:\my_projects\disney\disney_data_cleaned.json"
save_data(save_path, movie_info_list)
    


# In[1]:


import json

def load_data(title):
    with open(title, 'r', encoding='utf-8') as f:
        return json.load(f)

# Loading data from the specified location
load_path = r"G:\my_projects\disney\disney_data_cleaned.json"
movie_info_list = load_data(load_path)


# In[2]:


movie_info_list[-5]


# In[3]:


for movie_info in movie_info_list:
    if 'Running time' in movie_info:
        running_time_data = movie_info['Running time']
        running_time = None  # Initialize running_time as None

        # Check the type of 'Running time' value
        if isinstance(running_time_data, list):
            for item in running_time_data:
                if isinstance(item, int):
                    running_time = item
                    break  # Stop searching once an integer item is found
                elif isinstance(item, str):
                    # Try to extract numeric value from the string
                    try:
                        running_time = int(item.split()[0])
                        break  # Stop searching once a valid string item is found
                    except ValueError:
                        pass  # Handle cases where the string cannot be converted to an integer
        elif isinstance(running_time_data, (int, str)):
            # If 'Running time' is already an integer or string, try to convert it to an integer
            try:
                running_time = int(str(running_time_data).split()[0])
            except ValueError:
                pass  # Handle cases where the string cannot be converted to an integer

        # Update 'Running time' with the extracted value or None if not found
        movie_info['Running time'] = running_time

# Now, the 'Running time' values in movie_info_list have been updated to integers or None if not found
for movie_info in movie_info_list:
    print(movie_info.get('Running time'))


# In[4]:


movie_info_list[-9]


# In[5]:


movie_info_list[-5]


# In[6]:


for movie_info in movie_info_list:
    print(movie_info.get('Budget'))


# In[7]:


movie_info_list[-9]


# In[8]:


import re

def take_lower(budget_data):
    budget_data = str(budget_data).replace('$', '').replace('Budget', '')
    if '-' in budget_data:
        all_values = budget_data.split('-', 2) #return value from data in range form
        return_lower = all_values[1]
    else:
        return budget_data

def clean_budget(budget_data):
    try:
        budget_data = take_lower(budget_data)

        if 'million' in budget_data:
            # Extract the numeric part of the budget string
            numeric_part = re.search(r'\d+\.?\d*', budget_data)
            if numeric_part:
                budget_in_million = float(numeric_part.group())  # Extracted numeric value
                return int(budget_in_million * 1000000)  # Convert to integer in millions
    except TypeError:
        return None


# In[9]:


for movie_info in movie_info_list:
    budget_data = movie_info.get('Budget')  # Don't provide a default value of '' here
    if budget_data is not None:  # Check if 'Budget' key exists
        cleaned_budget = clean_budget(budget_data)
        movie_info['Budget'] = cleaned_budget
        print(cleaned_budget)
    else:
        print("No budget Info")


# In[10]:


movie_info_list[-9]


# In[11]:


for movie_info in movie_info_list:
    print(movie_info.get('Box office'))


# In[12]:


import re

def remove_values_in_parentheses(bo_data):
    # Ensure bo_data is a string
    bo_data = str(bo_data)
    
    # Define a regex pattern to match values within parentheses
    pattern = r'\s*\([^)]*\)'

    # Use re.sub() to replace the matched patterns with an empty string
    cleaned_bo_data = re.sub(pattern, '', bo_data)

    return cleaned_bo_data






def clean_boxoffice(bo_data):
    # Remove values within parentheses
    bo_data = remove_values_in_parentheses(bo_data)

    # Convert to string and remove "$", "Box office", ">", and "₹"
    bo_data = str(bo_data).replace('$', '').replace('Box office', '').replace('>', '').replace('₹', '')

    # Check if the bo_data contains a hyphen or an em dash
    if '-' in bo_data or '–' in bo_data:
        # Use regular expressions to extract the upper limit of the box office range
        bo_match = re.search(r'(\d+(\.\d+)?)[–-](\d+(\.\d+)?)\s*million', bo_data)

        if bo_match:
            lower_limit_str = bo_match.group(1)
            upper_limit_str = bo_match.group(3)
            # Remove any non-digit characters (except for decimal point) and convert to float
            lower_limit_str = ''.join(filter(lambda x: x.isdigit() or x == '.', lower_limit_str))
            upper_limit_str = ''.join(filter(lambda x: x.isdigit() or x == '.', upper_limit_str))
            lower_limit = float(lower_limit_str) * 1_000_000
            upper_limit = float(upper_limit_str) * 1_000_000
            return int((lower_limit + upper_limit) / 2)
    elif 'million' in bo_data.lower():
        # Replace 'million' with '' and handle decimal points
        value = re.search(r'(\d+(\.\d+)?)\s*million', bo_data.lower()).group(1)
        try:
            value = float(value) * 1_000_000
            return int(value)
        except ValueError:
            # If the value still cannot be converted, return it as is
            return bo_data
    elif 'crore' in bo_data.lower():
        # Change it to USD for uniformity, 1 crore = 10 million
        value = re.search(r'(\d+(\.\d+)?)\s*crore', bo_data.lower()).group(1)
        try:
            value = float(value) * 10_000_000 * 0.012
            return int(value)
        except ValueError:
            # If the value still cannot be converted, return it as is
            return bo_data
    elif 'billion' in bo_data.lower():
        # Replace 'million' with '' and handle decimal points
        value = re.search(r'(\d+(\.\d+)?)\s*billion', bo_data.lower()).group(1)
        try:
            value = float(value) * 1_000_000_000
            return int(value)
        except ValueError:
            # If the value still cannot be converted, return it as is
            return bo_data 
    else:
        # Return the original bo_data if it doesn't match any of the patterns
        return bo_data


# In[13]:


for movie_info in movie_info_list:
    bo_data = movie_info.get('Box office', '')
    cleaned_boxoffice = clean_boxoffice(bo_data)
    movie_info['Box office'] = cleaned_boxoffice
    print(cleaned_boxoffice)


# In[14]:


movie_info_list[-11]


# In[15]:


for movie_info in movie_info_list:
    print(movie_info.get('Release date'))


# In[16]:


# Update each dictionary in movie_info_list with the combined release date
for movie_info in movie_info_list:
    movie_info['The release date'] = movie_info.get('Release date') if movie_info.get('Release date') is not None else movie_info.get('Release dates')

# Print the updated movie_info_list
for movie_info in movie_info_list:
    print(movie_info.get('The release date'))


# In[17]:


import pendulum
import re

def clean_date(date_data):
    # Ensure date_data is a string
    date_data = str(date_data)
    
    # Define a regular expression pattern to extract the numerical date
    pattern = r'\(\d{4}-\d{2}-\d{2}\)'  # Matches (YYYY-MM-DD)
    
    # Extract all numerical dates from the string
    numerical_dates = re.findall(pattern, date_data)

    if numerical_dates:
        # Take the first numerical date (if there are multiple) and remove parentheses
        numerical_date = numerical_dates[0].strip('()')

        # Convert the extracted date string to a pendulum datetime object
        try:
            pendulum_date = pendulum.parse(numerical_date)
            
            # Format the date as a string in 'YYYY-MM-DD' format
            formatted_date = pendulum_date.strftime('%d-%m-%Y')
            
            return formatted_date
        except pendulum.parsing.exceptions.ParserError:
            return None  # Return None if the date couldn't be parsed
    else:
        return None  # Return None if no valid date pattern is found


# In[18]:


for movie_info in movie_info_list:
    date_data = movie_info.get('The release date', '')
    cleaned_date = clean_date(date_data)
    movie_info['The release date'] = cleaned_date
    print(cleaned_date)


# In[19]:


movie_info_list[-11]


# In[ ]:





# In[ ]:




