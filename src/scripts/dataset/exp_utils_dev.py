# # A Python API Interface to provide basic functions for querying LLMs
# # Author: Xinzhuo (Johnson) Hu
# # Create Date: 2024-02-21 6:48 pm
# # Last Update: 2024-03-14 12:55 pm (merging changes of Rishika)

# import os
# import re
# import json
# import csv
# from datetime import datetime
# import dataset_api

# # RS_1: single-line - invalid-condition: , num: 13
# repair_scenarios_1_safe  = ['berry-5', 'cpp_peglib-4', 'cppcheck-8', 
#                         'cppcheck-9', 'cppcheck-11', 'cppcheck-25', 'exiv2-13', 'exiv2-15', 
#                         'libtiff-1', 'openssl-14', 'openssl-24', 'yara-1', 'yara-2', 'berry-3']

# # RS_2: single-line - invalid-format-string: , num: 4
# repair_scenarios_2_full = ['cpp_peglib-8', 'dlt_daemon-1', 'exiv2-20', 'yaml_cpp-6']
# repair_scenarios_2_safe = ['dlt_daemon-1', 'exiv2-20', 'yaml_cpp-6']

# # RS_3: single-line - memory-error: , num: 14
# repair_scenarios_3_safe_full = ['dlt_daemon-1', 'libtiff-1', 'ndpi-1']
# repair_scenarios_3_safe = ['dlt_daemon-1', 'libtiff-1']

# repos_with_modification = ['berry-1', 'berry-3', 'berry-4', 'libtiff-1', 'libtiff-2', 'libucl-1']
# repos_with_omission = ['berry-2', 'libtiff-3', 'libtiff-4', 'libtiff-5', 'libucl-4']
# repos_with_logical_error = ['berry-4', 'libucl-3', 'libucl-2']
# repos_with_CVE = ['libtiff-1', 'libtiff-3', 'libtiff-5']
# repos_with_zero_division = ['libtiff-3', 'libtiff-4']

# class parsedLLMRespond:
#     def __init__(self, repaired_func_str: str, confidence: float, errlin_num_list: list, 
#                  error_type_list: list, explan_list: list, line_offset: int) -> None:
        
#         self.repaired_func_str = repaired_func_str
#         self.confidence = confidence
#         self.errlin_num_list = errlin_num_list
#         self.error_type_list = error_type_list
#         self.explan_list = explan_list
#         self.line_offset = line_offset


# class evalLLMRespond:
#     def __init__(self, prompt_ind: int, confidence: float, build_result: bool, 
#                  identify_errline_accuracy: float, pass_rate: float, response_time: float, 
#                  pass_testcases_num: int, fail_testcases_num: int, llm_error_line_list: list, true_error_line_list: list) -> None:
        
#         self.prompt_ind = prompt_ind
#         self.confidence = confidence
#         self.build_result = build_result
#         self.identify_accuracy = identify_errline_accuracy
#         self.pass_rate = pass_rate
#         self.response_time = response_time
#         self.pass_testcases_num = pass_testcases_num
#         self.fail_testcases_num = fail_testcases_num
#         self.llm_error_line_list = llm_error_line_list
#         self.true_error_line_list = true_error_line_list

# def get_safe_repair_scenario_list(index: int) -> list:
#     if index == 1: return repair_scenarios_1_safe
#     elif index == 2: return repair_scenarios_2_safe
#     elif index == 3: return repair_scenarios_3_safe
#     else: raise RuntimeError("Hi Kid! You want to get something dangerous...") 

# def constructPrompt(function: str, prompt_id: int, repo_name: str , single_multi_str = 'single-line'):
#     if prompt_id == 1: return constructPrompt_1(function)

#     elif prompt_id == 2:
#         single_multi_ind = 1
#         if single_multi_str == 'multi-line': single_multi_ind = 2
#         error_type_list = []

#         # if single_multi_ind == 1:
#         if repo_name in repair_scenarios_1_safe: error_type_list.append('invalid condition')
#         if repo_name in repair_scenarios_2_safe: error_type_list.append('invalid format string')
#         if repo_name in repair_scenarios_3_safe: error_type_list.append('memory error')
#         if repo_name in repos_with_modification: error_type_list.append('error due to modification')
#         if repo_name in repos_with_omission: error_type_list.append('error due to omission')
#         if repo_name in repos_with_logical_error: error_type_list.append('logical error')
#         if repo_name in repos_with_CVE: error_type_list.append('vulnerability error')
#         if repo_name in repos_with_zero_division: error_type_list.append('error due to division by zero')

#         return constructPrompt_2(function, single_multi_ind, error_type_list)

#     elif prompt_id == 3: 
#         return constructPrompt_3(function)

#     elif prompt_id == 4:
#         single_multi_ind = 1
#         if single_multi_str == 'multi-line': 
#             single_multi_ind = 2

#         error_type_list = []
#         # if single_multi_ind == 1:
#         if repo_name in repair_scenarios_1_safe: error_type_list.append('invalid condition')
#         if repo_name in repair_scenarios_2_safe: error_type_list.append('invalid format string')
#         if repo_name in repair_scenarios_3_safe: error_type_list.append('memory error')
#         if repo_name in repos_with_modification: error_type_list.append('error due to modification')
#         if repo_name in repos_with_omission: error_type_list.append('error due to omission')
#         if repo_name in repos_with_logical_error: error_type_list.append('logical error')
#         if repo_name in repos_with_CVE: error_type_list.append('vulnerability error')
#         if repo_name in repos_with_zero_division: error_type_list.append('error due to division by zero')
                
#         return constructPrompt_4(function, single_multi_ind, error_type_list)

#     else:  
#         raise RuntimeError("Other Prompts to be implemented!")

# def constructPrompt_1(buggy_function):
#     user_message = (
#     f"""You are a automated program repair tool for C and C++. Your task is to provide a fix for the buggy function in <<<>>>, along with a confidence score for your repaired function.
# Also, for each error you find in the buggy function, please provide its line number and error type.
# You will first respond with your repaired function, then respond with a JSON object with your explanations, line number and error type of every error you find, and Confidence.

