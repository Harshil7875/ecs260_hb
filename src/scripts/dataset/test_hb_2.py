import os
import time
from datetime import datetime
import json
import exp_utils_dev
import dataset_api
import openai
import sys

base_path = '/workspaces/ecs260_hb/src/scripts/dataset/gpt_results'

def run_gpt(user_message, model="gpt-3.5-turbo-0125"):
    # client = OpenAI(api_key=""my_key")
    messages = [
        {"role": "user", "content": f"{user_message}"}
    ]
    chat_response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature = 0.7,
        top_p = 1
    )
    return (chat_response.choices[0].message.content)

prompt4_prefix = '''
You are an Automatic Program Repair Tool. The following C++ code snippet is taken from an open source GitHub Project and contains an error.
Find and fix the bug. Provide the solution in the described format below.
'''
prompt4_suffix = '''
Format your response as follows.


Corrected function:
```
// Corrected function here:
```

For example, for the following function,
```cpp
int fibonacci(int n) {
  if (n <= 1) {
    return fibonacci(n-1) - fibonacci(n-2);
  }
}
```
A sample output is as follows:

Corrected function:
```
int fibonacci(int n) {
  if (n <= 1) {
    return fibonacci(n-1) + fibonacci(n-2);
  }
}
```
'''

HISTORY_MESSAGE = ''' Here is a history of previous interactions. Take them into account to provide a response for the last prompt.
The interactions are formated as follows:

[User Prompt]: <A string describing user prompt>
<Response Ends>

[Your Response]: <A string describing your response>
<Response Ends>

For example a sample interaction is given below:

[User Prompt]:
The following C++ function has an error. Please provide a fix.
```cpp
int fib(int n) {
    return fib(n) - fib(n-1);
}
```
<Prompt Ends>

[Your Response]:  
The provided C++ function fib(int n) has two main errors:

    Incorrect Logic: It attempts to calculate the Fibonacci sequence using subtraction, which is not the correct formula. The Fibonacci sequence is defined as F(n) = F(n-1) + F(n-2), where each number is the sum of the two preceding ones.

    Infinite Recursion: The function calls itself recursively without any base cases to stop the recursion. This causes it to loop infinitely until the program crashes.

Here's a corrected version of the function:
C++
```cpp
int fib(int n) {
    if (n <= 1) {  // Base cases: 0th and 1st Fibonacci numbers are 0 and 1
        return n;
    } else {
        return fib(n-1) + fib(n-2);  // Recursive call with the correct formula
    }
}
```
Use code with caution.

This version implements the correct recursive formula for the Fibonacci sequence and includes base cases to terminate the recursion, ensuring a valid calculation.
<Response Ends>

[User Prompt]: 
Please provide only the code (without explanation)
<Prompt Ends>

[Your Response]:
C++
```cpp
int fib(int n) {
    if (n <= 1) {
        return n;
    } else {
        return fib(n-1) + fib(n-2);
    }
}
```
<Response Ends>

'''



def getPrompt4(repo):
    buggy_func_str, true_errlin_num_list, buggy_func_labeled_str = exp_utils_dev.buggyFuncStrGetter(repo)
    return prompt4_prefix + '```cpp\n' + buggy_func_str + '\n```\n' + prompt4_suffix

def joinHistory(messages, prompt):
    while len(messages) > 3:
        messages.pop()
    messages.append(prompt)
    gen_prompt = messages[0] + "\n"
    if len(messages) > 1:
        gen_prompt += HISTORY_MESSAGE

    for p in range(1, len(messages)-2):
        if p%2 == 1:
            gen_prompt += "\n [Your Response]:\n" + messages[p] + "\n <Response Ends>\n"
        else:
            gen_prompt += "\n [User Prompt]:\n" + messages[p] + "\n <Prompt Ends>\n"
    return gen_prompt


