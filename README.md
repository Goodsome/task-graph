# TaskGraph

TaskGraph 是一个基于有向无环图（DAG）的复杂任务流管理与编排引擎。本项目严格遵循领域驱动设计（DDD）与洋葱架构（Onion Architecture）原则，旨在解决高复杂度项目规划中的任务依赖、动态优先级调度以及上下文边界隔离问题。

## 🏛️ 架构概览

系统按限界上下文（Bounded Contexts）进行模块化拆分，核心规划逻辑收敛于 `Planning` 上下文，并通过共享内核（`Shared`）维持跨域的通用模型。

整体结构遵循经典的 DDD 四层分层架构：

* **Domain (领域层)**: 封装核心业务逻辑，包含聚合根、值对象、领域枚举与领域服务。不依赖任何外部框架。
* **Application (应用层)**: 编排领域对象，通过命令（Command）和查询（Query）分离（CQRS 模式）的用例（Use Cases）对外提供服务。
* **Infrastructure (基础设施层)**: 提供持久化适配器（YAML/SQLAlchemy）及其他技术实现，实现依赖倒置。

## 🧩 核心领域模型 (Planning Context)

### 聚合根 (Aggregate Root)

* **`Task`**: 规划的原子单元，作为 DAG 中的节点。管理自身的状态机（Pending -> In Progress -> Review -> Done 等）、依赖关系（Dependencies/Dependents）、业务价值（ValueScore）、工作量（StoryPoint）以及交付物规则。

### 关键值对象 (Value Objects)

* **`StoryPoint`**: 封装了斐波那契数列规则的工作量评估，确保规划粒度的标准化。
* **`ValueScore`**: 业务价值的量化表示，用于后续的动态优先级（ROI）计算。
* **`RecurrencePolicy`**: 定义任务的循环规则（如按 Cron 表达式、成功/失败后触发），支持自动生成后续任务。
* **`TaskOutput` & `ReviewFeedback**`: 规范了执行者交付物与规划者验收意见的数据结构。

### 领域服务 (Domain Services)

为了保证聚合内部的一致性并处理跨任务的复杂校验，系统引入了以下核心服务：

* **`CycleDetectionService`**: 环路检测服务。在建立新的任务依赖时，利用图算法阻断循环依赖，确保任务规划图始终是严格的 DAG。
* **`DependencyResolutionService`**: 依赖解析服务。根据 `CompletionLogic`（ALL/ANY 等级）动态评估前置任务的完成情况，自动解锁下游任务的阻塞状态。
* **`PriorityAnalysisService`**: 优先级分析服务。基于任务树的拓扑结构、业务价值（ValueScore）和所需精力（StoryPoint）动态计算并推荐高 ROI 任务。

## ⚡ 应用层用例 (Use Cases)

系统通过标准化的 Command/Query 接口进行交互：

**任务生命周期管理 (Commands):**

* `CreateTask`: 声明新任务并配置依赖与验收逻辑。
* `ModifyTaskDependencies`: 动态调整 DAG 拓扑（受环路检测保护）。
* `UpdateTaskStatus` / `ReviseTaskDetails`: 状态流转与核心信息修正。
* `ClaimTask` / `SubmitTaskResult`: 任务认领与执行结果交付。
* `ReviewTask`: 验收流程，支持驳回重做或通过并触发下游状态更新。

**调度与查询 (Queries):**

* `SuggestNextAction`: 结合领域层的优先级计算，推荐当前最值得执行的 Actionable Tasks。
* `GetTaskDetails` / `ListTasks`: 多维度（项目、状态、规划层级）的任务检索。

## 🔌 基础设施与持久化

领域层通过 `TaskRepository` 端口定义存储契约，目前提供两种适配器实现：

1. **`YamlTaskRepository`**: 基于本地 YAML 文件的轻量级存储（如 `plan.yaml`），适合个人 CLI 环境与开发调试。
2. **`SqlAlchemyTaskRepository`**: 基于关系型数据库的生产级存储实现。

## 🚀 快速开始

本项目依赖 `uv` 作为包与环境管理工具。使用以下命令快速拉起开发环境：

```bash
# 同步依赖并创建虚拟环境
uv sync

# 运行测试以验证领域逻辑与 DAG 约束
uv run pytest

```
