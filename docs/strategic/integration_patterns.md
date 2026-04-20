# 全局集成与通信模式 (Integration Patterns)

## 1. 内部集成：同进程限界上下文协作

对于运行在同一进程（TaskGraph 核心服务）内的限界上下文（如 `Planning` 与 `Issue Tracking`），集成必须遵循以下契约：

### 异步事件驱动 (Local Event Bus)
*   **模式**：**发布-订阅 (Publish-Subscribe)**
*   **技术细节**：使用 `shared.infrastructure.event_bus.LocalEventBus` 进行解耦通信。
*   **约束**：
    *   **最终一致性**：领域操作（如 `IssueLinkedToTask`）在主事务提交后发布事件。
    *   **单向通信**：严禁在订阅者中发起反向同步调用，避免循环依赖与锁冲突。

### 事务边界隔离 (Unit of Work)
*   **模式**：**工作单元 (Unit of Work)**
*   **技术细节**：每个限界上下文拥有独立的 `UnitOfWork` 实现与数据库会话。
*   **约束**：
    *   跨上下文的操作**严禁**放在同一个本地数据库事务中。
    *   所有持久化操作必须通过该领域的 `Repository` 进行。

### 共享内核 (Shared Kernel)
*   **约束**：仅允许通过 `shared` 模块共享领域驱动设计的基础设施组件（如基类、异常定义、通用配置）。**禁止**在 `shared` 中定义任何具有业务逻辑的实体。

## 2. 外部集成：面向 Agent 与三方系统

系统作为 MCP (Model Context Protocol) 服务运行，外部集成主要由 **AI Agent** 驱动，并辅以事件输出。

### 工具驱动模式 (Agent-Driven via MCP)
*   **模式**：**主动适配器 (Proactive Adapter)**
*   **技术细节**：通过 `entrypoints.mcp` 暴露符合 MCP 标准的工具集。
*   **约束**：
    *   **业务逻辑闭环**：外部 Agent 通过调用 `create_issue` 或 `link_issue_to_task` 等原子工具来编排跨领域的业务流。
    *   **数据隔离**：所有 MCP 调用必须明确携带 `project_id` 以保证多租户/多项目的逻辑隔离。

### 状态变更发布 (External Event Publishing)
*   **模式**：**事件通知 (Event Notification)**
*   **技术细节**：系统捕获内部领域事件（如 `TaskDone`），并将其转化为外部可感知的通知。
*   **约束**：
    *   **负载最小化**：外部事件仅包含核心标识符（如 `issue_id`, `task_id`）和状态标记，不发送完整的实体镜像。接收方需回查 API 获取详情。

## 3. 全局技术底座契约

| 交互场景 | 推荐模式 | 技术底座 | 约束条件 |
| :--- | :--- | :--- | :--- |
| **跨领域逻辑联动** | 异步事件 | `LocalEventBus` | 必须支持幂等性处理 |
| **外部 Agent 指令** | 同步调用 | `MCP Tools` | 必须验证 `project_id` 权限 |
| **跨领域数据关联** | ID 引用 | `TaskId` (Value Object) | 物理上 Separate Ways，逻辑上 ID 关联 |
| **领域对象映射** | DTO 转化 | `Pydantic 2.0` | 严禁将领域实体直接暴露给外部层 |

