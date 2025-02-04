import os
import shutil
import subprocess
from typing import List
from utils import TypeEnum, json_default_val

py_type = {
    TypeEnum.BOOL: 'bool',
    TypeEnum.INT: 'int',
    TypeEnum.LONG: 'int',
    TypeEnum.DOUBLE: 'float',
    TypeEnum.STRING: 'str',
    TypeEnum.INT_LIST: 'List[int]',
    TypeEnum.INT_LIST_LIST: 'List[List[int]]',
    TypeEnum.DOUBLE_LIST: 'List[float]',
    TypeEnum.STRING_LIST: 'List[str]',
    TypeEnum.BOOL_LIST: 'List[bool]',
    TypeEnum.TREENODE: 'TreeNode',
    TypeEnum.LISTNODE: 'ListNode',
    TypeEnum.LONG_LIST : 'List[int]'
}

py_default_val = {
    TypeEnum.BOOL : 'False',
    TypeEnum.INT : '0',
    TypeEnum.LONG : '0',
    TypeEnum.DOUBLE : '0.0',
    TypeEnum.STRING: '""',
    TypeEnum.INT_LIST: '[]',
    TypeEnum.INT_LIST_LIST: '[]',
    TypeEnum.DOUBLE_LIST: '[]',
    TypeEnum.STRING_LIST: '[]',
    TypeEnum.BOOL_LIST: '[]',
    TypeEnum.TREENODE: 'None',
    TypeEnum.LISTNODE: 'None',
    TypeEnum.LONG_LIST : '[]'
}

des_func_name = {
    TypeEnum.BOOL : 'des_bool',
    TypeEnum.INT : 'des_int',
    TypeEnum.LONG : 'des_long',
    TypeEnum.DOUBLE : 'des_double',
    TypeEnum.STRING: 'des_string',
    TypeEnum.INT_LIST: 'des_int_list',
    TypeEnum.INT_LIST_LIST: 'des_int_list_list',
    TypeEnum.DOUBLE_LIST: 'des_double_list',
    TypeEnum.STRING_LIST: 'des_string_list',
    TypeEnum.BOOL_LIST: 'des_bool_list',
    TypeEnum.TREENODE: 'des_tree',
    TypeEnum.LISTNODE: 'des_linked_list',
    TypeEnum.LONG_LIST : 'des_long_list'
}

ser_func_name = {
    TypeEnum.BOOL : 'ser_bool',
    TypeEnum.INT : 'ser_int',
    TypeEnum.LONG : 'ser_long',
    TypeEnum.DOUBLE : 'ser_double',
    TypeEnum.STRING: 'ser_string',
    TypeEnum.INT_LIST: 'ser_int_list',
    TypeEnum.INT_LIST_LIST: 'ser_int_list_list',
    TypeEnum.DOUBLE_LIST: 'ser_double_list',
    TypeEnum.STRING_LIST: 'ser_string_list',
    TypeEnum.BOOL_LIST: 'ser_bool_list',
    TypeEnum.TREENODE: 'ser_tree',
    TypeEnum.LISTNODE: 'ser_linked_list',
    TypeEnum.LONG_LIST : 'ser_long_list'
}

TIME_COST_PATH = 'time_cost.txt'

def _py_generate_signature(function_name:str, params_type:List[TypeEnum], params_name:List[str], return_type:TypeEnum) -> str:
    params_list = []
    for p_type, p_name in zip(params_type, params_name):
        p_type_str = py_type[p_type]
        params_list.append(f'{p_name}: {p_type_str}')
    py_signature = f"def {function_name}(self, {', '.join(params_list)}) -> {py_type[return_type]}:"
    return py_signature

def py_generate_solution_code(function_name:str, params_type:List[TypeEnum], params_name:List[str], return_type:TypeEnum):
    lines = [
        'class Solution:',
        f"    {_py_generate_signature(function_name, params_type, params_name, return_type)}",
        '        # write code here',
        f'        return {py_default_val[return_type]}',
    ]
    return "\n".join(lines)

