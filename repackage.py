#!/usr/bin/env python3

from datetime import datetime
import json
import glob
import os
import shutil
import zipfile
import argparse

parser = argparse.ArgumentParser(description='Process vsix folder')
parser.add_argument('vsix_folder', help='Folder containing a single vsix file which will be repacked.')
parser.add_argument('repository', help='The URL of the NPM repository in which the repackaged extension will be stored.')
args = parser.parse_args()

cwd = os.getcwd()

try:
    os.chdir(args.vsix_folder)
    
    # Check if only 1 vsix file is in the folder and extract the package.json from it
    files = glob.glob("./*.vsix")
    if (len(files) != 1):
        print("Exactly one vsix file must exist in this folder.")
        exit
    with zipfile.ZipFile(files[0], 'r') as zipObj:
        zipObj.extract("extension/package.json")
        shutil.move("extension/package.json", "./package.json")
        shutil.rmtree("extension")
    
    # Open JSON file and return JSON object as  a dictionary
    f = open('package.json')
    data = json.load(f)
    
    # Prepare repackaging;  
    # data_new contains key-value pairs that are needed by the
    # private extension gallery keys_to_copy contains the keys from the original
    # package.json that will be copied to the one for the private extension gallery.
    print("Repackaging...")
    data_new = {}
    keys_to_copy = []
    
    # Add the vsix file
    data_new['files'] = [ 
         data['publisher'] + "." + data['name'] + "-" + data['version'] + ".vsix",
    ]
    
    # Handle extension icon (if existing)
    if "icon" in data:
        if not os.path.exists(os.path.dirname(data['icon'])):
            os.mkdir(os.path.dirname(data['icon']))
        with zipfile.ZipFile(files[0], 'r') as zipObj:
            zipObj.extract("extension/" + data['icon'], ".")
            shutil.move(os.path.abspath("extension/" + data['icon']), data['icon'])
        shutil.rmtree("extension")
        data_new['files'].append(data['icon'])
        keys_to_copy.append("icon")
    
    # Adjust the extension name to reflect that this a repackaged one
    data_new['displayName'] = data['displayName'] + " - VSC repacked extension"
    
    # Add the repository so that npm knows where the repackaged extension will be stored
    data_new['publishConfig'] = {"registry": args.repository}
    
    # Define remaining keys that are taken from original package.json
    keys_to_copy += [
        'name',
        'version',
        'publisher',
        'description',
        'repository',
        'engines',
    ]
    if 'author' in data:
        keys_to_copy.append('author')
    if 'keywords' in data:
        keys_to_copy.append('keywords')
    
    # Merge original data into new data
    data_dict_to_copy = { your_key: data[your_key] for your_key in keys_to_copy }
    data_new.update(data_dict_to_copy)
    
    # Write package.json; 'w' mode will overwrite original package.json
    with open('package.json', 'w', encoding='utf-8') as f:
        json.dump(data_new, f, ensure_ascii=False, indent=4)
    
    # Write README.md
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write("# Repackaging Information" + "\n\n")
        f.write("This is a repackaged extension from an internet source.  \n")
        f.write("packaged by: " + os.getlogin() + "  \n")
        f.write("packaged on: " + datetime.now().isoformat() + "\n\n")
        
        f.write("For extension documentation and README, check with the original extension")
        if "homepage" in data:
            f.write("  \nhomepage: " + data['homepage'])
        if "url" in data['repository']:
            f.write("  \nrepository: " + data['repository']['url'])
        f.write("\n")
    
    # Write desktop output
    print("Prepared package.json for publishing.")
    print("Execute following command for publishing to Nexus:")
    print("cd " + cwd + "; npm publish .")
            
finally:
    os.chdir(cwd)
