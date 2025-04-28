import argparse
import subprocess
import json

cmds = []

def create_buildscript(path, ext):
    with open(path) as json_data:
        db = json.load(json_data)

    with open(f"build.{ext}", "w+") as cmd_file:
        for line in db:
            loc = line['directory']
            cmd_file.write(f'cd {loc}\n')
            cmd = line['command']
            cmd_file.write(f'{cmd}\n')
            cmds.append(cmd)

def calculate_coverage(target_src):
    print("== COVERAGE STATISTICS ==")
    print(f"Number of commands: {len(cmds)}")

    cmd = "Get-ChildItem -Recurse -Include *.cpp,*.c | Measure-Object | Select-Object -ExpandProperty Count"
    result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
    file_cnt = int(result.stdout.strip(), 10)
    print(f"Counted {file_cnt} files")
    print(f"Coverage: {(file_cnt/len(cmds)):.2f}")


def createDB(name, buildscript_path):
    # just run the command
    print("Creating database...")
    subprocess.run(['codeql', 'database', 'create', '--language=cpp', f'--command="{buildscript_path}"', name, '--overwrite'])

def main():
    # get args
    parser = argparse.ArgumentParser(
            prog='CompileQL',
            description='Compile and collect metrics on a CodeQL database from a compile_commands.json file'
            )
    parser.add_argument('compile_commands_path')
    parser.add_argument('target_src')
    parser.add_argument('db_name')
    parser.add_argument('ext')
    args = parser.parse_args()

    print(f"Using compile_commands at: {args.compile_commands_path}")

    # run build
    create_buildscript(args.compile_commands_path, args.ext)

    # calculate coverage
    calculate_coverage(args.target_src)

    # generate codeQL db
    createDB(args.db_name, f'build.{args.ext}')

if __name__ == '__main__':
    main()
