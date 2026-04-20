# Planning 通用语言与规约 (Ubiquitous Language)

## 1. 核心名词定义 (Domain Terms)

| 术语 | 英文别名 | 业务定义 |
| :--- | :--- | :--- |
| **任务** | Task | 规划引擎的原子单元，是 DAG 中的一个节点，承载具体的业务意图、成本预估与价值评分。 |
| **层级范围** | Scope Level | 任务的职责边界，分为 `Project` (战略), `Context` (战术), `Architectural` (架构), `Atomic` (执行)。 |
| **依赖** | Dependency | 任务之间的因果约束关系。前置任务未完成，后续任务处于阻塞状态。 |
| **完成逻辑** | Completion Logic | 决定任务何时解锁的规则：`ALL` (所有依赖完成) 或 `ANY` (任一依赖完成)。 |
| **成本** | Effort | 完成任务所需的预估资源投入，必须遵循斐波那契数列（1, 2, 3, 5, 8, 13...）。 |
| **基础价值** | Base Value | 任务本身对项目的固有贡献度。 |
| **投资回报率** | ROI | 优先级计算指标。`ROI = Base Value / Effort`。分值越高，执行优先级越高。 |
| **拆解中** | Decomposing | 任务的一种特殊状态，表示该设计任务已完成并已通过初步验收，正处于子任务执行阶段。 |
| **产出物** | Output | 任务执行完成后的结果，包含总结（Summary）和具体制品（Artifacts，如文件路径、代码片段）。 |

## 2. 实体不变量 (Invariant Rules)

这些规则在任何时候都必须由 `Task` 聚合根强制执行：

*   **无环依赖 (DAG)**：任务的依赖链条严禁形成闭环。任何试图添加导致循环依赖的操作必须被拒绝。
*   **成本合法性**：`Effort` 必须是有效的斐波那契数，以强制执行估算的模糊性与区分度。
*   **状态单向流转**：
    *   `READY` 状态只能从 `PENDING` 或 `BLOCKED` 转换而来。
    *   只有处于 `READY` 状态的任务才能被 `Claim`（认领）进入 `IN_PROGRESS`。
*   **层级降级约束**：子任务的 `ScopeLevel` 必须低于父任务的层级（如 `Project` 的子任务应为 `Context`）。

## 3. 核心业务规约 (Business Rules)

### 递归拆解规约
*   **Given**: 一个任务处于 `REVIEWING` 状态且已提交设计产出。
*   **When**: 上层负责人（Agent）审批通过且判定需要下钻。
*   **Then**: 任务状态转为 `DECOMPOSING`，并允许创建下一层级的关联子任务。

### 递归验收与闭环规约
*   **Given**: 一个处于 `DECOMPOSING` 状态的任务。
*   **When**: 该任务关联的所有子任务状态均变为 `DONE`。
*   **Then**: 系统向父任务发送“子任务全达成”通知，父任务自动进入最终的可验收状态或直接标记为 `DONE`。

### 优先级动态重排规约
*   **Given**: 存在多个处于 `READY` 状态的任务。
*   **When**: 调用 `suggest_next_action` 工具。
*   **Then**: 系统必须根据 `ROI = Value / Effort` 对任务进行降序排列，并优先返回 ROI 最高的任务。

### 自动解锁规约
*   **Given**: 一个任务 B 依赖于任务 A。
*   **When**: 任务 A 的状态变更为 `DONE` 且满足任务 B 的 `CompletionLogic`。
*   **Then**: 任务 B 的状态必须立即从 `BLOCKED` 自动变更为 `READY`。