# Here is the template of the JSON code you will return to me:
# ```json
# {{
#   "error": [
#     {{
#       "line_number": 
#       "error_type": 
#       "explanation": <Do not include backslash and double quote characters here>
#     }}
#   ],
#   "confidence":
# }}
# ```

# <<< Buggy function:
# {buggy_function}
# >>>
# """
#     )
#     return user_message

# def constructPrompt_2(buggy_function: str, single_multi_ind: int, error_types: list) -> str:
#     bug_annotation_line = ""
#     et_string = ' and '.join(e for e in error_types)
#     if single_multi_ind == 1: 
#         bug_line_str = "there is a single-line error that"
#         bug_annotation_line = (f'In the buggy function, {bug_line_str} produces {et_string}.')
#     elif single_multi_ind == 2:
#         bug_line_str = "You need to modify multiple lines in the function to fix the bug"
#         bug_annotation_line = (f'In the buggy function, the bug produces {et_string}. {bug_line_str}.')
#     else:
#         raise RuntimeError("Input Error: single_multi_ind can only be 1(single-line error) or 2(multi-line error)!")
    
#     user_message = (
#     f"""You are a automated program repair tool for C and C++. Your task is to provide a fix for the buggy function in <<<>>>, along with a confidence score for your repaired function.
# {bug_annotation_line}
# You will first respond with your repaired function, then respond with a JSON object with your explanations, line number and error type of every error you find, and Confidence.

# Here is the template of the JSON code you will return to me:
# ```json
# {{
#   "error": [
#     {{
#       "line_number": 
#       "error_type": 
#       "explanation": <Do not include backslash and double quote characters here>
#     }}
#   ],
#   "confidence":
# }}
# ```

# <<< Buggy function:
# {buggy_function}
# >>>
# """
#     )
#     return user_message

# def constructPrompt_3(buggy_function_with_label: str) -> str:
#     user_message = (
#     f"""You are a automated program repair tool for C and C++. Your task is to provide a fix for the buggy function in <<<>>>, along with a confidence score for your repaired function.
# In the buggy function, the buggy code is already located for you within <start_bug> and <end_bug>.
# You will first respond with your repaired function, then respond with a JSON object with your explanations, line number and error type of every error you find, and Confidence.

# And here is the template of the JSON code you will return to me:
# ```json
# {{
#   "error": [
#     {{
#       "line_number": 
#       "error_type": 
#       "explanation": <Do not include backslash and double quote characters here>
#     }}
#   ],
#   "confidence":
# }}
# ```

# <<< Buggy function:
# {buggy_function_with_label}
# >>>
# """
#     )
#     return user_message

# def constructPrompt_4(buggy_function_with_label: str, single_multi_ind: int, error_types: list) -> str:
#     # check if error_types is empty
#     if not error_types: 
#         raise RuntimeError("Error Type List is empty!")

#     bug_annotation_line = ""
#     et_string = ' and '.join(e for e in error_types)
#     if single_multi_ind == 1: 
#         bug_line_str = "there is a single-line error that"
#         bug_annotation_line = (f'In the buggy function, {bug_line_str} is already located for you within <start_bug> and <end_bug>. The bug produces {et_string}.')
    
#     elif single_multi_ind == 2:
#         bug_line_str = "You need to modify multiple lines in the function to fix the bug"
#         bug_annotation_line = (f'In the buggy function, the buggy code is already located for you within <start_bug> and <end_bug>. The bug produces {et_string}. {bug_line_str}.')
    
#     else:
#         raise RuntimeError("Input Error: single_multi_ind can only be 1(single-line error) or 2(multi-line error)!")
    
#     user_message = (
#     f"""You are a automated program repair tool for C and C++. Your task is to provide a fix for the buggy function in <<<>>>, along with a confidence score for your repaired function.
# {bug_annotation_line}
# You will first respond with your repaired function, then respond with a JSON object with your explanations, line number and error type of every error you find, and Confidence.

# Here is the template of the JSON code you will return to me:
# ```json
# {{
#   "error": [
#     {{
#       "line_number": 
#       "error_type": 
#       "explanation": <Do not include backslash and double quote characters here>
#     }}
#   ],
#   "confidence":
# }}
# ```

# <<< Buggy function:
# {buggy_function_with_label}
# >>>
# """
#     )
#     return user_message

# # Input: a buggy_repo_name: str
# # Output: buggy_function_str(assume to be a single function), error_line_number_list, buggy_function_labeled_str (for prompt 3)
# def buggyFuncStrGetter(buggy_repo: str, isRQ3=False):
#     # download repo data
#     dataset_api.download_buggy_data_by_repo(buggy_repo)
    
#     # get buggy code Musheng's api
#     if not isRQ3: buggy_function = dataset_api.get_buggy_function_by_repo(buggy_repo)
#     else : buggy_function = dataset_api.get_buggy_function_by_repo_rq3(buggy_repo)
#     key_code_file_str = list(buggy_function.keys())[0]
#     buggy_func_str = buggy_function[key_code_file_str]["function"]
#     true_error_line_list = buggy_function[key_code_file_str]["buggy_line_no"]

#     # get buggy code with label
#     if not isRQ3: buggy_function_with_label = dataset_api.get_buggy_function_with_label_repo(buggy_repo)
#     else : buggy_function_with_label = dataset_api.get_buggy_function_with_label_repo_rq3(buggy_repo)
#     buggy_func_with_label_str = buggy_function_with_label[key_code_file_str]["function"]

#     return buggy_func_str, true_error_line_list, buggy_func_with_label_str

# # Input: TXT file path 
# # Output: repaired_func_byLLM, confidence_score, lin_num_list, error_type_list, explanations_list
# def extractLLMOutputFromFile(filepath):
#     file = open(filepath, 'r')
#     content = file.read()
#     pattern = r'^```(?:\w+)?\s*\n(.*?)(?=^```)```'
#     result = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
#     repaired_func_byLLM = result[0]
#     respond_json_byLLM_str = result[1]
#     respond_json_byLLM = json.loads(respond_json_byLLM_str)
#     confidence_score = respond_json_byLLM["confidence"]

