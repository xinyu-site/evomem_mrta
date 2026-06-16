# EMERGE Prompt 模板中文说明

本文档整理 EMERGE 中使用的 prompt 模板。模板按照其在记忆增强多智能体优化流程中的作用进行分组。动态字段使用花括号表示，例如 `{problem_description}`。

## 任务分类

### MRTA 类别选择 Prompt

MRTA 类别选择使用如下 prompt：

```text
你是一个用于 MRTA 任务描述的分类器。
请直接输出以下八个类别之一：

  ST_SR_IA, ST_MR_IA, MT_SR_IA, MT_MR_IA,
  ST_SR_TA, ST_MR_TA, MT_SR_TA, MT_MR_TA

分类规则：
1. ST/MT：
   判断单个机器人是否可以执行多个任务。
   如果可以，输出 MT；否则输出 ST。

2. SR/MR：
   判断是否存在需要多个机器人协作完成的任务。
   如果存在，输出 MR；否则输出 SR。

3. IA/TA：
   判断任务规划是否考虑时间步。
   如果考虑，输出 TA；否则输出 IA。

类别解释（按顺序组合）：
- 第一部分：ST（Single Task）或 MT（Multi-Task）
- 第二部分：SR（Single Robot）或 MR（Multi-Robot）
- 第三部分：IA（Instantaneous Assignment）或 TA（Time-Extended Assignment）

请仔细阅读任务描述，按顺序应用上述三条规则，
并且只输出最终类别名称，不要输出任何额外文本。

任务描述：
{problem_description}
```

## 多智能体求解 Prompt

### Parser Prompt

Parser agent \(P_{\mathrm{Par}}\) 使用如下 prompt：

```text
你是一名专家，擅长从自然语言问题描述中识别
与优化建模相关的信息。

作为 Parser，你的任务是分析问题描述并提取：
  - 相关决策变量，
  - 约束条件，
  - 目标函数。

请运用你的领域知识，确保这些元素被准确定义，
并适合构建一个可求解的 LP 或 MIP 模型。
确保约束只使用 <=、>= 或 = 运算符。
避免使用 > 或 < 这类严格不等式。

{example_context}

请阅读问题描述：
{problem_description}

以及其他专家的评论：
{comments_text}

然后给出提取出的变量、约束和目标函数，
并附上它们的定义。
```

当存在检索到的示例时，`{example_context}` 可由以下两种模板之一实例化：

```text
以下检索到的示例可用于指导你的工作：

{example_str}
```

```text
以下检索到的摘要或失败分析可提供上下文：

{example_str}
```

Parser 阶段使用的示例字符串格式如下：

```text
为了指导你的工作，请仔细学习以下示例。
每个示例展示了从问题描述到结构化抽取的过程。

---
### EXAMPLE {i} ###

Problem Description:
{example_problem}

Example Output:
{example_output}
---
***End of Examples***
```

### Modeler Prompt

Modeler agent \(P_{\mathrm{Mod}}\) 使用如下 prompt：

```text
你是一名运筹优化建模专家，
专长是混合整数规划（MIP）。

你的任务是基于以下信息构建数学优化模型：
  - 问题描述，
  - 其他推理阶段提供的洞察。

请构造决策变量、目标函数和约束条件。
确保模型是完整、可求解的，并符合标准运筹优化原则。

原始问题如下：
{problem_description}

其他推理阶段的评论如下：
{comments_text}

请给出该问题的 MIP 模型。

该模型必须是可求解的 LP 或 MIP 形式。
所有约束只能使用等式、大于等于或小于等于关系。
不要使用严格不等式（> 或 <）；在适当情况下将其替换为
\geq 或 \leq。

你的输出格式应为如下 JSON：
{
  "VARIABLES": "变量的数学描述",
  "CONSTRAINTS": "约束的数学描述",
  "OBJECTIVE": "目标函数的数学描述"
}
```

### Developer Prompt

Developer agent \(P_{\mathrm{Dev}}\) 使用如下 prompt：

