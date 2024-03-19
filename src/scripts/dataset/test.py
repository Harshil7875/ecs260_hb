import subprocess
import os
import re
import json
from pathlib import Path
from typing import List, Dict
from fetch import target_path, python_prefix, bugscpp_script_path, get_buggy_files

test_res_path = "./test_result"
build_out_path = "./build_output"

build_command_pattern = "{} {} build {}"
test_command_pattern = "{} {} test {} --output-dir {}"
test_command_with_tc_pattern = "{} {} test {} --output-dir {} --case {}"


class BuildResult:
    def __init__(self, build_res: bool, build_output: str):
        self.build_res = build_res
        self.build_output = build_output


class TestCasesResult:
    def __init__(self, pass_rate: float, pass_test_cases: List[str], fail_test_cases: List[str], fail_test_cases_info: List[str]):
        self.pass_rate = pass_rate
        self.pass_test_cases = pass_test_cases
        self.fail_test_cases = fail_test_cases
        self.fail_test_cases_info = fail_test_cases_info


class TestResult:
    def __init__(self, repo_name: str, build_result: bool, build_output: str, test_cases_result: TestCasesResult):
        self.repo_name = repo_name
        self.build_result = build_result
        self.build_output = build_output
        self.test_cases_result = test_cases_result


def build_repo(full_repo_name, is_buggy_repo: bool = True) -> BuildResult:
    repo, index = full_repo_name.split("-")
    if is_buggy_repo:
        buggy_repo_path = target_path + "/" + repo + "/buggy-" + index
    else:
        buggy_repo_path = target_path + "/" + repo + "/fixed-" + index
    return build(full_repo_name, buggy_repo_path)


def build(buggy_repo, build_path) -> BuildResult:
    build_command = build_command_pattern.format(python_prefix, bugscpp_script_path, build_path)
    with open('./build_output/' + buggy_repo + '_build_output.txt', 'w') as file:
        # Use Popen to execute the command, setting stdout to the file object to capture the output
        process = subprocess.Popen(build_command.split(), stdout=file, stderr=subprocess.STDOUT, text=True)
        process.wait()

    return generate_build_result(buggy_repo, build_path)


def generate_build_result(buggy_repo, build_path) -> BuildResult:
    # check build output to see if build successfully
    res = check_build_output(buggy_repo)

    # check if .o file exists
    buggy_files = get_buggy_files(buggy_repo)
    for buggy_file_path in buggy_files:
        file_name_with_extension = os.path.basename(buggy_file_path)
        file_name_without_extension, _ = os.path.splitext(file_name_with_extension)
        if Path(build_path + '/' + os.path.dirname(buggy_file_path) + '/' + file_name_without_extension
                + '.o').exists() or check_exe_file_exists(build_path + '/' + os.path.dirname(buggy_file_path),
                                                          file_name_without_extension):
            res = res | True
        else:
            res = res | False
            break

    # get build info
    build_output = get_build_output(buggy_repo, res)

    return BuildResult(res, build_output)


def check_build_output(buggy_repo):
    build_res = True
    with open('./build_output/' + buggy_repo + '_build_output.txt', 'r') as file:
        file_content = file.read()
        complete_build_info = remove_ansi_escape_sequences(file_content)

        if '100%' not in complete_build_info:
            build_res = False

        return build_res


def check_exe_file_exists(directory, target):
    for filename in os.listdir(directory):
        if filename.endswith(target + '.o'):
            return True
    return False


def get_build_output(buggy_repo, build_res):
    with open('./build_output/' + buggy_repo + '_build_output.txt', 'r') as file:
        if build_res:
            file_content = file.read()
            complete_build_info = remove_ansi_escape_sequences(file_content)
            return complete_build_info
        else:
            lines = file.readlines()
            build_error_infos = []
            buggy_files = get_buggy_files(buggy_repo)
            for buggy_file_path in buggy_files:
                file_name_with_extension = os.path.basename(buggy_file_path)

                # find the index of all rows containing keywords and their windows
                windows = [(max(0, i - 1), min(len(lines), i + 6)) for i, line in enumerate(lines) if
                           file_name_with_extension in line]
                # merge overlap window
                merged_windows = merge_overlapping_windows(windows)
                for start, end in merged_windows:
                    context = ''.join(lines[start:end])
                    build_error_infos.append(context)

            build_error_info = ''.join(build_error_infos)
            return build_error_info