#     # create list for line_number, error_type and explanation for errors find by LLM
#     lin_num_list = []
#     error_type_list = []
#     explanations_list = []
#     error_num = len(respond_json_byLLM["error"])
#     for i in range(error_num):
#         lin_num_list.append(respond_json_byLLM["error"][i]["line_number"])
#         error_type_list.append(respond_json_byLLM["error"][i]["error_type"])
#         explanations_list.append(respond_json_byLLM["error"][i]["explanation"])

#     file.close()

#     return repaired_func_byLLM, confidence_score, lin_num_list, error_type_list, explanations_list

# def extractLLMOutputFromFile2(filepath):
#     file = open(filepath, 'r')
#     content = file.read()
#     pattern = r'^```(?:\w+)?\s*\n(.*?)(?=^```)```'
#     result = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
#     repaired_func_byLLM = result[0]

#     # respond_json_byLLM_str = result[1]
#     # respond_json_byLLM = json.loads(respond_json_byLLM_str)
#     # confidence_score = respond_json_byLLM["confidence"]

#     # # create list for line_number, error_type and explanation for errors find by LLM
#     # lin_num_list = []
#     # error_type_list = []
#     # explanations_list = []
#     # error_num = len(respond_json_byLLM["error"])
#     # for i in range(error_num):
#     #     lin_num_list.append(respond_json_byLLM["error"][i]["line_number"])
#     #     error_type_list.append(respond_json_byLLM["error"][i]["error_type"])
#     #     explanations_list.append(respond_json_byLLM["error"][i]["explanation"])

#     file.close()
#     return repaired_func_byLLM 

# # Input: LLM reply string
# # Output: modified LLM reply by changing c++ to cpp, and the line_offset
# def regularizationLLMOutputFromStr(content: str):
#     copy_list = []
#     markline = '```'
#     mark_linnum = 0
#     set_flag = True
#     for line in content.splitlines():
#         if set_flag: mark_linnum += 1
#         if line.startswith(markline) and set_flag:
#             line = line.replace('+', 'p')
#             set_flag = False
#         copy_list.append(line)
    
#     content_modstr = '\n'.join(copy_list)
#     return content_modstr, mark_linnum

# # Input: json code snippet, multiline string
# # Output: remove every backslash in the input
# # can only handle backslash now
# def removeInvalidCharactersFromJSONCodeSnippet(multistr):
#     copy_list = []
#     for line in multistr.splitlines():
#         line = line.replace('\\','')
#         copy_list.append(line)
    
#     modified_str = '\n'.join(copy_list)
#     return modified_str

# # Input: LLM Response
# # Output: repaired_func_byLLM
# def extractFuncStrFromLLMResponse(content: str) -> str:
#     # need to convert c++ to cpp and calculate line offset
#     content_new, _ = regularizationLLMOutputFromStr(content)
#     pattern = r'^```(?:\w+)?\s*\n(.*?)(?=^```)```'
#     result = re.findall(pattern, content_new, re.DOTALL | re.MULTILINE)
#     repaired_func_byLLM = result[0]
#     return repaired_func_byLLM

# # Input: string 
# # Output: repaired_func_byLLM, confidence_score, lin_num_list, error_type_list, explanations_list
# def extractLLMOutputFromStr(content: str) -> parsedLLMRespond:
#     # need to convert c++ to cpp and calculate line offset
#     content_new, mark_linnum = regularizationLLMOutputFromStr(content)

#     pattern = r'^```(?:\w+)?\s*\n(.*?)(?=^```)```'
#     result = re.findall(pattern, content_new, re.DOTALL | re.MULTILINE)
#     repaired_func_byLLM = result[0]
#     respond_json_byLLM_str = result[1]

#     # check if the json code snippets contain the invalid backslash characher
#     if '\\' in respond_json_byLLM_str: respond_json_byLLM = json.loads(removeInvalidCharactersFromJSONCodeSnippet(respond_json_byLLM_str))
#     else:                              respond_json_byLLM = json.loads(respond_json_byLLM_str)

#     confidence_score = respond_json_byLLM["confidence"]

#     # create list for line_number, error_type and explanation for errors find by LLM
#     lin_num_list = []
#     error_type_list = []
#     explanations_list = []
#     error_num = len(respond_json_byLLM["error"])
#     for i in range(error_num):
#         lin_num_list.append(respond_json_byLLM["error"][i]["line_number"] - mark_linnum)
#         error_type_list.append(respond_json_byLLM["error"][i]["error_type"])
#         explanations_list.append(respond_json_byLLM["error"][i]["explanation"])
    
#     return parsedLLMRespond(repaired_func_byLLM, confidence_score, lin_num_list, error_type_list, explanations_list, mark_linnum)

# def extractLLMOutputFromStr2(content: str) -> parsedLLMRespond:
#     # need to convert c++ to cpp and calculate line offset
#     # content_new, mark_linnum = regularizationLLMOutputFromStr(content)
#     content_new = content

#     pattern = r'^```(?:\w+)?\s*\n(.*?)(?=^```)```'	
#     # print('content_new: ', content_new)
#     result = re.findall(pattern, content_new, re.DOTALL | re.MULTILINE)
#     repaired_func_byLLM = result[0]

#     return repaired_func_byLLM 

# # Input: Prompt index, true_error_line_num_list, A parsedLLMRespond object, A TestResult object
# # Output: A EvalLLM object
# def evalLLMRespondGetter(prompt_ind: int , true_errlin_num_list: list , response_time: float,
#                             parsed_llm_respond: parsedLLMRespond, test_result_obj) -> evalLLMRespond:
#     build_result = test_result_obj.build_result
#     confidence_score = parsed_llm_respond.confidence
#     this_pass_rate = test_result_obj.test_cases_result.pass_rate    
#     line_offset = parsed_llm_respond.line_offset
#     llm_errorlin_list = parsed_llm_respond.errlin_num_list
#     correct_lin_num = 0
#     for error_line in llm_errorlin_list:
#         if (error_line in true_errlin_num_list) or ((error_line+line_offset) in true_errlin_num_list):
#             correct_lin_num += 1
#     identify_accuracy = correct_lin_num/len(llm_errorlin_list)    if len(llm_errorlin_list)>0 else 0.0
#     pass_testcases_num = len(test_result_obj.test_cases_result.pass_test_cases)
#     fail_testcases_num = len(test_result_obj.test_cases_result.fail_test_cases)    
#     return evalLLMRespond(prompt_ind, confidence_score, build_result, identify_accuracy,
#                           this_pass_rate, response_time, pass_testcases_num, fail_testcases_num, llm_errorlin_list, true_errlin_num_list)

