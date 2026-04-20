# Planning 技术实现与架构设计 (Technical Design)

## 1. 物理架构 (Physical Architecture)

`Planning` 上下文遵循典型的 DDD 战术分层架构，并确保逻辑上的高度自治：

*   **Domain 层**：包含 `Task` 聚合根、领域事件 (`BaseTaskEvent`)、值对象 (`StoryPoint`, `ValueScore`, `ScopeContext`, `AcceptanceCriterion`) 及领域服务。
*   **Application 层**：通过 `Use Cases` 实现业务逻辑编排，定义 `UnitOfWork` 接口用于管理事务边界。
*   **Infrastructure 层**：实现 `TaskRepository` (基于 SQLAlchemy) 和数据持久化细节。
*   **Interfaces 层**：通过 `MCP` 和 `CLI` 适配器暴露能力。

## 2. 核心组件交互 (Core Components)

### 状态流转引擎
*   **机制**：当 `Task` 状态发生变更或被创建时，聚合根内部会记录领域事件（如 `TaskReadyEvent`）。
*   **协调**：`Application` 层在 `UnitOfWork` 提交后，通过 `LocalEventBus` 发布这些事件。
*   **响应**：订阅者（如 `DependencyResolutionService`）接收事件，重新评估下游依赖任务的状态，并触发连锁更新。

### 递归拆解与验收实现
*   **拆解触发**：`ReviewTask` 用例在收到 `approved=True` 且 `requires_decomposition=True` 时，调用领域模型将状态推向 `DECOMPOSING`。
*   **父子关联**：子任务通过 `parent_id` 属性引用父任务。
*   **自动闭环**：`UpdateTaskStatus` 用例在任务变为 `DONE` 时，会检查其父任务（如果存在）。若父任务的所有子任务均已 `DONE`，则自动推进父任务的进度或发送验收通知。

## 3. 数据持久化方案 (Data Persistence)

*   **存储引擎**：默认使用 PostgreSQL。
*   **ORM 映射**：使用 SQLAlchemy 2.0 声明式映射。
    *   **Task 表**：存储核心属性、`project_id` 及 `status`。
    *   **Dependency 关联表**：多对多关系，存储任务间的 DAG 依赖。
    *   **JSONB 字段**：用于存储半结构化数据，所有字段均支持 PostgreSQL GIN 索引扩展：
        *   `output`：任务产出物（总结 + 制品路径列表）
        *   `review_feedback`：人工或 Agent 的审核反馈（决策 + 评注）
        *   `acceptance_criteria`：BDD 验收标准列表（`Given/When/Then` 三段式 + 测试类型）
        *   `scope_context`：有界上下文与架构层归属信息

## 4. 跨领域集成契约 (Integration Contracts)

### 内部集成 (Inside the System)
*   **事件发布**：`Planning` 上下文发布 `TaskCompletedEvent` 到全局 `LocalEventBus`。
*   **事件订阅**：`Issue Tracking` 订阅此事件，用于自动更新关联 Issue 的状态（如果配置了联动规则）。

### 外部集成 (Outside the System)
*   **MCP 工具集**：
    *   `create_task`: 创建并初始化任务。
    *   `suggest_next_action`: 执行 ROI 排序算法。
    *   `submit_task_result`: 接收 Agent 产出的 Artifacts。
*   **数据隔离**：所有查询和修改必须通过 `project_id` 过滤器，由 `TaskRepository` 强制执行。

## 5. 关键设计约束

1.  **并发控制**：在 `claim_task` 操作中，必须使用数据库行级锁（`SELECT ... FOR UPDATE`），防止多个 Agent 同时认领同一个 `READY` 任务。
2.  **幂等性**：事件订阅逻辑必须是幂等的，确保在重试机制下不会导致任务重复解锁。
3.  **循环检测**：在 `modify_task_dependencies` 用例中，在保存前必须调用 `CycleDetectionService` 遍历全图，确保 DAG 的合法性。
4.  **验收标准结构化约束**：`AcceptanceCriterion` 是强类型值对象，`test_type` 使用 `Literal` 类型而非自由字符串，Pydantic 在应用层入口处强制校验，非法值不会触达持久化层。