def merge_overlapping_windows(windows):
    if not windows:
        return []

    # sort window by start index
    windows.sort(key=lambda x: x[0])

    merged_windows = [windows[0]]
    for current_start, current_end in windows[1:]:
        last_merged_start, last_merged_end = merged_windows[-1]

        if current_start <= last_merged_end:
            merged_windows[-1] = (last_merged_start, max(last_merged_end, current_end))
        else:
            merged_windows.append((current_start, current_end))
    return merged_windows


def test_repo(buggy_repo: str, is_buggy_repo: bool = True) -> TestCasesResult:
    repo_path, res_path = generate_repo_res_path(buggy_repo, is_buggy_repo)
    test(repo_path, res_path)
    return compute_test_result(res_path, [])


def test_repo_with_tcs(buggy_repo: str, test_cases: List[str], is_buggy_repo: bool = True) -> TestCasesResult:
    repo_path, res_path = generate_repo_res_path(buggy_repo, is_buggy_repo)
    test_with_tc(repo_path, res_path, test_cases)
    return compute_test_result(res_path, test_cases)


def test_repo_with_failed_tcs(buggy_repo: str, is_buggy_repo: bool = True) -> TestCasesResult:
    test_cases = get_repo_failed_test_cases(buggy_repo)
    return test_repo_with_tcs(buggy_repo, is_buggy_repo, test_cases)


def generate_repo_res_path(buggy_repo: str, is_buggy_repo: bool = True):
    repo, index = buggy_repo.split("-")
    if is_buggy_repo:
        buggy_repo_path = target_path + "/" + repo + "/buggy-" + index
        buggy_res_path = test_res_path + "/" + repo + "-buggy-" + index
        return buggy_repo_path, buggy_res_path
    else:
        fixed_repo_path = target_path + "/" + repo + "/fixed-" + index
        fixed_res_path = test_res_path + "/" + repo + "-fixed-" + index
        return fixed_repo_path, fixed_res_path


def test(test_path, res_path):
    test_command = test_command_pattern.format(python_prefix, bugscpp_script_path, test_path, res_path)
    subprocess.run(test_command.split(), check=True, text=True, capture_output=True)


def test_with_tc(test_path, res_path, test_cases: List[str]):
    tcs = ",".join([str(i) for i in test_cases])
    test_command = test_command_with_tc_pattern.format(python_prefix, bugscpp_script_path, test_path, res_path, tcs)
    subprocess.run(test_command.split(), check=True, text=True, capture_output=True)


def compute_test_result(res_path: str, test_cases: List[str]) -> TestCasesResult:
    idx = 0
    count = 0
    pass_test_cases = []
    fail_test_cases = []
    fail_tcs_info = {}
    is_test_all = True if len(test_cases) == 0 else False
    for test_res in Path(res_path).iterdir():
        if test_res.is_dir():
            repo, is_buggy, index, tc_no = test_res.name.split('-')
            try:
                test_case_no = int(tc_no)
                if not is_test_all and test_case_no not in test_cases:
                    continue
            except ValueError:
                pass

            for res in test_res.iterdir():
                if '.test' in res.name:
                    with open(res, 'r') as file:
                        for line in file:
                            if line == 'passed':
                                count += 1
                                pass_test_cases.append(test_res.name)
                                break
                            if line == 'failed':
                                fail_test_cases.append(test_res.name)
                                fail_tcs_info[test_res.name] = get_repo_failed_test_cases_info(repo + '-' + index, tc_no)
                                break
                    idx += 1
    return TestCasesResult(count / idx, pass_test_cases, fail_test_cases, fail_tcs_info)


def remove_ansi_escape_sequences(text):
    ansi_escape_re = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape_re.sub('', text)


def get_repo_failed_test_cases(repository_name: str) -> List[str]:
    with open('./repo_test_cases.json', 'r') as file:
        return json.load(file)[repository_name]


def get_repo_failed_test_cases_info(repository_name, test_case_no):
    with open('./repo_tc_failing_info.json', 'r') as file:
        data = json.load(file)
        repo_data = data.get(repository_name, {})  # Get the repository's data or an empty dict if not found
        return repo_data.get(str(test_case_no), {})  # Return the test case info or an empty dict if not found
