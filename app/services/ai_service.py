"""
AI服务
"""
import httpx
import json
import asyncio
from typing import Optional, Dict, Any
from app.config import get_settings

settings = get_settings()


class AIService:
    """AI服务"""

    # 装修方案生成提示词模板
    PLAN_PROMPT_TEMPLATE = """你是资深全屋装修设计师，根据用户信息生成详细、可落地的家用装修方案。
用户户型：{house_type}，面积：{area}平方米，装修风格：{style}
装修预算：{budget}，常住人口：{population}人，特殊需求：{special_needs}

要求输出内容：
1. 整体设计理念
2. 各空间（客厅/卧室/厨房/卫生间）详细设计方案
3. 主材搭配推荐
4. 色彩搭配方案
5. 施工先后顺序
6. 装修避坑重点
7. 预算分配建议

内容通俗易懂，适合装修小白，结构清晰，分点说明。"""

    def __init__(self):
        self.text_api_url = settings.ai_text_api_url
        self.text_api_key = settings.ai_text_api_key
        self.image_api_url = settings.ai_image_api_url
        self.image_api_key = settings.ai_image_api_key

    async def generate_plan(
        self,
        house_type: str,
        area: float,
        style: str,
        budget: str,
        population: int,
        special_needs: Optional[str] = None
    ) -> str:
        """
        生成装修方案

        Args:
            house_type: 户型格局
            area: 面积
            style: 装修风格
            budget: 预算档位
            population: 常住人口
            special_needs: 特殊需求

        Returns:
            生成的方案文本
        """
        # 构建提示词
        prompt = self.PLAN_PROMPT_TEMPLATE.format(
            house_type=house_type,
            area=area,
            style=style,
            budget=budget,
            population=population,
            special_needs=special_needs or "无特殊需求"
        )

        # 调用AI接口
        try:
            result = await self._call_text_ai(prompt)
            return result
        except Exception as e:
            # 返回模拟数据
            return self._get_mock_plan(house_type, area, style, budget)

    async def _call_text_ai(self, prompt: str) -> str:
        """
        调用文本AI接口

        Args:
            prompt: 提示词

        Returns:
            AI响应文本
        """
        headers = {
            "Authorization": f"Bearer {self.text_api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "doubao-pro",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.text_api_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60.0
            )
            result = response.json()
            return result["choices"][0]["message"]["content"]

    async def generate_render(
        self,
        house_img_url: str,
        style: str,
        room: str = "all"
    ) -> str:
        """
        生成装修渲染图

        Args:
            house_img_url: 户型图URL
            style: 装修风格
            room: 空间类型

        Returns:
            生成的图片URL
        """
        # 调用图生图AI接口
        try:
            result = await self._call_image_ai(house_img_url, style, room)
            return result
        except Exception as e:
            # 返回模拟数据
            return self._get_mock_render_url(style)

    async def _call_image_ai(self, image_url: str, style: str, room: str) -> str:
        """
        调用图生图AI接口

        Args:
            image_url: 输入图片URL
            style: 目标风格
            room: 空间类型

        Returns:
            生成的图片URL
        """
        headers = {
            "Authorization": f"Bearer {self.image_api_key}",
            "Content-Type": "application/json"
        }

        # TODO: 根据实际AI API调整请求格式
        data = {
            "model": "wanx2.1",
            "input": {
                "image": image_url,
                "prompt": f"将图片转换为{style}风格的{room}装修效果图"
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.image_api_url}/text2image/image_synthesis",
                headers=headers,
                json=data,
                timeout=120.0
            )
            result = response.json()
            return result.get("data", {}).get("image_url", "")

    @staticmethod
    def _get_mock_plan(house_type: str, area: float, style: str, budget: str) -> str:
        """获取模拟装修方案"""
        return f"""# {style}风格装修方案

## 一、整体设计理念
本方案采用{style}风格设计，强调简约、自然、温馨的居住氛围。整体色调以柔和的中性色为主，搭配木质元素，营造舒适宜居的家庭空间。

## 二、各空间详细设计方案

### 客厅
- 采用开放式布局，增加空间通透感
- 电视背景墙采用简约设计，配合收纳柜
- 沙发区以舒适为首要原则，选择布艺沙发

### 卧室
- 主卧采用步入式衣柜设计，增加收纳空间
- 床头背景墙采用软包设计，增加质感
- 次卧以多功能为主，榻榻米设计

### 厨房
- U型厨房布局，操作动线流畅
- 选用石英石台面，耐磨易清洁
- 安装集成灶，节省空间

### 卫生间
- 干湿分离设计，提高使用效率
- 选用悬挂式马桶，节省空间
- 浴室柜采用悬空设计

## 三、主材搭配推荐
| 空间 | 主材 | 品牌建议 |
|------|------|----------|
| 客厅 | 地板 | 实木复合地板 |
| 卧室 | 门 | 实木复合门 |
| 厨房 | 瓷砖 | 抛光砖 |
| 卫生间 | 洁具 | 国产品牌 |

## 四、色彩搭配方案
- 主色调：米白、浅灰
- 辅色调：木色、浅咖
- 点缀色：绿色植物、装饰画

## 五、施工顺序
1. 拆改工程
2. 水电改造
3. 泥瓦工程
4. 木工工程
5. 油漆工程
6. 安装工程
7. 保洁开荒

## 六、装修避坑重点
1. 水电改造前务必确认好家具尺寸和电器位置
2. 防水工程要做24小时闭水试验
3. 瓷砖铺贴要留缝，避免热胀冷缩
4. 乳胶漆颜色要在阳光下确认

## 七、预算分配建议
- 设计费：5%
- 基础装修：35%
- 主材采购：30%
- 家具家电：25%
- 软装配饰：5%

---
方案生成时间：2024年
本方案仅供参考，实际施工请咨询专业设计师
"""

    @staticmethod
    def _get_mock_render_url(style: str) -> str:
        """获取模拟渲染图URL"""
        # 返回占位图
        return f"https://via.placeholder.com/800x600/{style}/ffffff?text={style}+装修效果图"