# only for 1 prompt 
def run_exps(buggy_repo : str, prompt : str, gchat) -> list:
    print('*' * 80)
    print(f'Testing buggy repo : {buggy_repo}')
    print('-' * 35 + 'Test Begins:' + '-' * 35)
    print('\n')
     
    output_dir = './exp_results/'
    prompt_ind = 4

    total_patch_num = 0
    compilable_patch_num = 0
    plausible_patch_num = 0
    total_llm_response_time = 0

    # list to record specific patch-prompt-repeat
    compilable_patch_list = []
    plausible_patch_list = []
    # list to record repo-avg-stat
    repo_stat_list = []

    # buggy_repo_num = len(buggy_repo_list)
    total_exp_num = 0 # can calculate the average llm response time

    mlist = [buggy_repo]
    for i in mlist:
        buggy_repo_name = i
        # prompt_dir_name = "prompt_" + str(int(prompt_ind))

        Inrepo_total_patch_num = 0
        Inrepo_compilable_patch_num = 0
        Inrepo_plausible_patch_num = 0
        # can calculate average
        Inrepo_total_llm_response_time = 0
        Inrepo_total_confidence_score = 0
        Inrepo_total_identify_accuracy = 0
        Inrepo_total_pass_rate = 0
        Inrepo_max_pass_rate = 0

        print('^' * 65)
        print(f'Repo: {buggy_repo_name} Test Starts.')
        print('^' * 65)

        # while loop to begin our multiple queries to LLM
        repeat_counter = 0
        retry_counter = 0
        skip_flag = False
        while repeat_counter <= 0:
            retry_flag = False
            # repeat_time_dir_name = "repeat_" + str(int(repeat_counter + 1))
            # output_dir = os.path.join(base_path, buggy_repo_name, prompt_dir_name, repeat_time_dir_name)

            # get buggy function and error_line_number_list from the repo name
            buggy_func_str, true_errlin_num_list, buggy_func_labeled_str = exp_utils_dev.buggyFuncStrGetter(buggy_repo_name)
            # construct input prompt to LLM using prompt_ind and buggy_func_str(or buggy_func_labeled_str)
            # input_prompt_str = exp_utils_dev.constructPrompt(buggy_func_str, prompt_ind, buggy_repo_name)

            # Query LLM using input_prompt_str
            start_t = time.time()
            # LLM_respond_str = run_mistral(input_prompt_str)
            # gemini.configure()
            # gchat = gemini.start_chat()
            # LLM_respond_str = gemini.query_llm2(gchat, prompt)
            final_prompt = joinHistory(gchat, prompt)
            LLM_respond_str = run_gpt(final_prompt)
            print(LLM_respond_str)
            end_t = time.time()
            # the first step after receiving LLM's response is to check if it can be correctly parsed
            try:
                parsed_llm_obj = exp_utils_dev.extractLLMOutputFromStr2(LLM_respond_str)
            except (IndexError, json.decoder.JSONDecodeError) as Error:
                print(f"ERROR: Failed to extract from LLM's response! Details: {Error}")
                print(f"Retry Query: Repeat {repeat_counter+1}.")
                retry_flag = True
                retry_counter += 1
                return [[-1]]
            
            if skip_flag: break 
            if retry_flag: continue

            # Now we parsed LLM's output with no problem
            elapsed_time = end_t - start_t
            print('-' * 65)
            print(f'Repo: {buggy_repo_name} -- Prompt_id: {prompt_ind}. Current Repeat: {repeat_counter+1}. Parse Response Succefully! Time: {elapsed_time} seconds.')
            exp_utils_dev.saveLLMReply(output_dir, LLM_respond_str)

            # Test LLM's repaired function using Musheng's API
            test_result_obj = dataset_api.test_buggy_codes(buggy_repo_name, parsed_llm_obj)
            exp_utils_dev.saveTestResultTXT(output_dir, test_result_obj)

            # Evaulate LLM's reply using test_result_obj and save file
            eval_llm_obj = exp_utils_dev.evalLLMRespondGetter2(prompt_ind, true_errlin_num_list, elapsed_time, parsed_llm_obj, test_result_obj)
            print(f'Repo: {buggy_repo_name} -- Prompt_id: {prompt_ind}. Current Repeat: {repeat_counter+1}. Eval Response Done! Confidence: {eval_llm_obj.confidence}, Build Result: {eval_llm_obj.build_result}, Identify Accuracy: {eval_llm_obj.identify_accuracy}, Pass Rate: {eval_llm_obj.pass_rate}.')
            exp_utils_dev.saveEvalLLMObjTXT(output_dir, eval_llm_obj)
            print('-' * 65)
            # Now we should update experiment metrics here:
            temp_patch_name = buggy_repo_name + "_Prompt-" + str(prompt_ind) + "_Repeat-" + str(repeat_counter+1)
            Inrepo_total_patch_num += 1
            if eval_llm_obj.build_result: 
                Inrepo_compilable_patch_num += 1
                compilable_patch_list.append(temp_patch_name)
                Inrepo_max_pass_rate = max(Inrepo_max_pass_rate, eval_llm_obj.pass_rate)
            if eval_llm_obj.pass_rate > 0.999: 
                Inrepo_plausible_patch_num += 1
                plausible_patch_list.append(temp_patch_name)

            Inrepo_total_llm_response_time += elapsed_time
            Inrepo_total_confidence_score += eval_llm_obj.confidence
            Inrepo_total_identify_accuracy += eval_llm_obj.identify_accuracy
            # when compilation fails, pass rate = 0
            if eval_llm_obj.pass_rate < 0: Inrepo_total_pass_rate += 0
            else:     Inrepo_total_pass_rate += eval_llm_obj.pass_rate

            # update repeat counter!
            repeat_counter += 1

        total_exp_num += repeat_counter
        if repeat_counter > 0:
            Inrepo_average_llm_response_time = Inrepo_total_llm_response_time / repeat_counter 
            Inrepo_average_confidence_score = Inrepo_total_confidence_score / repeat_counter
            Inrepo_average_identify_accuracy = Inrepo_total_identify_accuracy / repeat_counter
            Inrepo_average_pass_rate = Inrepo_total_pass_rate / repeat_counter   
        print('^' * 65)   
        print(f'Repo: {buggy_repo_name} Test Ends. -- Prompt_id: {4}. Actual Repeat Number: {repeat_counter}. Inrepo Total Patch Number: {Inrepo_total_patch_num}, Inrepo Compilable Patch Number: {Inrepo_compilable_patch_num}, Inrepo Plausible Patch Number: {Inrepo_plausible_patch_num}. ')
        print(f'Repo: {buggy_repo_name} Test Statistic -- Average LLM Response Time: {Inrepo_average_llm_response_time}, Average LLM Confidence: {Inrepo_average_confidence_score}, Average Identify Accuracy: {Inrepo_average_identify_accuracy}, Average Pass Rate: {Inrepo_average_pass_rate}. ')

        # record repo-specific test statistics to a list
        temp_avgstat_list = []
        temp_avgstat_list.append(buggy_repo_name)
        temp_avgstat_list.append(4)
        temp_avgstat_list.append(repeat_counter)
        temp_avgstat_list.append(Inrepo_total_patch_num)
        temp_avgstat_list.append(Inrepo_compilable_patch_num)
        temp_avgstat_list.append(Inrepo_plausible_patch_num)
        temp_avgstat_list.append(Inrepo_average_llm_response_time)
        temp_avgstat_list.append(Inrepo_average_confidence_score)
        temp_avgstat_list.append(Inrepo_average_identify_accuracy)
        temp_avgstat_list.append(Inrepo_average_pass_rate)
        temp_avgstat_list.append(Inrepo_max_pass_rate)
        repo_stat_list.append(temp_avgstat_list)

        # write repo-specific test statistics to a txt file
        # avg_stat_filename = buggy_repo_name + '_Prompt-' + str(4) + '_' + 'avgstat.txt'
        # avg_stat_dir = os.path.join(base_path, buggy_repo_name, 'prompt_4/')
        # avg_stat_f = open(os.path.join(avg_stat_dir, avg_stat_filename), 'w')
        # avg_stat_f.write(f'Test_Repo: {buggy_repo_name}\n')
        # avg_stat_f.write(f'Prompt_ID: 4\n')
        # avg_stat_f.write(f'Repeat_Num: {repeat_counter}\n')
        # avg_stat_f.write(f'Total_Patch_Num: {Inrepo_total_patch_num}\n')
        # avg_stat_f.write(f'Compilable_Patch_Num: {Inrepo_compilable_patch_num}\n')
        # avg_stat_f.write(f'Plausible_Patch_Num: {Inrepo_plausible_patch_num}\n')
        # avg_stat_f.write(f'Average_Response_Time: {Inrepo_average_llm_response_time}\n')
        # avg_stat_f.write(f'Average_Confidence: {Inrepo_average_confidence_score}\n')
        # avg_stat_f.write(f'Average_Identify_Accuracy: {Inrepo_average_identify_accuracy}\n')
        # avg_stat_f.write(f'Average_Pass_Rate: {Inrepo_average_pass_rate}\n')
        # avg_stat_f.close()
        # print(f"  Success: write {avg_stat_filename} into {avg_stat_dir} .")
        print('^' * 65)
        print('\n')

        # contribute to global statistics
        total_patch_num += Inrepo_total_patch_num
        compilable_patch_num += Inrepo_compilable_patch_num
        plausible_patch_num += Inrepo_plausible_patch_num
        total_llm_response_time += Inrepo_total_llm_response_time

    average_llm_response_time = total_llm_response_time / total_exp_num

    print(f'All Test Ends. Total Patch Number: {total_patch_num}, Total Compilable Patch Number: {compilable_patch_num}, Total Plausible Patch Number: {plausible_patch_num}, Average LLM Response Time: {average_llm_response_time}. ')
    print('-' * 35 + 'Test   Ends:' + '-' * 35)
    # Write total stat file to a txt file with time stamp
    now = datetime.now()
    timestamp_str = now.strftime("%m%d%Y_%H%M%S")
    total_stat_filename = 'totalstat_' + timestamp_str + '.txt'
    total_stat_f = open(os.path.join(base_path, total_stat_filename), "w")
    total_stat_f.write(f'Test_Buggy_Repo_List: {buggy_repo}\n')
    total_stat_f.write(f'Total_Patch_Number: {total_patch_num}\n')
    total_stat_f.write(f'Total_Compilable_Patch_Number: {compilable_patch_num}\n')
    total_stat_f.write(f'Total_Plausible_Patch_Number: {plausible_patch_num}\n')
    total_stat_f.write(f'Compilable_Patch_List: {compilable_patch_list}\n')
    total_stat_f.write(f'Plausible_Patch_list: {plausible_patch_list}\n')
    total_stat_f.close()
    print(f"  Success: write {total_stat_filename} into {base_path} .")

    return repo_stat_list