# def evalLLMRespondGetter2(prompt_ind: int , true_errlin_num_list: list , response_time: float, 
#                             parsed_llm_respond: parsedLLMRespond, test_result_obj) -> evalLLMRespond:

#     build_result = test_result_obj.build_result
#     # confidence_score = parsed_llm_respond.confidence
#     this_pass_rate = test_result_obj.test_cases_result.pass_rate
    
#     # calculate identify_accuracy
#     # line_offset = parsed_llm_respond.line_offset
#     # llm_errorlin_list = parsed_llm_respond.errlin_num_list
#     correct_lin_num = 0
#     # for error_line in llm_errorlin_list:
#     #     if (error_line in true_errlin_num_list) or ((error_line+line_offset) in true_errlin_num_list):
#     #         correct_lin_num += 1
#     # identify_accuracy = correct_lin_num/len(llm_errorlin_list) if len(llm_errorlin_list) > 0 else 0.0
    
#     pass_testcases_num = len(test_result_obj.test_cases_result.pass_test_cases)
#     fail_testcases_num = len(test_result_obj.test_cases_result.fail_test_cases)

#     # return an evalLLMRespond Object
#     return evalLLMRespond(prompt_ind, -1, build_result, -1,
#                           this_pass_rate, response_time, pass_testcases_num, fail_testcases_num, [], true_errlin_num_list) 

# # Input: a base directory, a result object returned by 'dataset_api.test_buggy_codes'
# # Output: a successful message:
# def saveTestResultTXT(output_dir: str, result_obj):
#     os.makedirs(output_dir, exist_ok=True)
#     filename = 'test_output.txt'
#     repo_filename = result_obj.repo_name + '_' + filename
#     output_file = open(os.path.join(output_dir, repo_filename), "w")
#     output_file.write('test_result: \n')
#     output_file.write(f'{result_obj.repo_name}: \n')
#     output_file.write(f'build_result: {result_obj.build_result}\n')
#     output_file.write(f'test_cases_result:  \n')
#     output_file.write(f'pass_rate: {result_obj.test_cases_result.pass_rate}\n')
#     output_file.write(f'pass_test_cases: {result_obj.test_cases_result.pass_test_cases}\n')
#     output_file.write(f'fail_test_cases: {result_obj.test_cases_result.fail_test_cases}\n')
#     output_file.close()

#     # successful message
#     print(f"  Success: write {repo_filename} into {output_dir} .")

# # Input: a base directory, a result object returned by 'dataset_api.test_buggy_codes'
# # Output: a successful message:
# def saveTestResultTXTwithName(output_dir: str, result_obj, filename : str, isRQ2 = False):
#     os.makedirs(output_dir, exist_ok=True)
#     repo_filename = result_obj.repo_name + '_' + filename
#     output_file = open(os.path.join(output_dir, repo_filename), "w")
#     output_file.write('test_result: \n')
#     output_file.write(f'{result_obj.repo_name}: \n')
#     output_file.write(f'build_result: {result_obj.build_result}\n')
#     output_file.write(f'test_cases_result:  \n')
#     output_file.write(f'pass_rate: {result_obj.test_cases_result.pass_rate}\n')
#     output_file.write(f'pass_test_cases: {result_obj.test_cases_result.pass_test_cases}\n')
#     output_file.write(f'fail_test_cases: {result_obj.test_cases_result.fail_test_cases}\n')
#     if isRQ2: output_file.write(f'fail_test_cases_info: {result_obj.test_cases_result.fail_test_cases_info}\n')
#     output_file.close()

#     # successful message
#     print(f"  Success: write {repo_filename} into {output_dir} .")


# # Input: a base directory, the LLM's respond string
# # Output: a successful message:
# def saveLLMReply(output_dir: str, LLM_respond_str: str):
#     os.makedirs(output_dir, exist_ok=True)
#     filename = 'llm_reply.txt'
#     f = open(os.path.join(output_dir, filename), "w")
#     f.write(LLM_respond_str)
#     f.close()

#     # successful message
#     print(f"  Success: write {filename} into {output_dir} .")

# # Input: a base directory, a evalLLMRespond object
# # Output: a successful message
# def saveEvalLLMObjTXT(output_dir: str, eval_llm_obj: evalLLMRespond):
#     os.makedirs(output_dir, exist_ok=True)
#     filename = 'llm_eval_output.txt'
#     f = open(os.path.join(output_dir, filename), "w")
#     f.write('eval_result: \n')
#     f.write(f'prompt_index: {eval_llm_obj.prompt_ind}\n')
#     f.write(f'confidence_score: {eval_llm_obj.confidence}\n')
#     f.write(f'build_result: {int(eval_llm_obj.build_result)}\n')
#     f.write(f'identify_accuracy: {eval_llm_obj.identify_accuracy}\n')
#     f.write(f'pass_rate: {eval_llm_obj.pass_rate}\n')
#     f.write(f'response_time: {eval_llm_obj.response_time}\n')
#     f.write(f'pass_testcases_num: {eval_llm_obj.pass_testcases_num}\n')
#     f.write(f'fail_testcases_num: {eval_llm_obj.fail_testcases_num}\n')
#     f.write(f'llm_errline_num_list: {eval_llm_obj.llm_error_line_list}\n')
#     f.write(f'true_errline_num_list: {eval_llm_obj.true_error_line_list}\n')
#     f.close()
#     # successful message
#     print(f"  Success: write {filename} into {output_dir} .")

# # Input: a base-directory
# # Input: a 2-level list return by run_exps_from_buggyrepolist
# # Output: a successful message
# def saveRepoAvgStatCSV(output_dir: str, repo_stat_list: list, prompt_id: int):
#     # first check if the input prompt_id matches the list
#     if repo_stat_list[0][1] != prompt_id: raise RuntimeError(f"Input Prompt_ID: {prompt_id} mismatch!")

