# EMERGE Agent Implementation Summary

This note summarizes the implementation of the multi-agent reasoning module in EMERGE from the perspective of the paper. EMERGE decomposes MRTA solving into three specialized reasoning agents: `Parser`, `Modeler`, and `Developer`. The code also contains some additional utility agents, but they are not part of the three-agent reasoning process described in the paper and are therefore omitted here.

## Overall Implementation

The multi-agent solver is implemented in `main.py` through the `chain_of_agents()` function. Given a new MRTA problem, the system initializes the three reasoning agents, lets them produce intermediate reasoning outputs, stores these outputs as comments, and finally synthesizes an executable solver program.

The implementation follows this information flow:

```text
Natural-language MRTA task description
-> Parser extracts structured task representation
-> Modeler builds an optimization formulation
-> Developer generates executable solver code
-> Solver execution returns allocation result and feedback
```

This matches the paper formulation:

```text
u_new -> z -> Pi -> c -> (a, e)
```

where `u_new` is the new task description, `z` is the structured task representation, `Pi` is the instantiated optimization problem, `c` is the generated solver program, and `(a, e)` are the allocation result and execution feedback.

## Shared Agent Structure

All reasoning agents are implemented as prompt-driven LLM agents. They share the same base implementation in `agents/base_agent.py`.

Each agent is built from four main components:

```text
ROLE_DESCRIPTION
+ FORWARD_TASK
+ LangChain PromptTemplate
+ LangChain LLMChain
```

The shared implementation creates an LLM interface and wraps the agent prompt into an `LLMChain`:

```python
self.llm = ChatOpenAI(
    model_name=model,
    temperature=0,
    base_url="https://api.siliconflow.cn/v1",
    api_key="..."
)

self.forward_prompt_template = self.ROLE_DESCRIPTION + "\n" + self.FORWARD_TASK
self.forward_chain = LLMChain(
    llm=self.llm,
    prompt=PromptTemplate.from_template(self.forward_prompt_template)
)
```

Thus, the agents do not correspond to separately trained neural models. They are instantiated using the same LLM backbone, but each agent receives a different role-specific prompt and therefore performs a different reasoning function.

## LangChain, LLMChain, and forward()

`LangChain` is used as the LLM application framework. In this codebase, it mainly provides `PromptTemplate` and `LLMChain`.

`PromptTemplate` defines a prompt with placeholders, such as:

```text
{problem_description}
{comments_text}
{code_example}
```

At runtime, these placeholders are filled with the current problem description, previous agent outputs, retrieved memory examples, or starter code.

`LLMChain` connects the prompt template with the LLM. It can be understood as:

```text
input variables
-> fill the prompt template
-> call the LLM
-> return the generated text
```

For example, an agent calls:

```python
output = self.forward_chain.predict(
    problem_description=problem["description"],
    comments_text=comments_text
)
```

The `forward()` method is the execution interface defined by each agent class. It prepares the required prompt inputs, retrieves previous reasoning outputs from the shared comment pool, calls `self.forward_chain.predict(...)`, and returns the current agent output.

## Parser Agent

The first reasoning agent is the `Parser`. In the current codebase, this paper-level agent is implemented by the `Identifier` class in `agents/Identifier.py`.

The Parser is responsible for task parsing and schema induction. It maps the natural-language MRTA task description to a structured representation containing the optimization-relevant elements needed by later stages.

Its implementation role description is:

```text
You are an expert in identifying and extracting key decision variables from the problem description to support accurate modeling.
As a Parser agent, your task is to analyze the problem description and extract relevant variables, constraints, and objectives.
Use your domain expertise to ensure these elements are accurately defined and suitable for formulating a solvable LP or MIP model.
Specifically, ensure constraints use only <=, >=, or = operators (avoid > or <).
```

Its forward task is:

```text
Review the problem description
{problem_description}
and the comments from other experts
{comments_text}
then provide the extracted variables, constraints, and objectives along with their definitions.
```

Conceptually, this agent produces the structured representation `z` in the paper. It identifies entities such as robots and tasks, extracts decision-relevant variables, and summarizes the constraints and objective implied by the problem.

When memory is available, retrieved examples or summaries are inserted into the Parser prompt. This makes the parsing stage memory-conditioned, as described in the paper.

## Modeler Agent

The `Modeler` agent is implemented in `agents/Modeler.py`.

