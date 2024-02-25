import os
from fetch import patch_path_prefix, target_path, get_buggy_files, parse_patch, find_function_start, find_function_end


def update_buggy_code(buggy_repo, corrected_code):
    repo, index = buggy_repo.split("-")
    patch_file_path = patch_path_prefix + repo + '/patch/' + "{:04d}".format(int(index)) + '-buggy.patch'
    changes = parse_patch(patch_file_path)
    for change in changes:
        file_path = change.current_file
        start_line = change.start_line
        source_file = target_path + '/' + repo + '/buggy-' + index + '/' + file_path
        with open(source_file, 'r') as file:
            # write original code into temp file first
            content = file.read()
            write_code_to_temp_file(content, buggy_repo + '-' + os.path.basename(file_path))

            # update buggy file with corrected code provided by llm
            file.seek(0)
            lines = file.readlines()
            start_index = find_function_start(lines, start_line - 1)
            end_index = find_function_end(lines, start_index)

            # replace function code within the specified range
            lines[start_index:end_index + 1] = corrected_code.splitlines(keepends=True)
            with open(source_file, 'w', encoding='utf-8') as file:
                file.writelines(lines)


def restore_buggy_code(buggy_repo):
    repo, index = buggy_repo.split("-")
    buggy_files = get_buggy_files(buggy_repo)
    for buggy_file_path in buggy_files:
        path = target_path + '/' + repo + '/' + 'buggy-' + index + '/' + buggy_file_path
        with open(path, 'w', encoding='utf-8') as file:
            temp_file_name = buggy_repo + '-' + os.path.basename(buggy_file_path)
            origin_code = read_code_from_temp_file(temp_file_name)
            file.write(origin_code)
            os.remove(os.path.join('./tmp', temp_file_name))


def write_code_to_temp_file(code_text, file_name):
    temp_file_path = os.path.join('./tmp', file_name)
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write(code_text)


def read_code_from_temp_file(file_name):
    temp_file_path = os.path.join('./tmp', file_name)
    with open(temp_file_path, 'r') as temp_file:
        return temp_file.read()