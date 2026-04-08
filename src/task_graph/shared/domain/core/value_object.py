from pydantic import BaseModel, ConfigDict


class ValueObject(BaseModel):
    """值对象基类 特征： 1. 不可变（frozen=True） 2. 相等性基于所有属性值 3. 无唯一标识"""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        from_attributes=True,
    )