def py_generate_trailer_code(function_name:str, params_type:List[TypeEnum], params_name:List[str], return_type:TypeEnum):
    params_num = len(params_name)
    lines_pre = []
    for i, (p_type, p_name) in enumerate(zip(params_type, params_name)):
            lines_pre += [
                 'json_str = reader.read_line()',
                 'if json_str == None:',
                 '    break' if i == 0 else f'    raise ValueError("Testcase is missing the required argument: `{p_name}`")',
                 f"p{i} = {des_func_name[p_type]}(json_str)"
            ]
    lines = [
        '',
        'def run():',
        '    reader = StdinWrapper()',
        '    writer = StdoutWrapper()',
        '    total_time = 0',
        '    while True:',
        '',
        '\n'.join([' ' * 8 + s for s in lines_pre]),
        '',
        '        start_stamp = time.process_time_ns()',
        f'        result = Solution().{function_name}({", ".join(f"p{x}" for x in range(params_num))})',
        '        end_stamp = time.process_time_ns()',
        '        total_time += end_stamp - start_stamp',
        f'        writer.write_line({ser_func_name[return_type]}(result))',
        f'    with open("{TIME_COST_PATH}", "w") as fp:',
        '        fp.write(f"{total_time // 1000000}")',
        '',
        'if __name__ == "__main__":',
        '    try:',
        '        run()',
        '    except Exception as e:',
        '        exc_type, exc_value, exc_traceback = sys.exc_info()',
        '        sys.stdout = sys.stderr',
        '        traceback.print_tb(exc_traceback)',
        '        traceback.print_exception(exc_type, exc_value, None)',
        '        exit(1)',
    ]
    return "\n".join(lines)


def py_test(function_name:str, params_type:List[TypeEnum], params_name:List[str], return_type:TypeEnum):
    try:
        TMP = 'tmp'
        PATH = 'python3'
        os.makedirs(TMP, exist_ok=True)
        with open(os.path.join(TMP, 'user.in'),'w') as fp:
            for p_type in params_type:
                fp.write(json_default_val[p_type] + '\n')

        solution_code = py_generate_solution_code(function_name, params_type, params_name, return_type)
        trailer_code = py_generate_trailer_code(function_name, params_type, params_name, return_type)

        with open(os.path.join(TMP, 'main.py'), 'w') as fp:
            with open(os.path.join(PATH, 'py_header')) as fq:
                fp.write(fq.read() + '\n' + solution_code + trailer_code)
    
        tmp_list = [filename for filename in os.listdir(PATH) if filename.startswith('py') and filename.endswith('.so')]
        current_dir = os.getcwd()
        if len(tmp_list) == 0:
            print(f"No files matching the condition were found in the {PATH} directory. Running the build command...")
            os.chdir(PATH)
            subprocess.run(['python3', 'setup.py', 'build', '--build-lib', '.'])
            os.chdir(current_dir)
        else:
            print(f"{tmp_list[0]} already exists in the {PATH} directory. No need to run the build command.")

        for filename in os.listdir(PATH):
            if filename.startswith('py') and (filename.endswith('.py') or filename.endswith('.so')):
                src = os.path.join(PATH, filename)
                dst = os.path.join(TMP, filename)
                shutil.copy(src, dst)

    
        os.chdir(TMP)
        result = subprocess.run(['python3', 'main.py'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)

        os.chdir(current_dir)
        if result.returncode != 0:
           return result.returncode, result.stderr

        required_files = ['user.out', 'time_cost.txt']
        files_in_directory = os.listdir(TMP)

        missing_files = [file for file in required_files if file not in files_in_directory]
        if missing_files:
            return 1, f"Missing these files: {', '.join(missing_files)}"
        
        return 0, {'main_body.py' : solution_code, 'main_trailer.py' : trailer_code}
    finally:
        shutil.rmtree(TMP)

if __name__ == '__main__':
    params_type = [TypeEnum.INT, TypeEnum.LONG, TypeEnum.DOUBLE, TypeEnum.STRING, TypeEnum.INT_LIST,
                   TypeEnum.INT_LIST_LIST, TypeEnum.DOUBLE_LIST, TypeEnum.STRING_LIST, TypeEnum.BOOL_LIST,
                   TypeEnum.BOOL, TypeEnum.TREENODE, TypeEnum.LISTNODE]
    params_name = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
    return_type = TypeEnum.INT_LIST_LIST
    print(py_test('solve', params_type, params_name, return_type))