from memory_system_rb import MemoryNote,AgenticMemorySystemRB
from pathlib import Path

if __name__ == "__main__":
    memory_system = AgenticMemorySystemRB("memory")
    example_memory_dir = Path("example_memory")
    analysis_list = []
    description_list = []
    code_list = []
    catogory_list = []

    if example_memory_dir.exists():
        for type_folder in example_memory_dir.iterdir():
            if type_folder.is_dir():
                type_name = type_folder.name
                print(f"Type: {type_name}")
                
                for file_path in sorted(type_folder.glob("prob_*_analysis.txt")):
                    if file_path.is_file():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            print(f"  File: {file_path.name}")
                            analysis_list.append(content)
                            catogory_list.append(type_name)
                            #print(f"  Content: {content[:100]}...")  # Preview first 100 chars
                        except Exception as e:
                            print(f"  Error reading {file_path.name}: {e}")
                
                for file_path in sorted(type_folder.glob("prob_*_description.txt")):
                    if file_path.is_file():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            print(f"  File: {file_path.name}")
                            description_list.append(content)
                            catogory_list.append(type_name)
                            #print(f"  Content: {content[:100]}...")  # Preview first 100 chars
                        except Exception as e:
                            print(f"  Error reading {file_path.name}: {e}")

                for file_path in sorted(type_folder.glob("prob_*_*.py")):
                    if file_path.is_file():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            print(f"  File: {file_path.name}")
                            code_list.append(content)
                            #print(f"  Content: {content[:100]}...")  # Preview first 100 chars
                        except Exception as e:
                            print(f"  Error reading {file_path.name}: {e}")
        num= len(analysis_list)
        for i in range(num):
            memory_system.add_note(description=description_list[i],
                                   analysis=analysis_list[i],
                                   code=code_list[i],
                                   catogory=catogory_list[i])