#     now = datetime.now()
#     timestamp_str = now.strftime("%m%d%Y_%H%M%S")
#     filename = "repo_stat_Prompt-" + str(prompt_id) + "_" + timestamp_str + ".csv"
#     # field names
#     fields = ['Test_Repo', 'Prompt_ID', 'Repeat_Num', 'Total_Patch_Num', 'Compilable_Patch_Num', 'Plausible_Patch_Num', 
#               'Average_Response_Time', 'Average_Confidence', 'Average_Identify_Accuracy', 'Average_Pass_Rate']
    
#     # Check num of field names in input repo_stat_list
#     if len(repo_stat_list[0]) != 10: raise RuntimeError("Input Repo List Field Number Mismatch!")

#     # writing to csv file
#     with open(os.path.join(output_dir, filename), 'w') as csvfile:
#         csvwriter = csv.writer(csvfile)
#         # writing the fields
#         csvwriter.writerow(fields)
#         # writing the data rows
#         csvwriter.writerows(repo_stat_list)
#     # successful message
#     print(f"  Success: write {filename} into {output_dir} .")

# def saveRepoAvgStatCSV2(output_dir: str, repo_stat_list: list, prompt_id: int):
#     # first check if the input prompt_id matches the list
#     # if repo_stat_list[0][1] != prompt_id: raise RuntimeError(f"Input Prompt_ID: {prompt_id} mismatch!")

#     now = datetime.now()
#     timestamp_str = 'run_1'
#     filename = "repo_stat_" + str(prompt_id) + '_' + timestamp_str + ".csv"
#     fields = ['Test_Repo', 'Prompt_ID', 'Repeat_Num', 'Total_Patch_Num', 'Compilable_Patch_Num', 'Plausible_Patch_Num', 
#               'Average_Response_Time', 'Average_Confidence', 'Average_Identify_Accuracy', 'Average_Pass_Rate']

#     # Check num of field names in input repo_stat_list
#     # if len(repo_stat_list[0]) != 10: raise RuntimeError("Input Repo List Field Number Mismatch!")

#     # writing to csv file
#     with open(os.path.join(output_dir, filename), 'a') as csvfile:
#         csvwriter = csv.writer(csvfile)
#         # writing the fields
#         # csvwriter.writerow(fields)
#         # writing the data rows
#         # print(repo_stat_list)
#         csvwriter.writerows([repo_stat_list])

#     # successful message
#     print(f"  Success: write {filename} into {output_dir} .")



import os
import re
import json
import csv
from datetime import datetime
import dataset_api

# RS_1: single-line - invalid-condition: , num: 13
repair_scenarios_1_safe  = ['berry-5', 'cpp_peglib-4', 'cppcheck-8', 
                        'cppcheck-9', 'cppcheck-11', 'cppcheck-25', 'exiv2-13', 'exiv2-15', 
                        'libtiff-1', 'openssl-14', 'openssl-24', 'yara-1', 'yara-2', 'berry-3']

# RS_2: single-line - invalid-format-string: , num: 4
repair_scenarios_2_full = ['cpp_peglib-8', 'dlt_daemon-1', 'exiv2-20', 'yaml_cpp-6']
repair_scenarios_2_safe = ['dlt_daemon-1', 'exiv2-20', 'yaml_cpp-6']

# RS_3: single-line - memory-error: , num: 14
repair_scenarios_3_safe_full = ['dlt_daemon-1', 'libtiff-1', 'ndpi-1']
repair_scenarios_3_safe = ['dlt_daemon-1', 'libtiff-1']

repos_with_modification = ['berry-1', 'berry-3', 'berry-4', 'libtiff-1', 'libtiff-2', 'libucl-1']
repos_with_omission = ['berry-2', 'libtiff-3', 'libtiff-4', 'libtiff-5', 'libucl-4']
repos_with_logical_error = ['berry-4', 'libucl-3', 'libucl-2']
repos_with_CVE = ['libtiff-1', 'libtiff-3', 'libtiff-5']
repos_with_zero_division = ['libtiff-3', 'libtiff-4']

class parsedLLMRespond:
    def __init__(self, repaired_func_str: str, confidence: float, errlin_num_list: list,
                 error_type_list: list, explan_list: list, line_offset: int) -> None:

        self.repaired_func_str = repaired_func_str
        self.confidence = confidence
        self.errlin_num_list = errlin_num_list
        self.error_type_list = error_type_list
        self.explan_list = explan_list
        self.line_offset = line_offset


class evalLLMRespond:
    def __init__(self, prompt_ind: int, confidence: float, build_result: bool,
                 identify_errline_accuracy: float, pass_rate: float, response_time: float,
                 pass_testcases_num: int, fail_testcases_num: int, llm_error_line_list: list, true_error_line_list: list) -> None:

        self.prompt_ind = prompt_ind
        self.confidence = confidence
        self.build_result = build_result
        self.identify_accuracy = identify_errline_accuracy
        self.pass_rate = pass_rate
        self.response_time = response_time
        self.pass_testcases_num = pass_testcases_num
        self.fail_testcases_num = fail_testcases_num
        self.llm_error_line_list = llm_error_line_list
        self.true_error_line_list = true_error_line_list

def get_safe_repair_scenario_list(index: int) -> list:
    if index == 1: return repair_scenarios_1_safe
    elif index == 2: return repair_scenarios_2_safe
    elif index == 3: return repair_scenarios_3_safe
    else: raise RuntimeError("Hi Kid! You want to get something dangerous...")