```text
你是一名专注于运筹优化的 Python 程序员，
并且熟悉 Gurobi。

你的职责是编写清晰且可执行的求解器代码，
将优化模型转化为可运行的 Python 程序。
实现必须与问题目标和约束保持一致。

作为 Developer，你的核心任务是将以下内容转换为可执行求解器代码：
  - 解析后的任务信息，
  - 数学模型，
  - starter code 模板。

所有约束只能使用 <=、>= 或 =。
在 LP/MIP 公式中禁止使用严格不等式（> 或 <）。

{example_str}

请基于以下问题描述逐步分析：
{problem_description}

以及其他推理阶段的评论：
{comments_text}

使用 starter code 模板：
{code_example}

编写一个严格遵循给定格式的 Python 函数，
并定义一个可求解的 LP 或 MIP 模型。

只包含必要的 import 语句。
不要包含额外测试代码。
请输出清晰、高效且结构良好的代码。
```

当使用检索到的代码示例时，`{example_str}` 实例化如下：

```text
为了指导你的工作，请仔细学习以下示例。
每个示例展示了从问题描述到代码实现的过程。

---
### EXAMPLE {i} ###

Problem Description:
{example_problem}

Example Code Implementation:
{example_code}
---
***End of Examples***
```

## 记忆演化 Prompt

### 抽象记忆演化 Prompt

用于更新抽象记忆 \(m_i^\star\) 的抽象化 prompt \(P_{\mathrm{abs}}\) 如下。
它将当前 episode summary \(s_{ij}\) 与已有类别级 abstract memory 进行融合。

```text
你是一名经验丰富的工作复盘专家。
你擅长总结、比较和迭代式写作。

你的核心能力是比较旧摘要和新摘要，
提取有效模式，保留有用结论，
并将新洞察整合成更加成熟且具有指导性的工作摘要。

你将收到两个输入：

1. 当前 episode summary：
   {current_summary}

2. 原始 abstract memory summary：
   {original_summary}

你的任务：
通过整合当前 episode summary 中的新洞察与经验，
修订并升级原始 abstract memory summary。

输出规则：
1. 只输出最终修订后的摘要文本。不要解释。
2. 保留可复用的类别级建模知识。
3. 整合有用的新模式、注意事项或纠错经验。
```

### 成功 Episode 摘要 Prompt

用于构造成功 episode summary \(s_{ij}\) 的 prompt 如下：

```text
你是一名高效的模型精炼专家。
你擅长将复杂优化模型浓缩为其核心要点。

请阅读以下问题和模型。
简要总结问题描述、优化变量、约束条件、
目标函数和注意事项。
每一项使用 1-3 句话。

原始问题：
{problem_description}

模型文件：
{identify_text}

输出约束：
1. 每一项都应简洁。
2. 在合适的地方使用通用数学术语
   （例如二进制变量、线性约束）。
3. 不要使用数学公式。
4. 不要包含冗余解释。
5. 直接按照以下结构输出摘要：

[Problem Summary]: [Insert summary here]
[Optimization Variables]: [Insert summary here]
[Optimization Constraints]: [Insert summary here]
[Optimization Objective]: [Insert summary here]
[Precautions]: [insert precautions here]
```

### 失败 Episode 诊断 Prompt

用于构造失败 episode diagnosis \(s_{ij}\) 的 prompt 如下：

```text
你是一名高效的模型诊断专家。
你擅长识别优化模型中的核心逻辑错误。

请分析以下原始问题和一个已知错误的模型。
你的任务是直接且简洁地解释为什么这种建模方式是错误的。

原始问题：
{problem_description}

模型文件：
{identify_text}

输出要求：
1. 聚焦根本原因：
   分析建模中的基本逻辑错误或关键假设偏差，
   而不是表层问题或语法问题。
2. 只使用以下结构。
3. 不要包含引言式总结。
4. 每一部分用 1-2 句话解释。

输出结构（严格遵守）：
[Error Cause Analysis]
[Core Error]: [用 1-2 句话指出最根本的错误]
[Specific Analysis]: [解释模型逻辑与问题要求之间的矛盾]
[Potential Consequences]: [说明典型后果，例如无意义解或模型不可行]
```

