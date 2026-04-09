"""
Bootstrap configuration for the entire application.
Loads project-level settings and merges context configurations.
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from task_graph.shared.config import SharedSettings, get_settings as get_shared_settings
from task_graph.planning.config import Settings as PlanningSettings, get_settings as get_planning_settings

class AppConfig(BaseSettings):
    """
    Top-level application configuration.
    包含了 Project 级别的全局配置，并聚合了所有上下文的配置。
    """
    # --- Project 级别的全局配置 ---
    environment: str = "development" # 可通过环境变量 ENVIRONMENT=production 覆盖
    debug: bool = False
    log_level: str = Field(default="INFO", description="Global logging level")
    
    # --- 聚合的限界上下文配置 (保留自治性) ---
    # 使用 default_factory 确保每次实例化 AppConfig 时，都会调用各自的 get_settings()
    shared: SharedSettings = Field(default_factory=get_shared_settings)
    planning: PlanningSettings = Field(default_factory=get_planning_settings)

    model_config = SettingsConfigDict(
        # 允许从 .env 文件读取全局配置
        env_file=".env", 
        env_file_encoding="utf-8",
        # 设置为 True 可以锁定配置，防止运行时被修改
        frozen=True,
        # 忽略多余的环境变量，防止与其他不相关的环境变量冲突
        extra="ignore" 
    )

def load_all_configurations() -> AppConfig:
    """实例化全局配置（会自动触发各级环境变量的读取）"""
    return AppConfig()

__all__ = ["AppConfig", "load_all_configurations"]