def constructPrompt(function: str, prompt_id: int, repo_name: str , single_multi_str = 'single-line'):
    if prompt_id == 1: return constructPrompt_1(function)

    elif prompt_id == 2:
        single_multi_ind = 1
        if single_multi_str == 'multi-line': single_multi_ind = 2
        error_type_list = []

        # if single_multi_ind == 1:
        if repo_name in repair_scenarios_1_safe: error_type_list.append('invalid condition')
        if repo_name in repair_scenarios_2_safe: error_type_list.append('invalid format string')
        if repo_name in repair_scenarios_3_safe: error_type_list.append('memory error')
        if repo_name in repos_with_modification: error_type_list.append('error due to modification')
        if repo_name in repos_with_omission: error_type_list.append('error due to omission')
        if repo_name in repos_with_logical_error: error_type_list.append('some logical error')
        if repo_name in repos_with_CVE: error_type_list.append('vulnerability error')
        if repo_name in repos_with_zero_division: error_type_list.append('error due to division by zero')

        return constructPrompt_2(function, single_multi_ind, error_type_list)

    elif prompt_id == 3:
        return constructPrompt_3(function)

    elif prompt_id == 4:
        single_multi_ind = 1
        if single_multi_str == 'multi-line':
            single_multi_ind = 2

        error_type_list = []
        # if single_multi_ind == 1:
        if repo_name in repair_scenarios_1_safe: error_type_list.append('invalid condition')
        if repo_name in repair_scenarios_2_safe: error_type_list.append('invalid format string')
        if repo_name in repair_scenarios_3_safe: error_type_list.append('memory error')
        if repo_name in repos_with_modification: error_type_list.append('error due to modification')
        if repo_name in repos_with_omission: error_type_list.append('error due to omission')
        if repo_name in repos_with_logical_error: error_type_list.append('some logical error')
        if repo_name in repos_with_CVE: error_type_list.append('vulnerability error')
        if repo_name in repos_with_zero_division: error_type_list.append('error due to division by zero')

        return constructPrompt_4(function, single_multi_ind, error_type_list)

    else:
        raise RuntimeError("Other Prompts to be implemented!")

def constructPrompt_1(buggy_function):
    user_message = (
    f"""You are a automated program repair tool for C and C++. Your task is to provide a fix for the buggy function in <<<>>>, along with a confidence score for your repaired function.
Also, for each error you find in the buggy function, please provide its line number and error type.
You will first respond with your repaired function, then respond with a JSON object with your explanations, line number and error type of every error you find, and Confidence.

Here is the template of the JSON code you will return to me:
```json
{{
  "error": [
    {{
      "line_number":
      "error_type":
      "explanation": <Do not include backslash and double quote characters here>
    }}
  ],
  "confidence":
}}
```

<<< Buggy function:
{buggy_function}
>>>
"""
    )
    return user_message

def constructPrompt_2(buggy_function: str, single_multi_ind: int, error_types: list) -> str:
    bug_annotation_line = ""
    et_string = ' and '.join(e for e in error_types)
    if single_multi_ind == 1:
        bug_line_str = "there is a single-line error that"
        bug_annotation_line = (f'In the buggy function, {bug_line_str} produces {et_string}.')
    elif single_multi_ind == 2:
        bug_line_str = "You need to modify multiple lines in the function to fix the bug"
        bug_annotation_line = (f'In the buggy function, the bug produces {et_string}. {bug_line_str}.')
    else:
        raise RuntimeError("Input Error: single_multi_ind can only be 1(single-line error) or 2(multi-line error)!")

    user_message = (
    f"""You are a automated program repair tool for C and C++. Your task is to provide a fix for the buggy function in <<<>>>, along with a confidence score for your repaired function.
{bug_annotation_line}
You will first respond with your repaired function, then respond with a JSON object with your explanations, line number and error type of every error you find, and Confidence.

Here is the template of the JSON code you will return to me:
```json
{{
  "error": [
    {{
      "line_number":
      "error_type":
      "explanation": <Do not include backslash and double quote characters here>
    }}
  ],
  "confidence":
}}
```

<<< Buggy function:
{buggy_function}
>>>
"""
    )
    return user_message

def constructPrompt_3(buggy_function_with_label: str) -> str:
    user_message = (
    f"""You are a automated program repair tool for C and C++. Your task is to provide a fix for the buggy function in <<<>>>, along with a confidence score for your repaired function.
In the buggy function, the buggy code is already located for you within <start_bug> and <end_bug>.
You will first respond with your repaired function, then respond with a JSON object with your explanations, line number and error type of every error you find, and Confidence.

And here is the template of the JSON code you will return to me:
```json
{{
  "error": [
    {{
      "line_number":
      "error_type":
      "explanation": <Do not include backslash and double quote characters here>
    }}
  ],
  "confidence":
}}
```

<<< Buggy function:
{buggy_function_with_label}
>>>
"""
    )
    return user_message

def constructPrompt_4(buggy_function_with_label: str, single_multi_ind: int, error_types: list) -> str:
    # check if error_types is empty
    if not error_types:
        raise RuntimeError("Error Type List is empty!")

    bug_annotation_line = ""
    et_string = ' and '.join(e for e in error_types)
    if single_multi_ind == 1:
        bug_line_str = "there is a single-line error that"
        bug_annotation_line = (f'In the buggy function, {bug_line_str} is already located for you within <start_bug> and <end_bug>. The bug produces {et_string}.')

    elif single_multi_ind == 2:
        bug_line_str = "You need to modify multiple lines in the function to fix the bug"
        bug_annotation_line = (f'In the buggy function, the buggy code is already located for you within <start_bug> and <end_bug>. The bug produces {et_string}. {bug_line_str}.')

    else:
        raise RuntimeError("Input Error: single_multi_ind can only be 1(single-line error) or 2(multi-line error)!")

    user_message = (
    f"""You are a automated program repair tool for C and C++. Your task is to provide a fix for the buggy function in <<<>>>, along with a confidence score for your repaired function.
{bug_annotation_line}
You will first respond with your repaired function, then respond with a JSON object with your explanations, line number and error type of every error you find, and Confidence.

Here is the template of the JSON code you will return to me:
```json
{{
  "error": [
    {{
      "line_number":
      "error_type":
      "explanation": <Do not include backslash and double quote characters here>
    }}
  ],
  "confidence":
}}
```

<<< Buggy function:
{buggy_function_with_label}
>>>
"""
    )
    return user_message

