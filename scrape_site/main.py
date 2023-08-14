import json, subprocess, os, sys
import logging


data = {"urls": []}

def url_check(url):
    if "https://" in url and ".com" in url:
        return url
    elif "https://" not in url and ".com" in url:
        return "https://" + str(url)
    elif "https://" in url and ".com" not in url:
        return str(url) + ".com"
    else:
        return "https://" + str(url) + ".com"

# This Function Screated Json file
# This Function Screated Json file
def write_json(file_name, data):
    with open(file_name, 'w') as json_file:
        json.dump(data, json_file)

def read_json(file_name):
    # Read JSON data from a file
    with open(file_name) as file:
        json_data = file.read()
    # Load JSON data into a dictionary
    web_links = json.loads(json_data)
    return web_links

def remove_duplicate_links(file_name):
    urls_dict = read_json(file_name)
    urls_list = urls_dict["urls"]
    urls_list = list(set(urls_list))
    urls_dict["urls"] = urls_list
    write_json(file_name, urls_dict)
    return str(len(urls_list))


def main():
    # User arguments 
    starting_url = sys.argv[1]
    allowed_dom = sys.argv[2:]

    # Last user argument (Output Directory Path)
    output_file_path = allowed_dom[-1]

    # Allowed Domains list
    allowed_dom = allowed_dom[:-1]

    # Creating Output folder on that Directory
    directory_path = os.path.expanduser(output_file_path)
    try:
        print(directory_path)
        os.makedirs(directory_path, exist_ok=True)
        print("Directory created successfully!")

        # Create the full path for the new folders
        json_folder_path = os.path.join(os.path.expanduser(directory_path), 'json_files')
        images_folder_path = os.path.join(os.path.expanduser(directory_path), 'images')
        pdf_folder_path = os.path.join(os.path.expanduser(directory_path), 'pdfs')

        try:
            # Creating json_files folder on that Directory
            os.makedirs(json_folder_path, exist_ok=True)
            print("json_files created successfully!")
        except OSError as error:
            print(f"Error creating folder: {error}")
        
        try:
            # Creating images folder on that Directory
            os.makedirs(images_folder_path, exist_ok=True)
            print("images created successfully!")
        except OSError as error:
            print(f"Error creating folder: {error}")

        try:
            # Creating pdfs folder on that Directory
            os.makedirs(pdf_folder_path, exist_ok=True)
            print("pdfs created successfully!")
        except OSError as error:
            print(f"Error creating folder: {error}")

        print("\t3 Folders (images, json_files & pdfs created inside " + directory_path + ")")

        starting_url = url_check(starting_url)
        os.environ["STARTING_URL"] = starting_url
        os.environ["OUTPUT_FILE_PATH"] = directory_path
        write_json(directory_path + '/allowed_domains.json', allowed_dom)
        write_json(directory_path + '/json_files/pdf_urls.json', [])
        write_json(directory_path + '/json_files/image_urls.json', [])

        command = ['scrapy', 'crawl', 'website_spider', '-o', directory_path + '/json_files/html.json', '-a', f'directory_path={directory_path}']
        subprocess.run(command)


    except OSError as error:
        print(f"Error creating directory: {error}")
        
 
    

if __name__ == "__main__":
    main()