def main():
    test_list_1 = ['berry-5']
    # test_list_2 = ['berry-5', 'cpp_peglib-4', 'cppcheck-8']
    # test_list_3 = ['cpp_peglib-4']
    # test_list_5 = ['berry-5','cppcheck-8']
    test_1 = ['cpp_peglib-4']

    # ,'cppcheck-8','cppcheck-9','cppcheck-11','cppcheck-25','exiv2-13','exiv2-15','libtiff-1','openssl-14','openssl-24','yara-1','yara-2'

    # test_1 = ['yara-1','yara-2']
    # test_1 = ['yaml_cpp-6']
    # test_1 = ['dlt_daemon-1', 'libtiff-1']


    # test_1 = ['berry-5']

    # file_obj = open('bug_files.json')
    # data = json.load(file_obj)
    # test_repo = list(data.keys())
    # test_repo = test_repo[int(sys.argv[1]):int(sys.argv[2])]
    # print(test_repo)
    # file_obj.close()

    rp1_list = exp_utils_dev.get_safe_repair_scenario_list(1) # get safe repair scenario 1
    rp2_list = exp_utils_dev.get_safe_repair_scenario_list(2) # get safe repair scenario 2
    rp3_list = exp_utils_dev.get_safe_repair_scenario_list(3) # get safe repair scenario 3
    
    # gemini.configure()
    messages = []

    for repo in test_1:
        prompt = getPrompt4(repo)
        messages.append(prompt)
        # gchat = gemini.start_chat()
        comp_limit = 3
        pass_limit = 3
        prompt_limit = 3
        got_plausible = False
        pno = 0
        while comp_limit > 0 and pass_limit > 0 and prompt_limit > 0:
            print("Prompt:\n", prompt, "\n\n" + "-"*10 + "Prompt Done" + "-"*10)
            go = run_exps(repo, prompt, messages)
            go = go[0]
            go.append(pno)
            print("-"*10 + "GO" + "-"*10, go, "\n\n\n\n")
            if go[0] == -1:
                prompt_limit -= 1
                prompt = 'The previous solution did not match the output specifications. Please format the output correctly.'
                pno = 1
            elif go[4] != 1:
                comp_limit -= 1
                pass_limit = 3
                prompt_limit = 3
                prompt = 'The previous solution did not compile. Please provide another solution.'
                pno = 2
            elif go[9] < 0.9999:
                pass_limit -= 1
                prompt = '''
                The previous solution did not pass all testcases. Please provide another solution.
                The pass rate was : 
                '''
                prompt += str(go[9])
                pno = 3
            else:
                got_plausible = True 
                prompt = 'The previous solution was correct! Can you provide another solution?'
                pno = 4
            print("-"*10 + "Result array" + "-"*10 + "\n")
            print(go)
            print("-"*10 + "Result end" + "-"*10 + "\n")
            exp_utils_dev.saveRepoAvgStatCSV2('./exp_results/', go, 4)
        if got_plausible:
            file_obj = open('./plausible.txt', 'a')
            file_obj.write(repo)
            print(repo, ' Got Plausible Patch!')
            file_obj.close()



if __name__ == "__main__":
    main()