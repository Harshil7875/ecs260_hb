from pathlib import Path
import json
import re

target_path_prefix = "../../../3rdparty/bugscpp_hufork/bugscpp/taxonomy/"
file_name = 'bug_files.json'

data = {}

for repo in Path(target_path_prefix).iterdir():
    if repo.is_dir() and '__pycache__' not in repo.name:
        patch_path = str(repo) + '/patch'
        for bug_patch in Path(patch_path).iterdir():
            if '-buggy.patch' in bug_patch.name:
                files_list = []
                with open(bug_patch, 'r') as file:
                    for line in file:
                        if '---' in line:
                            next_line = next(file, None)
                            while next_line and 'changed' not in next_line:
                                buggy_file = next_line.strip().split('|')[0].strip()
                                files_list.append(buggy_file)
                                next_line = next(file, None)
                                # print(repo.name + '/' + buggy_file)
                            break  # Exit the loop after finding the first "---"
                match = re.search(r'[1-9]\d*', bug_patch.name)
                number = match.group(0) if match else None
                data[repo.name + '-' + number] = files_list

with open(file_name, 'w') as file:
    json.dump(data, file, indent=4)
