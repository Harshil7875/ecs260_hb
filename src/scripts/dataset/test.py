import subprocess
import os
from pathlib import Path
from fetch import target_path, python_prefix, bugscpp_script_path, get_buggy_files

test_res_path = "./test_result"

build_command_pattern = "{} {} build {}"
test_command_pattern = "{} {} test {} --output-dir {}"


class TestCasesResult:
    def __init__(self, pass_rate: float, pass_test_cases: [], fail_test_cases: []):
        self.pass_rate = pass_rate
        self.pass_test_cases = pass_test_cases
        self.fail_test_cases = fail_test_cases


class TestResult:
    def __init__(self, repo_name: str, build_result: bool, test_cases_result: TestCasesResult):
        self.repo_name = repo_name
        self.build_result = build_result
        self.test_cases_result = test_cases_result


def build_repo(full_repo_name, is_buggy_repo: bool = True) -> bool:
    repo, index = full_repo_name.split("-")
    if is_buggy_repo:
        buggy_repo_path = target_path + "/" + repo + "/buggy-" + index
    else:
        buggy_repo_path = target_path + "/" + repo + "/fixed-" + index
    return build(full_repo_name, buggy_repo_path)


def build_in_batch(buggy_repo_list):
    build_res = {}
    for buggy_repo in buggy_repo_list:
        build_res[build_repo] = build_repo(buggy_repo)

    return build_res


def build(buggy_repo, build_path):
    build_command = build_command_pattern.format(python_prefix, bugscpp_script_path, build_path)
    subprocess.run(build_command.split(), check=True, text=True, capture_output=True)
    return check_if_build_success(buggy_repo, build_path)


def check_if_build_success(buggy_repo, build_path):
    res = True
    buggy_files = get_buggy_files(buggy_repo)
    for buggy_file_path in buggy_files:
        file_name_with_extension = os.path.basename(buggy_file_path)
        file_name_without_extension, _ = os.path.splitext(file_name_with_extension)
        if not Path(build_path + '/' + os.path.dirname(
                buggy_file_path) + '/' + file_name_without_extension + '.o').exists():
            res = False
            break

    parent_directory = Path(build_path)
    build_directory = parent_directory / 'build'
    res = res | build_directory.is_dir()
    return res


def test_repo(buggy_repo: str, is_buggy_repo: bool = True) -> TestCasesResult:
    repo, index = buggy_repo.split("-")
    if is_buggy_repo:
        buggy_repo_path = target_path + "/" + repo + "/buggy-" + index
        buggy_res_path = test_res_path + "/" + repo + "-buggy-" + index
        test(buggy_repo_path, buggy_res_path)
        return compute_test_result(buggy_res_path)
    else:
        fixed_repo_path = target_path + "/" + repo + "/fixed-" + index
        fixed_res_path = test_res_path + "/" + repo + "-fixed-" + index
        test(fixed_repo_path, fixed_res_path)
        return compute_test_result(fixed_res_path)


def test_in_batch(buggy_repo_list):
    test_res = {}
    for buggy_repo in buggy_repo_list:
        test_res[buggy_repo] = test_repo(buggy_repo)
    return test_res


def test(test_path, res_path):
    test_command = test_command_pattern.format(python_prefix, bugscpp_script_path, test_path, res_path)
    subprocess.run(test_command.split(), check=True, text=True, capture_output=True)


def compute_test_result(res_path) -> TestCasesResult:
    idx = 0
    count = 0
    pass_test_cases = []
    fail_test_cases = []
    for test_res in Path(res_path).iterdir():
        if test_res.is_dir():
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
                                break
                    idx += 1
    return TestCasesResult(count / idx, pass_test_cases, fail_test_cases)