The Modeler transforms the structured representation produced by the Parser into a concrete mathematical optimization problem. It determines the decision variables, objective function, and constraints, and expresses them as a solvable LP or MIP formulation.

Its implementation role description is:

```text
You are a modeling expert in Operations Research and Optimization, specializing in Mixed-Integer Programming (MIP).
Your task is to construct a mathematical optimization model based on the problem description and insights provided by other agents.
Leverage your expertise to formulate the optimization objectives and constraints, ensuring the model is comprehensive and suitable for solving the given production challenge.
Please integrate all inputs and provide a well-defined model that aligns with operational research principles.
```

Its forward task is:

```text
Now the origin problem is as follow:
{problem_description}

And the comments from other agents are as follow:
{comments_text}

Give your MIP model of this problem. Additionally, please note that your model needs to be a solvable linear programming model or a mixed-integer programming model. This also means that the expressions of the constraint conditions can only be equal to, greater than or equal to, or less than or equal to (> or < are not allowed to appear and should be replaced to be \geq or \leq).

Your output format should be a JSON like this:
{
    "VARIABLES": "A mathematical description about variables",
    "CONSTRAINS": "A mathematical description about constrains",
    "OBJECTIVE": "A mathematical description about objective"
}
```

Conceptually, this agent produces the optimization problem `Pi` in the paper. It converts the parsed task information into formal modeling components that can later be implemented by the Developer.

The implementation also performs a simple post-processing step to replace strict inequalities with non-strict ones:

```python
output = output.replace(" < ", " \\leq ").replace(" > ", " \\geq ")
```

## Developer Agent

The `Developer` agent is implemented in `agents/Developer.py`.

The Developer translates the formal MRTA optimization problem into executable solver code. In the current implementation, it generates Python code using Gurobi as the optimization backend.

Its implementation role description is:

```text
You are a Python programmer specializing in operations research and optimization, with expertise in implementing and solving mathematical problems using Gurobi.
Your main responsibility is to write, debug, and optimize code that transforms given optimization formulations into executable solutions using Gurobi.
Ensure your implementation aligns with the problem objectives and constraints, and deliver clean, efficient, and well-documented code.
While Gurobi is your primary tool, knowledge of related libraries such as NumPy, SciPy, or PuLP can support additional functionality or preprocessing tasks.
Your goal is to provide robust, solver-ready code that effectively addresses the optimization problem.
```

Its forward task is:

```text
Analyze the problem step by step based on the provided description
{problem_description}
and the comments from other agents
{comments_text}.

Using the starter code template {code_example} write a Python function that strictly follows the given format and defines a solvable linear programming (LP) or mixed-integer programming (MIP) model.

Include only the necessary import statements and ensure no external test code is provided.
Deliver clean, efficient, and well-structured code that aligns with the problem requirements.
```

Conceptually, this agent produces the solver program `c` in the paper. It uses the original problem description, the previous agent outputs, the starter code template, and optionally retrieved implementation examples from memory.

## Comment-Based Collaboration

The agents communicate through `CommentPool`, implemented in `comment_pool.py`. Each agent output is stored as a textual comment and becomes available to later agents.

The current comments are retrieved through:

```python
comments_text = comment_pool.get_current_comment_text()
```

This implements an indirect collaboration mechanism: agents do not call each other directly, but each stage can condition its reasoning on the accumulated outputs of previous stages.

## Memory-Conditioned Reasoning

The implementation supports memory-conditioned prompts. When retrieved memory notes are available, they are inserted into the prompts of the Parser and Developer.

For the Parser, memory can provide previous task descriptions, analyses, or abstract summaries. This helps the agent infer the correct task schema and modeling structure.

For the Developer, memory can provide previous problem descriptions and successful code implementations. This helps the agent reuse solver templates and coding patterns.

This corresponds to the paper's memory-conditioned collaborative reasoning process, where the retrieved memory context `M_ret` guides the three reasoning agents.

## Summary

From the paper perspective, the implementation can be summarized as:

```text
Shared LLM backbone
+ role-specific prompts
+ Parser for task parsing
+ Modeler for mathematical formulation
+ Developer for solver synthesis
+ comment-based intermediate reasoning
+ memory-conditioned prompt augmentation
= EMERGE multi-agent reasoning module
```

The key design idea is that the three reasoning agents are instantiated from the same LLM backbone but specialized through prompts. The Parser extracts optimization-relevant task structure, the Modeler formulates the MRTA problem as an LP/MIP model, and the Developer generates executable solver code.
