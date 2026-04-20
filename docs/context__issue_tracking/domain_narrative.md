# Issue Tracking 领域业务叙事 (Domain Narrative)

## 1. 领域愿景 (Context Vision)

`Issue Tracking` 上下文是系统的“神经末梢”，其愿景是**作为项目与外部利益相关者的核心沟通桥梁，捕捉并管理所有非结构化的反馈、缺陷与需求**。

它在系统中扮演“漏斗”角色，通过规范化的收集、分类与生命周期管理，将零散的用户输入转化为系统可识别、可追溯的领域资产。它不仅提供了问题跟踪的基础 CRUD 能力，更通过与 `Planning` 的松耦合关联，实现了从“发现问题”到“解决问题”的闭环链路。

## 2. 核心业务流程 (Core Workflows)

### A. 提交与初筛 (Capture & Triage)
1.  **提交**：外部用户（Submitter）通过 MCP 工具或 API 提交包含标题、描述、严重程度（Severity）和类型（IssueType）的 Issue。
2.  **初筛**：由 Agent 接收并识别为 `NEW` 状态。此时系统会自动收集上下文信息，并由 Agent 进行初步分类与评估。
*   **业务价值**：建立统一的入口，防止研发团队被低质量、重复的反馈淹没。

### B. 状态流转与互动 (Lifecycle & Collaboration)
1.  **评估分流**：Agent 将评估后的 Issue 推向 `TRIAGED` 状态，并为其添加业务标签（Label）。
2.  **迭代处理**：通过 `Comment` 实体记录用户与 Agent/开发者之间的沟通历史。任何关键的决策和补充信息都作为评论持久化。
3.  **最终闭环**：当关联的 Task 完成或问题被拒绝时，Issue 进入 `RESOLVED` 或 `CLOSED` 终态。

### C. 跨领域关联 (Context Linking)
1.  **建立链路**：Agent 在判定 Issue 具有执行价值时，会调用 `link_issue_to_task`，将 `Issue` 与 `Planning` 上下文中的 `TaskId` 建立关联。
2.  **进度回溯**：通过 `TaskLink` 值对象，系统可以从 Issue 详情中回溯其解决进度，而无需直接依赖 Planning 的内部模型。

## 3. 典型用户故事 (User Stories)

*   **作为终端用户**，我报告一个影响核心流程的 Critical Bug，并希望能够随时查看该 Bug 是否已被开发团队受理并关联到具体的执行计划中。
*   **作为分流 Agent**，我每天会检查所有 `NEW` 状态的 Issue，通过其描述自动识别其 Severity，并为需要修复的 Bug 自动寻找关联的 `project_id`。
*   **作为开发人员**，我需要查看某个具体 Task 关联的所有原始 Issue，以便理解该功能的业务背景和用户的真实痛点。