## Baseline Prompt 模板

### Direct Standard Prompting

Direct standard prompting 使用如下 prompt：

```text
你是一名专注于运筹优化的 Python 程序员。
你在使用 Gurobi 求解器方面具备专业能力。

你将得到一个具体的优化问题。
请开发一个高效的 Python 程序，使用 Gurobi
解决以下问题：

{problem}

请直接给出 Python 代码。
确保解法中只使用 Gurobi 作为求解器。
```

### Chain-of-Thought Baseline

Chain-of-thought baseline 使用如下 prompt：

```text
你是一名专注于运筹优化的 Python 程序员。
你在使用 Gurobi 求解器方面具备专业能力。

你将得到一个具体问题。
你的目标是开发一个高效的 Python 程序来解决该问题。

原始问题如下：
{problem_description}

请逐步分析该问题，然后给出你的 Python 代码。

以下是 starter code：
{code_example}
```

### PHP Baseline

PHP baseline 使用如下 prompt：

```text
你是一名运筹优化领域的 Python 程序员。
你在使用 Gurobi 求解器方面具备专业能力。

你将得到一个具体问题。
你的目标是开发一个高效的 Python 程序来解决该问题。

原始问题如下：
{problem_description}

请逐步分析该问题，然后给出你的 Python 代码。

以下是 starter code：
{code_example}

已有代码如下：
{history_answer}

你需要检查该代码是否正确，并且是否可以直接执行。
```

## Benchmark 与评估细节

### MRTA 类别定义

benchmark 遵循 MRTA 分类中的三个二元维度：机器人能力、任务需求和分配时间性。它们的组合构成实验中使用的八个类别。

| Category | Robot capability | Task requirement | Temporality |
| --- | --- | --- | --- |
| ST/SR/IA | 单任务机器人 | 单机器人任务 | 瞬时分配 |
| ST/SR/TA | 单任务机器人 | 单机器人任务 | 时间扩展分配 |
| ST/MR/IA | 单任务机器人 | 多机器人任务 | 瞬时分配 |
| ST/MR/TA | 单任务机器人 | 多机器人任务 | 时间扩展分配 |
| MT/SR/IA | 多任务机器人 | 单机器人任务 | 瞬时分配 |
| MT/SR/TA | 多任务机器人 | 单机器人任务 | 时间扩展分配 |
| MT/MR/IA | 多任务机器人 | 多机器人任务 | 瞬时分配 |
| MT/MR/TA | 多任务机器人 | 多机器人任务 | 时间扩展分配 |

**单任务（ST）与多任务（MT）机器人。**
在 ST 设置中，每个机器人在相关分配决策中最多被分配给一个任务。在 MT 设置中，一个机器人可以在分配过程中服务多个任务；对于时间扩展场景，仍然需要满足实例中指定的每时间步执行约束。

**单机器人（SR）与多机器人（MR）任务。**
在 SR 设置中，每个任务只需要一个机器人。在 MR 设置中，至少有一个任务需要多个机器人共同执行，因此会引入联盟或同步约束。

**瞬时分配（IA）与时间扩展分配（TA）。**
IA 设置求解不含时间调度的静态分配问题。TA 设置要求分配结果满足任务时间窗和每时间步机器人可用性约束。

### Benchmark 实例结构

每个 benchmark 实例存储为一个问题文件夹，包含三个文件：自然语言描述、starter function 模板和 JSON 测试样例。自然语言描述提供任务语义和分配需求。starter 模板固定所需函数名、输入变量和输出格式。JSON 文件提供可执行测试输入和 evaluator 使用的 ground-truth 输出。

