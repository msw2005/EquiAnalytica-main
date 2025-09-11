from google.adk.agents.callback_context import CallbackContext

# --- Define your callback function ---
def save_agent_output(callback_context: CallbackContext) -> None:
    print(f"Callback running before agent returns: {callback_context.agent_name}")
    
    agent_name = callback_context.agent_name
    state = callback_context.state

    output_key = f"{agent_name}_output"

    md_content = state.get(output_key, None)
    if md_content:
        filename = f"reports/{agent_name}_report.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"[Callback] Saved {agent_name} output to {filename}")


    return None # Allow the model call to proceed


def call_log(callback_context: CallbackContext) -> None:

    agent_name = callback_context.agent_name
    state = callback_context.state

    print(f"[Callback] {agent_name} called with state: {state}")


    return None