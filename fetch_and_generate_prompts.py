import os
import json
import requests

# Directory to store cached OEIS sequences
CACHE_DIR = "oeis_cache"

def fetch_oeis_sequence(number):
    # Ensure the cache directory exists
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    # Format the sequence number with leading zeros
    sequence_number = str(number).zfill(6)
    cache_file_path = os.path.join(CACHE_DIR, f"A{sequence_number}.json")

    # Check if the sequence is already cached
    if os.path.exists(cache_file_path):
        with open(cache_file_path, 'r') as cache_file:
            cached_data = json.load(cache_file)
    else:
        # If not cached, fetch from OEIS
        url = f"https://oeis.org/search?fmt=json&q=id:A{sequence_number}"
        response = requests.get(url)
        
        # Ensure the request was successful
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.status_code}")
        
        # Cache the entire response JSON to disk
        cached_data = response.json()
        with open(cache_file_path, 'w') as cache_file:
            json.dump(cached_data, cache_file)

    # Now we extract the relevant parts from the cached JSON
    sequence_data = cached_data[0]  # The data is in the first element of the JSON list
    
    # Extract and process the "data" field
    data_str = sequence_data.get("data", "")
    data_array = [int(x) for x in data_str.split(",") if x.strip().isdigit()]
    
    # Extract and process the "comment" field
    comments = sequence_data.get("comment", [])
    comments_str = "\n\n".join(comments)
    
    # Extract and process the "offset" field
    offset_str = sequence_data.get("offset", "")
    offset_array = [int(x) for x in offset_str.split(",") if x.strip().isdigit()]
    
    # Extract the "name" field
    name = sequence_data.get("name", "")
    
    # Extract the "keyword" field and process it as a list of strings
    keywords_str = sequence_data.get("keyword", "")
    keywords_list = keywords_str.split(",") if keywords_str else []
    
    return {
        "name": name,
        "data": data_array,
        "comments": comments_str,
        "offset": offset_array,
        "keywords": keywords_list
    }
###########################################################
def get_prompt(info):
    return f"""Write a python code that takes a number n as input from stdin, outputs a single element of a sequence as a string to stdout. Just output the n-th element in the sequence, not the whole sequence or anything other than the single sequence element. You will be graded by my running your code and comparing the results with a look-up table. If you use a look-up table for your code, you will not only fail the test. Hardcoding values that can be computed without hardcoding is considered to be using a look-up table. Use only the standard python library. No packages will be installed with pip or conda. Output your final code at the end of your response inside triple backticks like:
```
#your code goes here
```
The last part of your response that is inside triple backticks will be used as your response for the purposes of the test. The code will be stopped after a short period of time, so make it efficient if needed.

Here is some information on the sequence:
```
Name: {info["name"]}
Comments: {info["comments"]}
```"""



##########################################################    
# Initialize counts for the benchmarks
hards = 0
easies = 0

# Create directories for prompts
easy_prompt_dir = "SequenceEasyPrompts"
hard_prompt_dir = "SequenceHardPrompts"

if not os.path.exists(easy_prompt_dir):
    os.makedirs(easy_prompt_dir)

if not os.path.exists(hard_prompt_dir):
    os.makedirs(hard_prompt_dir)

for i in range(1, 10 ** 4):
    print(i)
    info = fetch_oeis_sequence(i)
    sequence_id = f"A{str(i).zfill(6)}"
    if "hard" in info["keywords"] and hards < 250:
        print("hard", sequence_id)
        hards += 1
        prompt = get_prompt(info)
        filename = os.path.join(hard_prompt_dir, f"{sequence_id}.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(prompt)
    elif "easy" in info["keywords"] and easies < 250:
        print("easy", sequence_id)
        easies += 1
        prompt = get_prompt(info)
        filename = os.path.join(easy_prompt_dir, f"{sequence_id}.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(prompt)
    # Break the loop if both benchmarks have 250 sequences
    if hards >= 250 and easies >= 250:
        break

print("Total hard sequences collected:", hards)
print("Total easy sequences collected:", easies)