| Field | Meaning |
| --- | --- |
| `RobotPositions` | 机器人的二维坐标 |
| `TaskPositions` | 任务的二维坐标 |
| `NumRobots` | 实例中的机器人数量 |
| `NumTasks` | 实例中的任务数量 |
| `TaskRequirements` | 每个任务所需机器人数量（如适用） |
| `TimeSteps` | 时间扩展设置中的规划时域长度 |
| `EarliestStep` | 每个任务最早可执行时间步 |
| `LatestStep` | 每个任务最晚可执行时间步 |
| `output` | ground-truth 分配结构或最优目标值 |

输出格式取决于类别。一些瞬时分配设置返回显式机器人-任务分配结构，而时间优化设置通常返回最优总欧氏移动距离。所有情况下，成功都要求生成程序遵循 starter function signature，并返回满足类别特定约束的输出。

### 基于执行的成功判据

对于每个 benchmark 实例，模型生成 Python 求解器代码。代码会被提取出来，并使用实例对应的测试样例执行，再由自动 evaluator 检查。只有同时满足以下条件时，一次 trial 才被记为成功：

1. 生成的 Python 程序可以被解析并执行，不产生语法错误或运行时错误。
2. 程序保留 starter 模板中定义的函数名和输入变量。
3. 返回的分配结果或目标值在 evaluator 容差内匹配 ground-truth 输出。
4. 返回结果满足所有 MRTA 约束，包括机器人容量、任务覆盖、多机器人任务需求和时间窗约束（如适用）。

### Ablation 设置

主文中的 ablation study 隔离了各记忆组件的贡献。各变体含义如下：

| Variant | Removed or disabled component |
| --- | --- |
| w/o Mem | 禁用记忆检索和记忆条件 prompt |
| w/o Evo | 禁用任务执行后的抽象记忆演化 |
| w/o Forget | 禁用基于访问频率的记忆保留 |
| w/o Corr | 禁用基于执行反馈的纠错与诊断 |
| Ours | 使用检索、抽象演化、保留和纠错 |

### 错误类型标注

主文中的错误分析根据最早可识别的失败来源对每个失败实例进行分类。类别定义如下：

| Error type | Definition |
| --- | --- |
| Optimization objective | 求解器优化了与任务目标不一致的量 |
| Constraint condition | 求解器遗漏、弱化或错误表述了必需的 MRTA 约束 |
| Syntax | 生成的 Python 代码无法解析或执行 |
| Output format | 求解器计算出看似合理的结果，但返回格式错误 |

当同一个生成解中出现多个错误时，标签按照求解流程中最早的失败来源分配。例如，如果代码可执行但编码了错误的时间窗约束，则该失败计为 constraint-condition error，而不是 output-format error。

## 实现细节

### 记忆条目结构

每个类别特定的 memory buffer 包含一个 abstract memory 和一组有界 instance memories。abstract memory 存储类别层面的建模知识，而每个 instance memory 存储一个具体任务求解 episode：

```text
m_ij = {h_ij, u_ij, z_ij, Pi_ij, c_ij, e_ij, a_ij, s_ij}
```

其中，`u_ij` 是任务描述，`h_ij` 是其文本 embedding，`z_ij` 是解析后的任务表示，`Pi_ij` 是优化模型，`c_ij` 是生成的求解器程序，`e_ij` 是执行反馈，`a_ij` 是返回的分配结果或目标值，`s_ij` 是用于 retention 的访问频率。

### 检索与保留

对于一个新任务，EMERGE 首先预测其 MRTA 类别，然后在对应类别 buffer 内检索。文本 embedding 使用 `all-MiniLM-L6-v2` 计算。Instance memories 根据与新任务 embedding 的余弦相似度排序，检索 top-\(K\) 条目，并与类别级 abstract memory 一起使用。每当一个 instance memory 被检索到，其访问频率会增加。如果 buffer 超过容量 \(N_i\)，则保留访问频率更高的条目。

## 完整复现实验协议

本节列出复现报告实验所需的具体实现选择。provider-specific API key、proxy 地址和私有 endpoint 被有意省略；它们应替换为支持所选 backbone model 的任意 OpenAI-compatible LLM endpoint。

### 软件环境

