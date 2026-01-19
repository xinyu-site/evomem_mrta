from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
import uuid
import os
import json
import random
import logging
try:
    from .retrievers import PersistentChromaRetriever
except:
    from retrievers import PersistentChromaRetriever
from .llm_controller import Evolver

logger = logging.getLogger(__name__)

def split_k_to_n(k: int, n: int) -> list:
    base = k // n
    remainder = k % n
    result = [base] * n
    for i in range(remainder):
        result[i] += 1
    return result

class MemoryNote:
    """A memory note specifically for storing programming problem solutions and analysis.
    
    This class is designed to encapsulate programming-related memories, including:
    - Original problem description and requirements
    - Problem analysis and solution approach
    - Implementation code
    - Classification and organization metadata
    """
    
    def __init__(self,
                 problem_description: str,
                 problem_analysis: str,
                 code: str,
                 category: Optional[str] = None,
                 index: Optional[str] = None,
                 timestamp: Optional[str] = None,
        ):
       
        # Core memory attributes
        self.problem_description = problem_description
        self.problem_analysis = problem_analysis
        self.code = code
        self.id = str(uuid.uuid4())
        self.index = index or "0"
        self.category = category or "Uncategorized"
        current_time = datetime.now().strftime("%Y%m%d%H%M")
        self.timestamp = timestamp or current_time
        # 记忆分数
        self.score = 0.0
        self.memory_level = 'specific'

    def to_dict(self) -> Dict:
        """Convert the memory note to a dictionary for serialization."""
        return {
            "id": self.id,
            "index": self.index,
            "problem_description": self.problem_description,
            "problem_analysis": self.problem_analysis,
            "code": self.code,
            "category": self.category,
            "timestamp": self.timestamp,
            "score": self.score,
            "memory_level": self.memory_level
        }    

    def save_as_json(self,dir_name:Optional[str]=None) -> bool:
        """Save the memory note as a JSON file in the memory subfolder.
        
        The file will be saved in a 'memory' subfolder relative to the Python file location,
        with the filename being the memory ID.
        """
        # Get the directory of the current Python file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create memory subfolder if it doesn't exist
        if dir_name:
            memory_dir = os.path.join(current_dir, dir_name)
        else:
            memory_dir = os.path.join(current_dir, "memory")
        os.makedirs(memory_dir, exist_ok=True)
        
        # Create filename from ID
        filename = f"{self.id}.json"
        filepath = os.path.join(memory_dir, filename)
        
        # Convert to dictionary and save as JSON
        data = self.to_dict()
        
        try:
            with open(filepath, 'w', encoding='utf-8',errors='ignore') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            #print(f"Memory saved successfully: {filepath}")
            return True
        except Exception as e:
            print(f"Error saving memory: {e}")
            return False

    def delete_as_json(self,dir_complete:str) -> bool:
        try:
            file_path = os.path.join(dir_complete, f"{self.id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                return True

        except Exception as e:
            print(f"Error deleting JSON file for {self.id}: {e}")
            return False
        
    def load_from_json(self, filepath: str) -> bool:
        """Load a memory note from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8',errors="ignore") as f:
                data = json.load(f)
            self.memory_level = data.get("memory_level","null")
            if self.memory_level != 'specific':
                return False
            self.id = data.get("id", "")
            self.index = data.get("index", "0")
            self.problem_description = data.get("problem_description", "null")
            self.problem_analysis = data.get("problem_analysis", "null")
            self.code = data.get("code", "null")
            self.category = data.get("category", "Uncategorized")
            self.timestamp = data.get("timestamp", "")
            self.score = data.get("score", 0.0)

            return True
        except Exception as e:
            print(f"Error loading memory: {e}")
            return False

class AbstructMemoryNote:
    def __init__(self,
                 resolve_summary:str,
                 category:str):
        self.resolve_summary = resolve_summary
        self.id = str(uuid.uuid4())
        self.category = category
        self.memory_level = 'abstruct'
    
    def to_dict(self) -> Dict:
        """Convert the memory note to a dictionary for serialization."""
        return {
            "id": self.id,
            "resolve_summary": self.resolve_summary,
            "category": self.category,
            "memory_level":self.memory_level,
        }    

    def save_as_json(self,dir_name:Optional[str]=None) -> bool:
        """Save the memory note as a JSON file in the memory subfolder.
        
        The file will be saved in a 'memory' subfolder relative to the Python file location,
        with the filename being the memory ID.
        """
        # Get the directory of the current Python file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create memory subfolder if it doesn't exist
        if dir_name:
            memory_dir = os.path.join(current_dir, dir_name)
        else:
            memory_dir = os.path.join(current_dir, "memory")
        os.makedirs(memory_dir, exist_ok=True)
        
        # Create filename from ID
        filename = f"{self.id}.json"
        filepath = os.path.join(memory_dir, filename)
        
        # Convert to dictionary and save as JSON
        data = self.to_dict()
        
        try:
            with open(filepath, 'w', encoding='utf-8',errors='ignore') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            #print(f"Memory saved successfully: {filepath}")
            return True
        except Exception as e:
            print(f"Error saving memory: {e}")
            return False

    def delete_as_json(self,dir_complete:str) -> bool:
        try:
            file_path = os.path.join(dir_complete, f"{self.id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                return True

        except Exception as e:
            print(f"Error deleting JSON file for {self.id}: {e}")
            return False
        
    def load_from_json(self, filepath: str) -> bool:
        """Load a memory note from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8',errors="ignore") as f:
                data = json.load(f)
            self.memory_level = data.get("memory_level","null")
            if self.memory_level != 'abstruct':
                return False
            self.id = data.get("id", "")
            self.resolve_summary = data.get("resolve_summary", "null")
            self.category = data.get("category", "Uncategorized")
            return True
        except Exception as e:
            print(f"Error loading memory: {e}")
            return False

class AgenticMemorySystemRB:
    """A memory system for storing and retrieving programming problem solutions and analyses.
    
    This class provides methods to add, retrieve, and organize programming-related memories.
    """
    
    def __init__(self,dir_memory:Optional[str],model_name:Optional[str]=None,llm_name:Optional[str]=None,category_abstruct_memory_num=1):
        self.memories = {}
        self.abstruct_memories = {}
        self.category_abstruct_memory_num = category_abstruct_memory_num
        self.dir_memory = dir_memory
        
        if model_name:
            self.model_name = model_name
        else:
            self.model_name = "all-MiniLM-L6-v2"

        # create path for memory embedding
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if dir_memory:
            memory_dir = os.path.join(current_dir, dir_memory)
        else:
            memory_dir = os.path.join(current_dir, "memory")
        self.dir_memory_complete = memory_dir

        # 自动拾取先前的记忆json文件
        self.process_memory("memory")

        # 加载ChromaDB持久化存储的记忆，自动拾取先前的记忆
        self.retriever = PersistentChromaRetriever(collection_name="memories",model_name=self.model_name,directory=memory_dir,extend=True)

        # 准备进化器
        if llm_name == None:
            llm_name='deepseek-ai/DeepSeek-V3'            
        self.evolver = Evolver(llm_name)

    def add_note(self, description: str, analysis: str, code: str, category: str, **kwargs) -> str:
        """Add a new memory note"""
        # 增加新的记忆
        note = MemoryNote(problem_description=description,problem_analysis=analysis, code=code,
                          category=category ,**kwargs)
        self.memories[note.id] = note
        self.save_memory_single(note.id,"memory")
        # Convert MemoryNote object to serializable format
        note_json_data = {"description":note.problem_description,"category":note.category}
        ####test####
        #print(note.id)
        self.retriever.add_document(document=description, metadata=note_json_data, doc_id=note.id)
        return note.id
    
    def add_abstruct_note(self, summary: str, category, **kwargs) -> str:
        abstruct_note = AbstructMemoryNote(resolve_summary=summary,category=category)
        self.abstruct_memories[abstruct_note.id] = abstruct_note
        self.save_abstruct_memory_single(abstruct_note.id,"memory")
        return abstruct_note.id

    def delete_note(self, memory_id: str) -> bool:
        """Delete a memory note by its ID.
        
        Args:
            memory_id (str): ID of the memory to delete
            
        Returns:
            bool: True if memory was deleted, False if not found
        """
        # 删除记忆，包括ChromaDB和本地存储

        if memory_id in self.memories:
            # Delete from ChromaDB
            self.retriever.delete_document(memory_id)
            # Delete from local storage
            self.memories[memory_id].delete_as_json(dir_complete=self.dir_memory_complete)
            del self.memories[memory_id]
            self.retriever.delete_document(memory_id)
            return True
        return False
    
    def delete_abstruct_note(self, memory_id: str) -> bool:
        """Delete a memory note by its ID.
        
        Args:
            memory_id (str): ID of the memory to delete
            
        Returns:
            bool: True if memory was deleted, False if not found
        """
        # 删除记忆，包括ChromaDB和本地存储

        if memory_id in self.abstruct_memories:
            # Delete from local storage
            self.abstruct_memories[memory_id].delete_as_json(dir_complete=self.dir_memory_complete)
            del self.abstruct_memories[memory_id]
            return True
        return False
    
    def save_memory(self, dir_name:Optional[str]=None) -> None:
        """Save all memories to JSON files"""
        # 将当前记忆保存，不会保存重复记忆
        for memory in self.memories.values():
            memory.save_as_json(dir_name)

    def save_memory_single(self, memory_id: str , dir_name:Optional[str]=None) -> None:
        self.memories[memory_id].save_as_json(dir_name)

    def save_abstruct_memory_single(self, memory_id: str , dir_name:Optional[str]=None) -> None:
        self.abstruct_memories[memory_id].save_as_json(dir_name)
 
    def process_memory(self,dir_name:Optional[str]=None) -> None:
        # 从当前文件夹的memory子文件夹加载记忆
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if dir_name:
            memory_dir = os.path.join(current_dir, dir_name)
        else:
            memory_dir = os.path.join(current_dir, "memory")
        file_paths = self._list_all_jsonfiles(memory_dir)
        for file_path in file_paths:
            note = MemoryNote(problem_description="null",problem_analysis="null", code="null",
                          category="null")
            abstruct_note = AbstructMemoryNote(resolve_summary='null',
                            category='null')
            if note.load_from_json(file_path):
                self.memories[note.id] = note
            if abstruct_note.load_from_json(file_path):
                self.abstruct_memories[abstruct_note.id] = abstruct_note
        

    def select_memory_bycatogory_distance(self , current_catogory:str , desired_dis : int , k : int) -> List[MemoryNote]:
        """Select a memory by catogory with desired distance"""
        selected_memories = []
        for memory in self.memories.values():
            distance = self._catogory_distance(current_catogory, memory.category)
            if distance == desired_dis:
                selected_memories.append(memory)
        
        #random.shuffle(selected_memories)
        return selected_memories
    
    def select_memory_bycatogory(self , current_catogory:str , k : int , tolerance_level : Optional[int]) -> List[MemoryNote]:
        level = tolerance_level if tolerance_level is not None else 1
        for desired_dis in range(0,level+1):
            selected_memories = self.select_memory_bycatogory_distance(current_catogory, desired_dis, k)
            if len(selected_memories) > 0:
                if len(selected_memories) >= k:
                    return selected_memories[:k]
                else:
                    return selected_memories
                
    def select_memory_bycatogory_content(self , description:str , current_catogory:str , k : int , tolerance_level : Optional[int]) -> List[MemoryNote]:
        level = tolerance_level if tolerance_level is not None else 1
        for desired_dis in range(0,level+1):
            selected_memories = self.select_memory_bycatogory_distance(current_catogory, desired_dis, k)
            if len(selected_memories) > 0:
                if len(selected_memories) >= k:
                    reselect_memories = []
                    categories = {memory.category for memory in selected_memories}
                    category_num = len(categories)
                    assignment_list = split_k_to_n(k,category_num)
                    for i,category_i in enumerate(categories):
                        results = self.retriever.search_bycatogory(description,category_i,assignment_list[i])
                        results = results['ids'][0]
                        #print("----xytest----")
                        #print(results)
                        if len(results) < assignment_list[i]:
                            assignment_list[i+1] += assignment_list[i] - len(results)
                        for id in results:
                            reselect_memories.append(self.memories[id])

                    #selected_memories = sorted(selected_memories, key=lambda memory: self.retriever.search(memory.problem_description, k=1)['distances'][0][0])
                    return reselect_memories
                else:
                    return selected_memories
            else:
                return selected_memories
                
    def scoring_memory_bynewnote(self, new_note_id , addscore_num = Optional[int]):
        description = self.memories[new_note_id].problem_description
        catogory = self.memories[new_note_id].category
        if addscore_num is None:
            addscore_num = 3
        results = self.retriever.search_bycatogory(description,catogory,addscore_num+1)
        for i, doc_id in enumerate(results['ids'][0]):
            print(f'test:{i} id:{doc_id}')
            memory_id = doc_id
            if memory_id != new_note_id:
                if memory_id in self.memories:
                    print(f'test add score {memory_id}')
                    self.memories[memory_id].score += 1.0
                    self.save_memory_single(memory_id,self.dir_memory)
        '''    
        for result in results:
            memory_id = result['id']
            if memory_id != new_note_id:
                if memory_id in self.memories:
                    self.memories[memory_id].score += 1.0 
        '''

    def retrenching_memory_byscore_old(self, target_num : int):
        if len(self.memories) <= target_num:
            return
        # 按分数排序并保留前target_num个记忆
        sorted_memories = sorted(self.memories.items(), key=lambda item: item[1].score, reverse=True)
        top_memories = dict(sorted_memories[:target_num])
        # 删除低分记忆
        low_score_memories = dict(sorted_memories[target_num:])
        for memory_id in low_score_memories.keys():
            self.delete_note(memory_id)
        self.memories = top_memories

    def retrenching_memory_byscore(self, target_num : int):
        catogory_set=set()
        for key in self.memories.keys():
            catogory_set.add(self.memories[key].category)
        memory_dict = {item:[] for item in catogory_set}
        for key in self.memories.keys():
            memory_dict[self.memories[key].category].append(self.memories[key])
        # 按类别分配记忆
        for catogory in memory_dict.keys():
            memories_in_catogory = memory_dict[catogory]
            if len(memories_in_catogory) <= target_num:
                continue
            # 按分数排序并保留前target_num个记忆
            sorted_memories = sorted(memories_in_catogory, key=lambda item: item.score, reverse=True)
            top_memories = sorted_memories[:target_num]
            low_score_memories = sorted_memories[target_num:]
            for memory in low_score_memories:
                self.delete_note(memory.id)
            memory_dict[catogory] = top_memories
        # 重建记忆库
        self.memories = {}
        for catogory in memory_dict.keys():
            for memory in memory_dict[catogory]:
                self.memories[memory.id] = memory
        
    def select_abstruct_memory_bycatogory(self , current_category):
        selected_abstruct_memory=[]
        for memory in self.abstruct_memories.values():
            if memory.category == current_category:
                selected_abstruct_memory.append(memory)
        return selected_abstruct_memory
    
    def select_abstruct_memory_bycatogory_distance(self , current_category , test_shift=False , target_num = 2 , tolerance_level=2):
        selected_abstruct_memory=[]
        # for memory in self.abstruct_memories.values():
        #     if memory.category == current_category:
        #         selected_abstruct_memory.append(memory)
        start_level = 1 if test_shift else 0
        for level in range(start_level,tolerance_level+1):
            for memory in self.abstruct_memories.values():
                if self._catogory_distance(memory.category,current_category)==level:
                    selected_abstruct_memory.append(memory)
            if len(selected_abstruct_memory)>=target_num:
                break
        random.shuffle(selected_abstruct_memory)
        return selected_abstruct_memory
    
    def evolving_abstruct_memory(self, description:str , summary:str , category:str ):
        selected_memory = self.select_abstruct_memory_bycatogory(category)
        if len(selected_memory)==0:
            return
        print('---evolving memory---')
        print(f'evolving {len(selected_memory)} memories!')
        print('---------------------')    
        for memory in selected_memory:
            id=memory.id
            orin_sum = self.abstruct_memories[id].resolve_summary
            renew_sum = self.evolver.forward(description,summary,orin_sum)
            self.abstruct_memories[id].resolve_summary = renew_sum
            self.save_abstruct_memory_single(id,"memory")
        
        return renew_sum


    def _catogory_distance(self,s1:str, s2:str) -> int:
        # 分割字符串
        p1 = s1.split('_')
        p2 = s2.split('_')
        # 确保每段长度正确
        if len(p1) != 3 or len(p2) != 3:
            print("compare string format error")
            return 5
        distance = 0
        # 比较第一段
        if p1[0] != p2[0]:
            distance += 1  # MT vs ST
        # 比较第二段
        if p1[1] != p2[1]:
            distance += 1  # MR vs SR
        # 比较第三段
        if p1[2] != p2[2]:
            distance += 3  # IA vs TA
        return distance
    
    def _list_all_jsonfiles(self,directory):
        """列出指定文件夹及其子文件夹中的所有文件地址"""
        file_paths = []
    
        # 检查目录是否存在
        if not os.path.exists(directory):
            print(f"错误：目录 '{directory}' 不存在")
            return file_paths
    
        # 遍历目录树
        for root, dirs, files in os.walk(directory):
            for file in files:
                # 拼接完整路径
                if file.lower().endswith('.json'):
                    file_path = os.path.join(root, file)
                    file_paths.append(file_path)
    
        return file_paths
    
    
if __name__ == "__main__":
    memory_system = AgenticMemorySystemRB(dir_memory="memory")
       
    example_description1 = '''
        In a two-dimensional environment, there are three robots and three tasks. Each task may require multiple robots, and each robot can perform multiple tasks. The assignment occurs instantaneously, with no future planning. Task 0 requires 2 robots, while Tasks 1 and 2 each require 1 robot. The goal is to assign robots to tasks such that the total Euclidean distance is minimized. Each task must be assigned a specific number of robots, as defined in the task requirements. Robots can be assigned to multiple tasks simultaneously, and there is no restriction on the number of tasks a robot can handle at the same time. The objective is to minimize the sum of Euclidean distances for robots assigned to each task.
    '''

    example_analysis1 = '''
    ### Extracted Variables, Constraints, and Objectives

#### Variables
1. **Defender Positions (D)**: A (10, 2) matrix representing the positions of the 10 Defenders in the XY coordinate system. Each row corresponds to a Defender, and each column corresponds to the X and Y coordinates.
   - \( D = [d_{i,j}] \) where \( i \in \{1, 2, \dots, 10\} \) and \( j \in \{1, 2\} \).

2. **Intruder Positions (I)**: A (10, 2) matrix representing the positions of the 10 Intruders in the XY coordinate system. Each row corresponds to an Intruder, and each column corresponds to the X and Y coordinates.
   - \( I = [i_{k,l}] \) where \( k \in \{1, 2, \dots, 10\} \) and \( l \in \{1, 2\} \).

3. **Pairing Variable (P)**: A binary variable indicating whether Defender \( i \) is paired with Intruder \( k \).
   - \( P_{i,k} \in \{0, 1\} \) for \( i, k \in \{1, 2, \dots, 10\} \).

4. **Euclidean Distance (E)**: The Euclidean distance between Defender \( i \) and Intruder \( k \).
   - \( E_{i,k} = \sqrt{(d_{i,1} - i_{k,1})^2 + (d_{i,2} - i_{k,2})^2} \).

#### Constraints
1. **Pairing Constraint**: Each Defender must be paired with exactly one Intruder.
   - \( \sum_{k=1}^{10} P_{i,k} = 1 \) for \( i \in \{1, 2, \dots, 10\} \).

2. **Pairing Constraint**: Each Intruder must be paired with exactly one Defender.
   - \( \sum_{i=1}^{10} P_{i,k} = 1 \) for \( k \in \{1, 2, \dots, 10\} \).

3. **Non-Negativity Constraint**: The Euclidean distance must be non-negative.
   - \( E_{i,k} \geq 0 \) for \( i, k \in \{1, 2, \dots, 10\} \).

#### Objective
1. **Minimize Total Euclidean Distance**: The objective is to minimize the total Euclidean distance between the paired Defenders and Intruders.
   - \( \text{Minimize} \sum_{i=1}^{10} \sum_{k=1}^{10} P_{i,k} \cdot E_{i,k} \).

### Summary
- **Variables**: \( D, I, P, E \).
- **Constraints**: Pairing constraints for Defenders and Intruders, non-negativity of Euclidean distance.
- **Objective**: Minimize the total Euclidean distance between paired Defenders and Intruders.

These variables, constraints, and objectives are well-defined and suitable for formulating a solvable Linear Programming (LP) or Mixed-Integer Programming (MIP) model.
    '''

    example_code1 = '''
    def prob_0(RobotPositions, TaskPositions, TaskRequirements, NumRobots, NumTasks):
    """ 
    Solves the robot-task assignment problem minimizing total Euclidean distance.
    
    Args:
        RobotPositions: List of lists, Cartesian coordinates of robots [[x1,y1], [x2,y2], ...]
        TaskPositions: List of lists, Cartesian coordinates of tasks [[x1,y1], [x2,y2], ...]
        TaskRequirements: List of integers, number of robots required per task
        NumRobots: Integer, number of robots
        NumTasks: Integer, number of tasks
        
    Returns:
        assignment: List of lists, where each sublist contains robot indices assigned to that task
        
    Raises:
        ValueError: If input dimensions are inconsistent or invalid
        Exception: If no optimal solution is found
    """
    import numpy as np
    from gurobipy import Model, GRB, quicksum

    # Input validation
    if len(RobotPositions) != NumRobots:
        raise ValueError("RobotPositions length must match NumRobots")
    if len(TaskPositions) != NumTasks or len(TaskRequirements) != NumTasks:
        raise ValueError("TaskPositions and TaskRequirements length must match NumTasks")
    if any(req < 0 for req in TaskRequirements):
        raise ValueError("TaskRequirements must be non-negative")
    if any(len(pos) != 2 for pos in RobotPositions + TaskPositions):
        raise ValueError("All positions must be 2D Cartesian coordinates")

    def euclidean_distance(p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    try:
        # Create and configure model
        model = Model("robot_task_assignment")
        model.setParam('OutputFlag', 0)
        
        # Precompute distances
        distances = np.zeros((NumRobots, NumTasks))
        for i in range(NumRobots):
            for j in range(NumTasks):
                distances[i,j] = euclidean_distance(RobotPositions[i], TaskPositions[j])

        # Decision variables
        x = {}
        for i in range(NumRobots):
            for j in range(NumTasks):
                x[i, j] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")

        # Objective: minimize total distance
        model.setObjective(
            quicksum(distances[i,j] * x[i,j] for i in range(NumRobots) for j in range(NumTasks)),
            GRB.MINIMIZE
        )

        # Task requirement constraints
        for j in range(NumTasks):
            model.addConstr(
                quicksum(x[i, j] for i in range(NumRobots)) == TaskRequirements[j],
                name=f"task_{j}_requirement"
            )

        # Solve the model
        model.optimize()

        # Extract solution
        assignment = [[] for _ in range(NumTasks)]
        if model.status == GRB.OPTIMAL:
            for i in range(NumRobots):
                for j in range(NumTasks):
                    if round(x[i, j].X) == 1:
                        assignment[j].append(i)
            return assignment
        else:
            raise Exception(f"No optimal solution found. Model status: {model.status}")
            
    finally:
        model.dispose()
    '''  

    example_description2 = '''
    In a 2D environment with an XY Cartesian coordinate system, there are 3 robots and 3 tasks. The tasks must be assigned to robots over 4 discrete time steps. Each robot can execute multiple tasks simultaneously (MT), but each robot can only handle one task at a time. Some tasks require multiple robots simultaneously (MR), meaning each task must be performed by exactly the number of robots specified in the TaskRequirements. Tasks must be assigned within their respective time windows, which are defined by the EarliestStep and LatestStep for each task.
Key Constraints: 1. Each task must be assigned to the required number of robots within its valid time window (EarliestStep, LatestStep). 2. Each robot can handle only one task at any given time step. 
The goal is to minimize the total Euclidean distance traveled by robots while completing their assigned tasks. Tasks must be completed within a single time step, respecting their earliest and latest allowed start times. The objective is to find the robot-task assignment that minimizes the total travel distance. Before returning the total_distance, rounding can be applied to eliminate floating-point errors.
    '''

    example_analysis2 = '''
    ### Extracted Variables, Constraints, and Objectives

#### Variables
1. **Defender Positions (D)**: A (10, 2) matrix representing the positions of the 10 Defenders in the XY coordinate system. Each row corresponds to a Defender, and each column corresponds to the X and Y coordinates.
   - \( D = [d_{i,j}] \) where \( i \in \{1, 2, \dots, 10\} \) and \( j \in \{1, 2\} \).

2. **Intruder Positions (I)**: A (10, 2) matrix representing the positions of the 10 Intruders in the XY coordinate system. Each row corresponds to an Intruder, and each column corresponds to the X and Y coordinates.
   - \( I = [i_{k,l}] \) where \( k \in \{1, 2, \dots, 10\} \) and \( l \in \{1, 2\} \).

3. **Pairing Variable (P)**: A binary variable indicating whether Defender \( i \) is paired with Intruder \( k \).
   - \( P_{i,k} \in \{0, 1\} \) for \( i, k \in \{1, 2, \dots, 10\} \).

4. **Euclidean Distance (E)**: The Euclidean distance between Defender \( i \) and Intruder \( k \).
   - \( E_{i,k} = \sqrt{(d_{i,1} - i_{k,1})^2 + (d_{i,2} - i_{k,2})^2} \).

#### Constraints
1. **Pairing Constraint**: Each Defender must be paired with exactly one Intruder.
   - \( \sum_{k=1}^{10} P_{i,k} = 1 \) for \( i \in \{1, 2, \dots, 10\} \).

2. **Pairing Constraint**: Each Intruder must be paired with exactly one Defender.
   - \( \sum_{i=1}^{10} P_{i,k} = 1 \) for \( k \in \{1, 2, \dots, 10\} \).

3. **Non-Negativity Constraint**: The Euclidean distance must be non-negative.
   - \( E_{i,k} \geq 0 \) for \( i, k \in \{1, 2, \dots, 10\} \).

#### Objective
1. **Minimize Total Euclidean Distance**: The objective is to minimize the total Euclidean distance between the paired Defenders and Intruders.
   - \( \text{Minimize} \sum_{i=1}^{10} \sum_{k=1}^{10} P_{i,k} \cdot E_{i,k} \).

### Summary
- **Variables**: \( D, I, P, E \).
- **Constraints**: Pairing constraints for Defenders and Intruders, non-negativity of Euclidean distance.
- **Objective**: Minimize the total Euclidean distance between paired Defenders and Intruders.

These variables, constraints, and objectives are well-defined and suitable for formulating a solvable Linear Programming (LP) or Mixed-Integer Programming (MIP) model.

    '''
    
    example_code2 = '''
    def prob_1(RobotPositions, TaskPositions, EarliestStep, LatestStep, NumRobots, NumTasks, TimeSteps, TaskRequirements):
    """
    Args:
        RobotPositions: a list of lists, positions of robots in Cartesian coordinates
        TaskPositions: a list of lists, positions of tasks in Cartesian coordinates
        EarliestStep: a list, earliest time step for each task
        LatestStep: a list, latest time step for each task
        NumRobots: an integer, number of robots
        NumTasks: an integer, number of tasks
        TimeSteps: an integer, number of time steps
        TaskRequirements: list, number of robots required for each task
    Returns:
        total_distance: a float, the minimized sum of Euclidean distances between robots and tasks over all time steps
    """
    import math
    from gurobipy import Model, GRB, quicksum   

    model = Model("MT_MR_TA")

    # Create assignment variables
    x = {}
    for r in range(NumRobots):
        for k in range(NumTasks):
            for t in range(TimeSteps):
                if EarliestStep[k] <= t <= LatestStep[k]:
                    x[r, k, t] = model.addVar(vtype=GRB.BINARY, name=f'x_{r}_{k}_{t}')
                else:
                    x[r, k, t] = model.addVar(vtype=GRB.BINARY, ub=0, name=f'x_{r}_{k}_{t}')

    # Create position variables
    pos_x = {}
    pos_y = {}
    for r in range(NumRobots):
        for t in range(TimeSteps + 1):
            pos_x[r, t] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f'pos_x_{r}_{t}')
            pos_y[r, t] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f'pos_y_{r}_{t}')

    # Initial positions
    for r in range(NumRobots):
        model.addConstr(pos_x[r, 0] == RobotPositions[r][0], name=f'init_pos_x_{r}')
        model.addConstr(pos_y[r, 0] == RobotPositions[r][1], name=f'init_pos_y_{r}')

    # Position updates based on assignments
    for r in range(NumRobots):
        for t in range(TimeSteps):
            assigned = model.addVar(vtype=GRB.BINARY, name=f'assigned_{r}_{t}')
            model.addConstr(assigned == quicksum(x[r, k, t] for k in range(NumTasks)), name=f'assigned_constr_{r}_{t}')

            for k in range(NumTasks):
                model.addGenConstrIndicator(
                    x[r, k, t],
                    True,
                    pos_x[r, t+1] == TaskPositions[k][0],
                    name=f'pos_x_update_{r}_{k}_{t}'
                )
                model.addGenConstrIndicator(
                    x[r, k, t],
                    True,
                    pos_y[r, t+1] == TaskPositions[k][1],
                    name=f'pos_y_update_{r}_{k}_{t}'
                )

            model.addGenConstrIndicator(
                assigned,
                False,
                pos_x[r, t+1] == pos_x[r, t],
                name=f'pos_x_stay_{r}_{t}'
            )
            model.addGenConstrIndicator(
                assigned,
                False,
                pos_y[r, t+1] == pos_y[r, t],
                name=f'pos_y_stay_{r}_{t}'
            )

    # 引入新变量y[k,t]表示任务k在时间t执行
    y = {}
    for k in range(NumTasks):
        for t in range(EarliestStep[k], LatestStep[k] + 1):
            y[k, t] = model.addVar(vtype=GRB.BINARY, name=f'y_{k}_{t}')

    # 每个任务必须在一个时间步执行
    for k in range(NumTasks):
        model.addConstr(
            quicksum(y[k, t] for t in range(EarliestStep[k], LatestStep[k] + 1)) == 1,
            name=f'task_{k}_exact_time'
        )

    # 约束任务在选中的时间步分配正确数量的机器人
    for k in range(NumTasks):
        for t in range(EarliestStep[k], LatestStep[k] + 1):
            # 如果y[k,t]=1，则分配TaskRequirements[k]个机器人
            model.addGenConstrIndicator(
                y[k, t],
                True,
                quicksum(x[r, k, t] for r in range(NumRobots)) == TaskRequirements[k],
                name=f'task_{k}_t_{t}_req'
            )
            # 如果y[k,t]=0，则分配0个机器人
            model.addGenConstrIndicator(
                y[k, t],
                False,
                quicksum(x[r, k, t] for r in range(NumRobots)) == 0,
                name=f'task_{k}_t_{t}_no_req'
            )

    # 每个机器人每时间步最多分配到一个任务
    for r in range(NumRobots):
        for t in range(TimeSteps):
            model.addConstr(
                quicksum(x[r, k, t] for k in range(NumTasks)) <= 1,
                name=f'robot_{r}_time_{t}_max_one'
            )

    # 定义位移变量
    delta_x = {}
    delta_y = {}
    for r in range(NumRobots):
        for t in range(TimeSteps):
            delta_x[r, t] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f'delta_x_{r}_{t}')
            delta_y[r, t] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f'delta_y_{r}_{t}')
            model.addConstr(delta_x[r, t] == pos_x[r, t+1] - pos_x[r, t], name=f'delta_x_constr_{r}_{t}')
            model.addConstr(delta_y[r, t] == pos_y[r, t+1] - pos_y[r, t], name=f'delta_y_constr_{r}_{t}')

    # 计算总距离
    total_distance = 0
    for r in range(NumRobots):
        for t in range(TimeSteps):
            dist = model.addVar(name=f'dist_{r}_{t}')
            model.addGenConstrNorm(dist, [delta_x[r, t], delta_y[r, t]], 2, name=f'dist_norm_{r}_{t}')
            total_distance += dist

    model.setObjective(total_distance, GRB.MINIMIZE)
    model.Params.NonConvex = 2
    model.Params.LogToConsole = 0

    model.optimize()

    #total_distance = 0
    
    return total_distance
    '''
    
    id1 = memory_system.add_note(description=example_description1,
                                        analysis=example_analysis1,
                                        code=example_code1,
                                        catogory="MT_MR_IA")
    
    id2 = memory_system.add_note(description=example_description2,
                                        analysis=example_analysis2,
                                        code=example_code2,
                                        catogory="MT_MR_TA")
    
    #memory_system.save_memory(dir_name="memory")
    
    #memory_system.delete_note(memory_id=id2)

    #memory_system.process_memory(dir_name="memory")

    #memory_system.save_memory(dir_name="memory")

    print(len(memory_system.memories))

    # selected_memories = memory_system.select_memory_bycatogory(current_catogory="MT_MR_TA", k=2, tolerance_level=2)
    # for dist, memory in selected_memories:
    #     print(f"Distance: {dist}")
    #     print(f"ID: {memory.id}")
    memory_system.scoring_memory_bynewnote(new_note_id=id1, addscore_num=1)
    memory_system.retrenching_memory_byscore(target_num=5)
    for mem_id, mem in memory_system.memories.items():
        print(f"Memory ID: {mem_id}, Score: {mem.score}")

