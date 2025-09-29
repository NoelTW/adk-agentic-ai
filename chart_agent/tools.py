from google.adk.tools import Tool, ToolResult


class SaveFileTool(Tool):
    def __init__(self, storage_path: str):
        super().__init__(name="save_file", description="Saves content to a file.")
        self.storage_path = storage_path

    async def _run(self, file_name: str, content: str) -> ToolResult:
        try:
            full_path = f"{self.storage_path}/{file_name}"
            with open(full_path, "w") as f:
                f.write(content)
            return ToolResult(
                output=f"File '{file_name}' saved successfully at {full_path}"
            )
        except Exception as e:
            return ToolResult(error=f"Failed to save file: {e}")
