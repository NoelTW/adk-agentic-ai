from google.adk.agents import Agent


root_agent = Agent(
    name="genie_agent",
    model="gemini-2.0-flash",
    description="An AI agent that can assist with various tasks using the Gemini 2.0 Flash model.",
    instruction="You're a helpful assistant that can perform a variety of tasks.",
)
