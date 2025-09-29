import io

import google.genai.types as types
import matplotlib.pyplot as plt
import pandas as pd
from google.adk.agents import LlmAgent, RunConfig
from google.adk.agents.callback_context import CallbackContext
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool, ToolContext
import google.genai.types as types


async def analyze_csv(tool_context: ToolContext) -> dict:
    """分析上傳的 CSV 檔案結構和內容。"""
    try:
        artifacts = await tool_context.list_artifacts()
        csv_files = [f for f in artifacts if f.endswith(".csv")]

        if not csv_files:
            return {
                "status": "error",
                "message": "找不到 CSV 檔案。請先上傳 CSV 檔案。",
            }

        csv_filename = csv_files[-1]
        csv_artifact = await tool_context.load_artifact(csv_filename)
        csv_data = csv_artifact.inline_data.data.decode("utf-8")
        df = pd.read_csv(io.StringIO(csv_data))

        analysis = {
            "status": "success",
            "filename": csv_filename,
            "rows": len(df),
            "columns": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "preview": df.head(5).to_dict("records"),
            "summary": df.describe().to_dict() if len(df) > 0 else {},
        }

        return analysis

    except Exception as e:
        return {"status": "error", "message": f"CSV 分析失敗: {str(e)}"}


async def generate_chart(
    chart_type: str,
    x_column: str,
    y_column: str,
    title: str = "Chart",
    tool_context: ToolContext = None,
) -> dict:
    """根據指定參數生成圖表。"""
    try:
        artifacts = await tool_context.list_artifacts()
        csv_files = [f for f in artifacts if f.endswith(".csv")]

        if not csv_files:
            return {"status": "error", "message": "找不到 CSV 檔案"}

        csv_artifact = await tool_context.load_artifact(csv_files[-1])
        csv_data = csv_artifact.inline_data.data.decode("utf-8")
        df = pd.read_csv(io.StringIO(csv_data))

        if x_column not in df.columns or y_column not in df.columns:
            return {
                "status": "error",
                "message": f"欄位不存在。可用欄位: {list(df.columns)}",
            }

        plt.figure(figsize=(10, 6))

        if chart_type == "line":
            plt.plot(df[x_column], df[y_column], marker="o", linewidth=2)
        elif chart_type == "bar":
            plt.bar(df[x_column], df[y_column])
        elif chart_type == "scatter":
            plt.scatter(df[x_column], df[y_column], alpha=0.6, s=100)
        elif chart_type == "histogram":
            plt.hist(df[y_column], bins=20, edgecolor="black")
        else:
            plt.close()
            return {"status": "error", "message": f"不支援的圖表類型: {chart_type}"}

        plt.title(title, fontsize=14, fontweight="bold")
        plt.xlabel(x_column, fontsize=12)
        plt.ylabel(y_column, fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
        chart_bytes = buffer.getvalue()
        plt.close()

        chart_artifact = types.Part.from_bytes(data=chart_bytes, mime_type="image/png")

        filename = f"chart_{chart_type}_{x_column}_{y_column}.png"
        version = await tool_context.save_artifact(
            filename=filename, artifact=chart_artifact
        )

        return {
            "status": "success",
            "message": f"已成功生成 {chart_type} 圖表",
            "filename": filename,
            "version": version,
        }

    except Exception as e:
        plt.close()
        return {"status": "error", "message": f"圖表生成失敗: {str(e)}"}


async def execute_custom_code(python_code: str, tool_context: ToolContext) -> dict:
    """執行自訂的 Python 繪圖程式碼。"""
    try:
        artifacts = await tool_context.list_artifacts()
        csv_files = [f for f in artifacts if f.endswith(".csv")]

        if not csv_files:
            return {"status": "error", "message": "找不到 CSV 檔案"}

        csv_artifact = await tool_context.load_artifact(csv_files[-1])
        csv_data = csv_artifact.inline_data.data.decode("utf-8")

        exec_globals = {
            "pd": pd,
            "plt": plt,
            "io": io,
            "csv_data": csv_data,
            "StringIO": io.StringIO,
        }

        exec(python_code, exec_globals)

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
        chart_bytes = buffer.getvalue()
        plt.close()

        chart_artifact = types.Part.from_bytes(data=chart_bytes, mime_type="image/png")

        filename = "custom_chart.png"
        version = await tool_context.save_artifact(
            filename=filename, artifact=chart_artifact
        )

        return {
            "status": "success",
            "message": "自訂圖表已成功生成",
            "filename": filename,
            "version": version,
        }

    except Exception as e:
        plt.close()
        return {"status": "error", "message": f"程式碼執行失敗: {str(e)}"}


def save_uploaded_file_as_artifact(context: CallbackContext):
    """Saves the first uploaded file in the context as an artifact."""
    if context.user_content and context.user_content.parts:
        for part in context.user_content.parts:
            if part.data and part.mime_type:
                # Assuming the first data part is the uploaded file
                # You might want more sophisticated logic to identify specific files
                filename = (
                    "uploaded_file.txt"  # Or extract from part metadata if available
                )
                artifact = types.Part.from_data(
                    data=part.data, mime_type=part.mime_type
                )
                try:
                    version = context.save_artifact(
                        filename=filename, artifact=artifact
                    )
                    print(f"Artifact '{filename}' saved with version {version}")
                except Exception as e:
                    print(f"Failed to save artifact: {e}")
                break  # Save only the first found file for this example


AGENT_INSTRUCTION = """
你是一個專業的數據視覺化助手，擅長分析 CSV 資料並生成各種圖表。

## 你的工作流程：

1. **分析 CSV 檔案**
   - 當使用者上傳 CSV 檔案後，使用 analyze_csv 工具分析資料結構
   - 告訴使用者檔案有哪些欄位、資料型態、行數等資訊

2. **理解使用者需求**
   - 仔細聆聽使用者想要什麼類型的圖表
   - 主動詢問 X 軸、Y 軸、圖表類型

3. **生成圖表**
   - 使用 generate_chart 工具生成：line、bar、scatter、histogram

4. **進階客製化**
   - 複雜需求使用 execute_custom_code 執行 Python 程式碼

## 注意事項：
- 永遠先使用 analyze_csv 了解資料結構
- 確保欄位名稱正確
- 保持友善、專業的溝通風格
"""


root_agent = LlmAgent(
    name="chart_generation_agent",
    model="gemini-2.0-flash-exp",
    description="專業的數據視覺化助手",
    instruction=AGENT_INSTRUCTION,
    tools=[
        FunctionTool(func=analyze_csv),
        FunctionTool(func=generate_chart),
        FunctionTool(func=execute_custom_code),
    ],
    before_model_callback=save_uploaded_file_as_artifact,
)


session_service = InMemorySessionService()

config = RunConfig(save_input_blobs_as_artifacts=True)
runner = Runner(
    agent=root_agent,  # The agent we want to run
    app_name="chart_generation_agent",  # Associates runs with our app
    session_service=session_service,  # Uses our session manager
    # Callback to save uploads
)
