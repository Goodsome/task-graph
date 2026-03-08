import asyncio
import json
import psycopg
from datetime import datetime

from task_graph.planning.config import get_settings

async def event_handler(payload: str, channel_name: str):
    """处理接收到的事件数据"""
    try:
        data = json.loads(payload)
        event_type = data.get("event_type", "UnknownEvent")
        occurred_at = data.get("occurred_at", "UnknownTime")
        
        print(f"\n{"="*40}")
        print(f"🔔 收到事件: {event_type}")
        print(f"⏰ 发生时间: {occurred_at}")
        print(f"📦 完整载荷: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print(f"{"="*40}")
        
        # 这里未来可以根据 event_type 路由到不同的处理逻辑
        if event_type == "TaskReadyEvent":
            print(f"🚀 动作: 准备拉起任务 {data.get('task_id')} 的执行器...")
            
    except Exception as e:
        print(f"❌ 解析事件失败: {e}")

async def listen_for_events():
    """监听 PostgreSQL NOTIFY 的主循环"""
    settings = get_settings()
    
    if not settings.DATABASE_URL:
        print("❌ DATABASE_URL is not set in environment variables or .env file.")
        return

    # Pydantic 的 DSN 默认是 postgresql://，如果包含 +psycopg 则替换为原生协议
    db_url = str(settings.DATABASE_URL)
    if db_url.startswith("postgresql+psycopg://"):
        db_url = db_url.replace("postgresql+psycopg://", "postgresql://", 1)

    try:
        # 注意：这里继续使用原生的 psycopg.AsyncConnection 是非常正确的！
        # 因为 LISTEN 命令会一直阻塞当前连接，我们绝对不能使用 SQLAlchemy 的引擎连接池 (Engine)
        # 否则这个常驻进程会长期霸占并消耗尽池里的一个工作连接。
        async with await psycopg.AsyncConnection.connect(db_url, autocommit=True) as conn:
            channel = settings.EVENT_BUS_CHANNEL
            print(f"✅ 已连接到数据库，正在监听频道: '{channel}'...")
            
            # 执行 LISTEN 指令
            await conn.execute(f"LISTEN {channel}")
            
            # psycopg3 极其优雅的异步生成器接口
            # 它会自动处理底层的轮询，并在有消息时唤醒
            async for notify in conn.notifies():
                await event_handler(notify.payload, channel)
                
    except psycopg.OperationalError as e:
        print(f"💥 数据库连接错误: {e}")
    except asyncio.CancelledError:
        print("🛑 监听已停止")

if __name__ == "__main__":
    try:
        asyncio.run(listen_for_events())
    except KeyboardInterrupt:
        pass