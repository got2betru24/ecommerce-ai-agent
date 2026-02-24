import anthropic
from .database import save_message, load_history
from .tools import tools, process_tool_call

client = anthropic.Anthropic()

SYSTEM_PROMPT = """
You are an e-commerce assistant helping with customer order lookup or product lookup. You should be cheerful and empathetic but concise.
Only answer questions related to orders and products. If a question falls outside these topics, politely decline and explain what you can help with. Do not answer from general knowledge.
When discussing customer orders, ProductIds are not helpful to them. Make sure you include actual product details instead.
Never share order details unless the customer has provided identifying information that matched a record. If a lookup returns no match, do not speculate about or reveal what information exists in the system.
"""


def run_agent(user_message: str, session_id: str):
    """
    Generator function that yields text chunks as Claude produces them.
    Saves conversation history to the database as it goes.
    """
    save_message(session_id, "user", user_message)
    messages = load_history(session_id)

    full_response = ""

    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            tools=tools,
            system=SYSTEM_PROMPT,
            messages=messages,
        )

        # Claude is done - stream the final text response
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    # Yield each chunk of text to the frontend
                    yield block.text
                    full_response += block.text

            # Save the complete response to history
            save_message(session_id, "assistant", full_response)
            return

        # Claude wants to use a tool - handle silently, don't stream tool calls
        if response.stop_reason == "tool_use":
            content_to_save = [block.model_dump() for block in response.content]
            save_message(session_id, "assistant", content_to_save, "tool_use")

            # Use the dict version in memory too, not the SDK objects
            messages.append({"role": "assistant", "content": content_to_save})

            tool_results = []
            for block in content_to_save:  # iterate dicts, not SDK objects
                if block["type"] == "tool_use":
                    result = process_tool_call(block["name"], block["input"])
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": block["id"], "content": result}
                    )

            messages.append({"role": "user", "content": tool_results})
            save_message(session_id, "user", tool_results, "tool_result")