实现使用 Python 编写，并使用 LangChain 调用 OpenAI-compatible chat models。生成的求解器程序使用 Gurobi 作为优化后端，因此需要可用的 Gurobi 安装和 license。

| Dependency | Version or role |
| --- | --- |
| Python | 推荐 3.10 或更新版本 |
| `gurobipy` | 13.0.0 |
| `langchain` | 0.1.11 |
| `openai` | 2.9.0 |
| `sentence-transformers` | 5.1.2 |
| `transformers` | 4.57.3 |
| `torch` | 2.9.1 |
| `numpy` | 1.26.4 |
| `scipy` | 1.15.3 |
| `scikit-learn` | 1.7.2 |

完整依赖列表由 `requirements.txt` 提供。复现实验前，安装依赖并配置 LLM backend：

```bash
pip install -r requirements.txt
```

### 仓库结构

实验流程使用以下文件和目录：

```text
agents/                    # Parser, Modeler, and Developer prompts
agentic_memory_rb/         # memory storage, retrieval, scoring, and evolution
baseline/                  # Standard, CoT, and PHP baselines
dataset/                   # eight MRTA categories, 25 instances each
scripts/ablation/          # ablation experiment helpers
main.py                    # multi-agent reasoning loop
run_exp.py                 # single-instance experiment entry point
run_exp_batch_insist.py    # full benchmark runner
test_generated_code.py     # execution-based evaluator
utils.py                   # problem loading and code extraction helpers
```

每个问题文件夹结构如下：

```text
dataset/<MRTA_CATEGORY>/prob_k/
  description.txt          # natural-language task description
  code_example.py          # required function signature and starter template
  sample.json              # executable input and ground-truth output
```

### 模型与解码设置

所有 LLM 调用均使用 temperature \(0\)。实验入口中的默认模型名为 `deepseek-ai/DeepSeek-V3`。主文中的跨模型实验使用相同 pipeline，仅替换 LLM backbone。测试的 backbones 包括 DeepSeek-V3、Claude-3.5、Gemini-2.5-Flash、Gemini-2.5-Pro、GPT-4o、DeepSeek-V2.5 和 Qwen2.5-VL。

为了复现，应在实例化 `ChatOpenAI` 的文件中配置 LLM endpoint。科学实验设置与具体 endpoint URL 或 API key 无关，这些是环境相关项，不属于论文 artifact。

### 单实例执行

可以使用 `run_exp.py` 评估单个实例。以下命令在一个实例上运行完整 EMERGE 配置：

```bash
python run_exp.py \
  --dataset ST_SR_TA \
  --problem prob_0 \
  --algorithm coe \
  --model deepseek-ai/DeepSeek-V3 \
  --use true \
  --useab true \
  --record true \
  --evolve true \
  --forget true \
  --check true \
  --max_collaborate_nums 5
```

主要命令行参数如下：

| Argument | Default | Meaning |
| --- | --- | --- |
| `--algorithm` | `coe` | 使用 EMERGE/chain-of-experts 或 baseline |
| `--model` | `deepseek-ai/DeepSeek-V3` | LLM backbone 名称 |
| `--use` | `true` | 启用 instance-level memory retrieval |
| `--useab` | `true` | 启用 abstract memory retrieval |
| `--record` | `true` | 执行后记录新记忆 |
| `--evolve` | `true` | 更新 abstract memory summaries |
| `--forget` | `true` | 启用基于 score 的 memory retention |
| `--check` | `true` | 使用执行反馈进行 memory update |
| `--max_collaborate_nums` | 5 | 最大 reasoning-stage consultation rounds |

### 完整 Benchmark 执行

完整 benchmark 包含 200 个实例：八个 MRTA 类别，每类 25 个实例。类别按 `run_exp_batch_insist.py` 中使用的顺序评估：

```text
MT_MR_TA, MT_SR_TA, ST_SR_IA, MT_MR_IA,
ST_SR_TA, ST_MR_TA, ST_MR_IA, MT_SR_IA
```

