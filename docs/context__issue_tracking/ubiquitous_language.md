# Issue Tracking 通用语言与规约 (Ubiquitous Language)

## 1. 核心名词 definition (Domain Terms)

| 术语 | 英文别名 | 业务定义 |
| :--- | :--- | :--- |
| **问题** | Issue | 系统的核心聚合根，代表第三方用户提交的原始反馈（Bug、需求、咨询等）。 |
| **提交者** | Submitter | 提交 Issue 的外部主体，可以是最终用户、测试人员或合作伙伴。 |
| **问题类型** | IssueType | 对 Issue 的功能性分类：`BUG` (缺陷), `FEATURE` (功能需求), `QUESTION` (咨询), `IMPROVEMENT` (改进建议)。 |
| **严重程度** | Severity | 描述问题的紧迫性与破坏性：`CRITICAL`, `MAJOR`, `MINOR`, `LOW`。 |
| **评论** | Comment | 对 Issue 的补充信息或讨论记录，具有时间戳和作者标识。 |
| **标签** | Label | 用于分类、筛选或标记 Issue 的灵活关键字（如 "frontend", "api"）。 |
| **任务链接** | TaskLink | 记录 Issue 与 `Planning` 上下文中的 `Task` 之间关联关系的值对象。 |
| **问题状态** | IssueStatus | Issue 在生命周期中的位置（NEW, TRIAGED, IN_PROGRESS, RESOLVED, CLOSED）。 |

## 2. 实体不变量 (Invariant Rules)

这些规则由 `Issue` 聚合根强制执行，确保数据一致性：

*   **唯一引用约束**：同一 Issue 下的 `TaskLink` 列表严禁包含重复的 `task_id`。
*   **状态准入原则**：只有处于非终态（非 `CLOSED`）的 Issue 才允许添加评论、修改元数据或建立任务关联。
*   **核心元数据不可空**：Issue 在创建时必须包含 `project_id`, `title`, `description`, `type`, `severity` 和 `submitter`。
*   **审计完整性**：所有状态变更必须伴随 `updated_at` 的自动刷新。

## 3. 核心业务规约 (Business Rules)

### 问题分流规约
*   **Given**: 一个处于 `NEW` 状态的 Issue。
*   **When**: Agent 调用 `update_issue_metadata`（分类、定级）或添加评论。
*   **Then**: 系统通常应将状态推进至 `TRIAGED`（已评估），表示该问题已被受理并进入待处理队列。

### 自动闭环规约 (基于集成)
*   **Given**: 一个已关联到具体 Task 的 Issue。
*   **When**: 关联的 Task 在 `Planning` 上下文中变更为 `DONE` 状态。
*   **Then**: 系统通过事件驱动机制，建议或自动将 Issue 状态推进至 `RESOLVED`（已解决），并通知提交者。

### 关联有效性规约
*   **Given**: 一个合法的 `task_id`。
*   **When**: 调用 `link_issue_to_task`。
*   **Then**: `Issue Tracking` 上下文仅存储该 `task_id` 引用，不验证其在 `Planning` 中的实时状态，以实现物理上的完全解耦。

### 状态流转约束
*   **NEW** 只能流转至 **TRIAGED** 或 **CLOSED**。
*   **RESOLVED** 在验证失败后可以回滚至 **IN_PROGRESS**。
*   **CLOSED** 是终态，严禁任何形式的再流转（除非进行特殊的“重新开启”操作）。
