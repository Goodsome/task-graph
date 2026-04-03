from pydantic import BaseModel, ConfigDict


class Entity(BaseModel):
    """实体基类 特征： 1. 具有唯一标识（ID） 2. 相等性基于 ID 判断 3. 可变（但应通过行为方法修改） 4. 使用 UTC 时区记录时间"""

    model_config = ConfigDict(extra="forbid")