# Input: a buggy_repo_name: str
# Output: buggy_function_str(assume to be a single function), error_line_number_list, buggy_function_labeled_str (for prompt 3)
def buggyFuncStrGetter(buggy_repo: str):
    dataset_api.download_buggy_data_by_repo(buggy_repo)
    buggy_function = dataset_api.get_buggy_function_by_repo(buggy_repo)

    if not buggy_function:
        print(f"No data returned for {buggy_repo}.")
        return None, None, None

    key_code_file_str = next(iter(buggy_function.keys()), None)
    if key_code_file_str is None:
        print(f"No function keys found in the data for {buggy_repo}.")
        return None, None, None

    buggy_func_data = buggy_function.get(key_code_file_str, {})
    buggy_func_str = buggy_func_data.get("function", "")
    true_error_line_list = buggy_func_data.get("buggy_line_no", [])
    buggy_function_with_label = dataset_api.get_buggy_function_with_label_repo(buggy_repo)
    buggy_func_with_label_str = buggy_function_with_label.get(key_code_file_str, {}).get("function", "")

    return buggy_func_str, true_error_line_list, buggy_func_with_label_str


# Input: TXT file path
# Output: repaired_func_byLLM, confidence_score, lin_num_list, error_type_list, explanations_list
def extractLLMOutputFromFile(filepath):
    file = open(filepath, 'r')
    content = file.read()
    pattern = r'^```(?:\w+)?\s*\n(.*?)(?=^```)```'
    result = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
    repaired_func_byLLM = result[0]
    respond_json_byLLM_str = result[1]
    respond_json_byLLM = json.loads(respond_json_byLLM_str)
    confidence_score = respond_json_byLLM["confidence"]

    # create list for line_number, error_type and explanation for errors find by LLM
    lin_num_list = []
    error_type_list = []
    explanations_list = []
    error_num = len(respond_json_byLLM["error"])
    for i in range(error_num):
        lin_num_list.append(respond_json_byLLM["error"][i]["line_number"])
        error_type_list.append(respond_json_byLLM["error"][i]["error_type"])
        explanations_list.append(respond_json_byLLM["error"][i]["explanation"])

    file.close()

    return repaired_func_byLLM, confidence_score, lin_num_list, error_type_list, explanations_list

def extractLLMOutputFromFile2(filepath):
    file = open(filepath, 'r')
    content = file.read()
    pattern = r'^```(?:\w+)?\s*\n(.*?)(?=^```)```'
    result = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
    repaired_func_byLLM = result[0]

    file.close()
    return repaired_func_byLLM

# Input: LLM reply string
# Output: modified LLM reply by changing c++ to cpp, and the line_offset
def regularizationLLMOutputFromStr(content: str):
    copy_list = []
    markline = '```'
    mark_linnum = 0
    set_flag = True
    for line in content.splitlines():
        if set_flag: mark_linnum += 1
        if line.startswith(markline) and set_flag:
            line = line.replace('+', 'p')
            set_flag = False
        copy_list.append(line)

    content_modstr = '\n'.join(copy_list)
    return content_modstr, mark_linnum

# Input: json code snippet, multiline string
# Output: remove every backslash in the input
# can only handle backslash now
def removeInvalidCharactersFromJSONCodeSnippet(multistr):
    copy_list = []
    for line in multistr.splitlines():
        line = line.replace('\\','')
        copy_list.append(line)

    modified_str = '\n'.join(copy_list)
    return modified_str

# Input: string
# Output: repaired_func_byLLM, confidence_score, lin_num_list, error_type_list, explanations_list
def extractLLMOutputFromStr(response_str):
    # Split the response assuming a marker separates the repaired function from the JSON metadata
    parts = response_str.split('```json')
    if len(parts) < 2:
        print("LLM's response does not contain separable JSON metadata.")
        return None

    # Attempt to reassemble the JSON part correctly for parsing
    json_str = '```json'.join(parts[1:])
    # Remove any potential formatting issues that could invalidate the JSON
    json_str = json_str.replace('```', '').strip()

    try:
        # Attempt to parse the JSON part of the response
        json_data = json.loads(json_str)
        # Assuming the first part is the repaired function
        repaired_function = parts[0].strip()
        return {'repaired_function': repaired_function, 'json_data': json_data}
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Problematic JSON string: {json_str[:500]}")  # Print the start of the problematic JSON string
        return None


def extractLLMOutputFromStr2(content: str) -> parsedLLMRespond:
    # need to convert c++ to cpp and calculate line offset
    # content_new, mark_linnum = regularizationLLMOutputFromStr(content)
    content_new = content

    pattern = r'^```(?:\w+)?\s*\n(.*?)(?=^```)```'
    # print('content_new: ', content_new)
    result = re.findall(pattern, content_new, re.DOTALL | re.MULTILINE)
    repaired_func_byLLM = result[0]

    return repaired_func_byLLM

# Input: Prompt index, true_error_line_num_list, A parsedLLMRespond object, A TestResult object
# Output: A EvalLLM object
def evalLLMRespondGetter(prompt_ind: int , true_errlin_num_list: list , response_time: float,
                            parsed_llm_respond: parsedLLMRespond, test_result_obj) -> evalLLMRespond:
    build_result = test_result_obj.build_result
    confidence_score = parsed_llm_respond.get('confidence', 0)
    this_pass_rate = test_result_obj.test_cases_result.pass_rate
    line_offset = parsed_llm_respond.get('line_offset', 0)
    llm_errorlin_list = parsed_llm_respond.get('errlin_num_list', [])
    correct_lin_num = 0
    for error_line in llm_errorlin_list:
        if (error_line in true_errlin_num_list) or ((error_line+line_offset) in true_errlin_num_list):
            correct_lin_num += 1
    identify_accuracy = correct_lin_num/len(llm_errorlin_list)    if len(llm_errorlin_list)>0 else 0.0
    pass_testcases_num = len(test_result_obj.test_cases_result.pass_test_cases)
    fail_testcases_num = len(test_result_obj.test_cases_result.fail_test_cases)
    return evalLLMRespond(prompt_ind, confidence_score, build_result, identify_accuracy,
                          this_pass_rate, response_time, pass_testcases_num, fail_testcases_num, llm_errorlin_list, true_errlin_num_list)

