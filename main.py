import os

from dotenv import load_dotenv
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from chart_agent.agent import chart_agent


def main():
    """啟動 ADK Agent."""
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 錯誤：找不到 GOOGLE_API_KEY")
        print("請在 .env 檔案中設定：GOOGLE_API_KEY=your_api_key")
        return

    print("✅ 已載入 Google API Key")
    print("🚀 正在啟動 Chart Generation Agent...")

    artifact_service = InMemoryArtifactService()

    # 建立 Runner
    runner = Runner(
        agent=chart_agent,
        app_name="chart_generator",
        artifact_service=artifact_service,
        session_service=InMemorySessionService(),
    )

    print("\n" + "=" * 60)
    print("📊 Chart Generation Agent 已準備就緒！")
    print("=" * 60)
    print("\n使用方式：")
    print("1. 在網頁介面上傳 CSV 檔案")
    print("2. 告訴 Agent 你想要什麼類型的圖表")
    print("3. Agent 會分析資料並生成圖表")
    print("\n範例 prompt：")
    print('  - "請分析這個 CSV 檔案"')
    print('  - "用銷售額和日期畫一個折線圖"')
    print('  - "幫我做一個長條圖比較各產品的銷量"')
    print("\n" + "=" * 60)

    runner.run_web()


if __name__ == "__main__":
    main()