完整 benchmark runner 可如下启动：

```bash
python run_exp_batch_insist.py
```

runner 设置 `num_problems_per_dataset=25` 和 `random_order=False`。如果实验子进程失败或超时，它会重新入队该任务；该 retry 行为用于处理基础设施层面的失败。报告的 success rate 仍只由每个 benchmark 实例的 evaluator 结果决定。

### Baseline 执行

论文中报告的 baselines 使用同一个 `run_exp.py` 入口，通过改变 `--algorithm` 来运行。相关名称为：

```text
standard
chain_of_thought  # alias: cot
php
```

例如，standard baseline 可如下运行：

```bash
python run_exp.py \
  --dataset ST_SR_TA \
  --problem prob_0 \
  --algorithm standard \
  --model deepseek-ai/DeepSeek-V3
```

### Ablation 执行

Ablation 脚本位于 `scripts/ablation/`。它们会在临时副本中 patch batch runner，并执行所选配置。仓库中的 helper scripts 当前将每类 `num_problems=10` 作为快速 ablation；设置为 `num_problems=25` 可复现完整 200-instance ablation。

```bash
python scripts/ablation/run_no_memory.py
python scripts/ablation/run_no_evolve.py
python scripts/ablation/run_no_forget.py
python scripts/ablation/run_no_check.py
```

各 ablation 的具体 flag 如下：

| Variant | use | useab | record | evolve | forget | check |
| --- | --- | --- | --- | --- | --- | --- |
| w/o Mem | false | false | false | false | false | false |
| w/o Evo | true | true | true | false | true | true |
| w/o Forget | true | true | true | true | false | true |
| w/o Corr | true | true | true | true | true | false |
| Ours | true | true | true | true | true | true |

### 记忆超参数

记忆系统使用 sentence-transformer encoder `all-MiniLM-L6-v2` 初始化。`run_exp.py` 中使用以下设置：

| Parameter | Value | Description |
| --- | --- | --- |
| Specific-memory retrieval \(K\) | 1 | 同类别中 top similar instance memory |
| Specific-memory tolerance | 0 | 只从 routed category 中检索 |
| Abstract-memory target number | 2 | 检索的 abstract memories 数量 |
| Abstract-memory tolerance | 2 | abstract retrieval 的 category-distance tolerance |
| Abstract memory per category | 1 | 每类初始 abstract-memory 数量 |
| Memory score increment | 2 | 新 accepted note 存储时增加的 score |
| Specific-memory retention size | 5 | 每类最多保留的 specific memories 数量 |

主实验中，运行 `run_exp.py` 时使用 dataset name 作为任务类别。类别选择 prompt 被包含在 appendix 中，是因为代码库实现了该功能，并可用于类别标签不可用的情况；但 benchmark 实验使用实例已知的 dataset category 进行路由。

### 多智能体推理流程

对于 EMERGE，多智能体推理过程包含三个专门阶段：Parser、Modeler 和 Developer。系统最多运行五轮 consultation，生成答案后通过提取 fenced Python code blocks 进行后处理。如果没有找到 code block，则使用原始回答作为代码。执行前还应用一个小的确定性后处理规则，将 `inrange` 替换为 `in range`。

### 自动 Evaluator

Evaluator 将生成文件作为 `generated_code.py` 导入并 reload，然后调用函数名与问题文件夹匹配的函数，例如 `prob_0`。如果文件无法导入或函数无法加载，则结果为 `COMPILE_ERROR`。如果函数在任一测试样例上抛出异常，则结果为 `RUNTIME_ERROR`。否则，返回输出会与 `sample.json` 中的 ground truth 进行比较。

对于标量数值输出，如果满足以下条件，evaluator 接受结果：

```text
|y_hat - y| < 0.1
```

对于非标量或结构化输出，需要完全相等。只有所有测试样例都通过时，问题才被计为 accepted。结果标签包括：`ACCEPT`、`WRONG_ANSWER`、`RUNTIME_ERROR` 和 `COMPILE_ERROR`。
