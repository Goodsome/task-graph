# Issue Tracking 技术实现与架构设计 (Technical Design)

## 1. 物理架构 (Physical Architecture)

`Issue Tracking` 上下文严格遵循 DDD 战术分层架构，并作为独立的组件运行：

*   **Domain 层**：包含 `Issue` 聚合根、`Comment` 实体、`TaskLink` 值对象。
*   **Application 层**：定义应用服务用例（如 `CreateIssue`, `LinkIssueToTask`）和 `UnitOfWork` 接口。
*   **Infrastructure 层**：实现 `IssueRepository`（基于 SQLAlchemy），处理复杂的 Issue 及其评论、标签的级联保存。
*   **Interfaces 层**：主要通过 `MCP` 适配器暴露接口，支持 Agent 的自动化操作。

## 2. 核心组件交互 (Core Components)

### 关联链路管理 (Linking Mechanism)
*   **模式**：采用 ID 软关联。`Issue` 聚合根持有一个 `TaskLink` 列表。
*   **解耦实现**：`link_issue_to_task` 用例仅负责在 `Issue` 表中插入关联记录。它并不依赖 `Planning` 的服务。
*   **状态同步**：系统通过 `LocalEventBus` 订阅 `Planning` 上下文发布的 `TaskCompletedEvent`。一旦收到事件，`Issue Tracking` 的订阅者会查找受影响的 Issue，并由 Agent 决定是否将其标记为 `RESOLVED`。

### 级联数据管理
*   **评论与标签**：`Comment` 作为实体受 `Issue` 聚合根管辖。
*   **持久化**：`IssueRepository` 在保存时负责同步更新 `issue_comments` 和 `issue_labels` 关联表，确保整个聚合根的原子性写入。

## 3. 数据持久化方案 (Data Persistence)

*   **存储引擎**：共享项目的 PostgreSQL (或 SQLite)。
*   **ORM 映射**：
    *   **Issue 表**：核心字段包含 `project_id`, `status`, `severity`, `type`。
    *   **TaskLink 表**：一对多/多对多关联表，存储 `issue_id` 到 `task_id` (UUID) 的映射。
    *   **Comment 表**：外键关联到 `Issue`，支持富文本描述。
*   **索引优化**：对 `project_id` 和 `status` 建立复合索引，优化大规模 Issue 列表的查询性能。

## 4. 跨领域集成契约 (Integration Contracts)

### 内部集成 (Inside the System)
*   **事件订阅者**：`PlanningSubscriber` 运行在该上下文的 `Infrastructure` 层，负责监听跨领域的 `Task` 完成事件。
*   **共享内核依赖**：仅依赖 `shared` 模块中定义的基类和 `LocalEventBus` 契约。

### 外部集成 (Outside the System)
*   **MCP 工具集**：
    *   `create_issue`: 提交新反馈。
    *   `list_issues`: 分页查询（强制 project_id 过滤）。
    *   `add_comment`: 在问题上发起互动。
    *   `get_issue_details`: 返回包含完整评论和 Task 关联信息的视图。

## 5. 关键设计约束

1.  **数据隔离**：所有 Repository 操作必须严格限制在 `project_id` 范围内。
2.  **写一致性**：添加评论或修改状态必须通过聚合根方法进行，严禁直接在 Infrastructure 层操作 `CommentModel`。
3.  **弱一致性引用**：`Issue Tracking` 不保证 `TaskLink` 指向的任务一定存在或有效，这一校验职责下放到编排层的 Agent。