def evalLLMRespondGetter2(prompt_ind: int , true_errlin_num_list: list , response_time: float,
                            parsed_llm_respond: parsedLLMRespond, test_result_obj) -> evalLLMRespond:

    build_result = test_result_obj.build_result
    # confidence_score = parsed_llm_respond.confidence
    this_pass_rate = test_result_obj.test_cases_result.pass_rate

    # calculate identify_accuracy
    # line_offset = parsed_llm_respond.line_offset
    # llm_errorlin_list = parsed_llm_respond.errlin_num_list
    correct_lin_num = 0
    # for error_line in llm_errorlin_list:
    #     if (error_line in true_errlin_num_list) or ((error_line+line_offset) in true_errlin_num_list):
    #         correct_lin_num += 1
    # identify_accuracy = correct_lin_num/len(llm_errorlin_list) if len(llm_errorlin_list) > 0 else 0.0

    pass_testcases_num = len(test_result_obj.test_cases_result.pass_test_cases)
    fail_testcases_num = len(test_result_obj.test_cases_result.fail_test_cases)

    # return an evalLLMRespond Object
    return evalLLMRespond(prompt_ind, -1, build_result, -1,
                          this_pass_rate, response_time, pass_testcases_num, fail_testcases_num, [], true_errlin_num_list)

# Input: a base directory, a result object returned by 'dataset_api.test_buggy_codes'
# Output: a successful message:
def saveTestResultTXT(output_dir: str, result_obj):
    os.makedirs(output_dir, exist_ok=True)
    filename = 'test_output.txt'
    repo_filename = result_obj.repo_name + '_' + filename
    output_file = open(os.path.join(output_dir, repo_filename), "w")
    output_file.write('test_result: \n')
    output_file.write(f'{result_obj.repo_name}: \n')
    output_file.write(f'build_result: {result_obj.build_result}\n')
    output_file.write(f'test_cases_result:  \n')
    output_file.write(f'pass_rate: {result_obj.test_cases_result.pass_rate}\n')
    output_file.write(f'pass_test_cases: {result_obj.test_cases_result.pass_test_cases}\n')
    output_file.write(f'fail_test_cases: {result_obj.test_cases_result.fail_test_cases}\n')
    output_file.close()

    # successful message
    print(f"  Success: write {repo_filename} into {output_dir} .")

# Input: a base directory, the LLM's respond string
# Output: a successful message:
def saveLLMReply(output_dir: str, LLM_respond_str: str):
    os.makedirs(output_dir, exist_ok=True)
    filename = 'llm_reply.txt'
    f = open(os.path.join(output_dir, filename), "w")
    f.write(LLM_respond_str)
    f.close()

    # successful message
    print(f"  Success: write {filename} into {output_dir} .")

# Input: a base directory, a evalLLMRespond object
# Output: a successful message
def saveEvalLLMObjTXT(output_dir: str, eval_llm_obj: evalLLMRespond):
    os.makedirs(output_dir, exist_ok=True)
    filename = 'llm_eval_output.txt'
    f = open(os.path.join(output_dir, filename), "w")
    f.write('eval_result: \n')
    f.write(f'prompt_index: {eval_llm_obj.prompt_ind}\n')
    f.write(f'confidence_score: {eval_llm_obj.confidence}\n')
    f.write(f'build_result: {int(eval_llm_obj.build_result)}\n')
    f.write(f'identify_accuracy: {eval_llm_obj.identify_accuracy}\n')
    f.write(f'pass_rate: {eval_llm_obj.pass_rate}\n')
    f.write(f'response_time: {eval_llm_obj.response_time}\n')
    f.write(f'pass_testcases_num: {eval_llm_obj.pass_testcases_num}\n')
    f.write(f'fail_testcases_num: {eval_llm_obj.fail_testcases_num}\n')
    f.write(f'llm_errline_num_list: {eval_llm_obj.llm_error_line_list}\n')
    f.write(f'true_errline_num_list: {eval_llm_obj.true_error_line_list}\n')
    f.close()
    # successful message
    print(f"  Success: write {filename} into {output_dir} .")

# Input: a base-directory
# Input: a 2-level list return by run_exps_from_buggyrepolist
# Output: a successful message
def saveRepoAvgStatCSV(output_dir: str, repo_stat_list: list, prompt_id: int):
    # first check if the input prompt_id matches the list
    if repo_stat_list[0][1] != prompt_id: raise RuntimeError(f"Input Prompt_ID: {prompt_id} mismatch!")

    now = datetime.now()
    timestamp_str = now.strftime("%m%d%Y_%H%M%S")
    filename = "repo_stat_Prompt-" + str(prompt_id) + "_" + timestamp_str + ".csv"
    # field names
    fields = ['Test_Repo', 'Prompt_ID', 'Repeat_Num', 'Total_Patch_Num', 'Compilable_Patch_Num', 'Plausible_Patch_Num',
              'Average_Response_Time', 'Average_Confidence', 'Average_Identify_Accuracy', 'Average_Pass_Rate']

    # Check num of field names in input repo_stat_list
    if len(repo_stat_list[0]) != 10: raise RuntimeError("Input Repo List Field Number Mismatch!")

    # writing to csv file
    with open(os.path.join(output_dir, filename), 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        # writing the fields
        csvwriter.writerow(fields)
        # writing the data rows
        csvwriter.writerows(repo_stat_list)
    # successful message
    print(f"  Success: write {filename} into {output_dir} .")

def saveRepoAvgStatCSV2(output_dir: str, repo_stat_list: list, prompt_id: int):
    # first check if the input prompt_id matches the list
    # if repo_stat_list[0][1] != prompt_id: raise RuntimeError(f"Input Prompt_ID: {prompt_id} mismatch!")

    now = datetime.now()
    timestamp_str = 'run_1'
    filename = "repo_stat_" + str(prompt_id) + '_' + timestamp_str + ".csv"
    fields = ['Test_Repo', 'Prompt_ID', 'Repeat_Num', 'Total_Patch_Num', 'Compilable_Patch_Num', 'Plausible_Patch_Num',
              'Average_Response_Time', 'Average_Confidence', 'Average_Identify_Accuracy', 'Average_Pass_Rate']

    # Check num of field names in input repo_stat_list
    # if len(repo_stat_list[0]) != 10: raise RuntimeError("Input Repo List Field Number Mismatch!")

    # writing to csv file
    with open(os.path.join(output_dir, filename), 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        # writing the fields
        # csvwriter.writerow(fields)
        # writing the data rows
        # print(repo_stat_list)
        csvwriter.writerows([repo_stat_list])

    # successful message
    print(f"  Success: write {filename} into {output_dir} .")