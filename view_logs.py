"""
Streamlit app to visualize tau2 agent conversation logs.

Usage:
    uv run streamlit run view_logs.py
"""

import re
import streamlit as st
from pathlib import Path


def parse_log_file(log_path: str):
    """Parse the debug.log file and extract conversation messages."""
    with open(log_path, 'r') as f:
        content = f.read()

    messages = []

    # Pattern to match the structured log entries
    # Matches: ================================================================================
    #          USER: ... or ASSISTANT: ... or SYSTEM: ... or TOOL RESPONSE: ...
    #          ================================================================================

    # Split on the separator lines
    sections = content.split('=' * 80)

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Check for USER message
        if section.startswith('USER:'):
            message_content = section[5:].strip()
            # Remove trailing separator if present
            message_content = message_content.split('=' * 80)[0].strip()
            messages.append({
                'type': 'user',
                'content': message_content
            })

        # Check for ASSISTANT message
        elif 'ASSISTANT' in section:
            # Extract the content after the ASSISTANT tag
            lines = section.split('\n')
            assistant_label = lines[0] if lines else ''

            # Get everything after the first line
            message_content = '\n'.join(lines[1:]).strip()
            # Remove trailing separator if present
            message_content = message_content.split('=' * 80)[0].strip()

            # Parse out content and tool calls if present
            content_text = None
            tool_calls = None

            if 'Content:' in message_content and 'Tool Calls:' in message_content:
                parts = message_content.split('Tool Calls:', 1)
                content_text = parts[0].replace('Content:', '').strip()
                tool_calls = parts[1].strip()

                if content_text == 'None':
                    content_text = None
            else:
                content_text = message_content

            messages.append({
                'type': 'assistant',
                'label': assistant_label,
                'content': content_text,
                'tool_calls': tool_calls
            })

        # Check for SYSTEM message (injections and tool outputs)
        elif 'SYSTEM' in section:
            lines = section.split('\n')
            system_label = lines[0] if lines else ''
            message_content = '\n'.join(lines[1:]).strip()

            # Distinguish between tool outputs and injections
            if 'TOOL OUTPUTS' in system_label:
                messages.append({
                    'type': 'tool_outputs',
                    'label': system_label,
                    'content': message_content
                })
            else:
                messages.append({
                    'type': 'system',
                    'label': system_label,
                    'content': message_content
                })

        # Check for TOOL RESPONSE
        elif 'TOOL RESPONSE' in section:
            lines = section.split('\n')
            tool_label = lines[0] if lines else ''
            message_content = '\n'.join(lines[1:]).strip()
            # Remove trailing separator if present
            message_content = message_content.split('=' * 80)[0].strip()

            messages.append({
                'type': 'tool',
                'label': tool_label,
                'content': message_content
            })

    return messages


def main():
    st.set_page_config(
        page_title="Tau2 Agent Conversation Viewer",
        page_icon="🤖",
        layout="wide"
    )

    st.title("🤖 Tau2 Agent Conversation Viewer")

    # File selector
    log_file = st.sidebar.text_input(
        "Log file path",
        value="debug.log",
        help="Path to the debug.log file"
    )

    # Display options
    show_system = st.sidebar.checkbox("Show system injections", value=False)
    show_tool_outputs = st.sidebar.checkbox("Show tool outputs summary", value=True)
    show_tools = st.sidebar.checkbox("Show tool responses", value=True)

    if not Path(log_file).exists():
        st.error(f"File not found: {log_file}")
        st.info("Run the agent first to generate logs:\n\n```bash\nuv run tau2 run --domain airline --agent llm_agent_injection --agent-llm gpt-4.1 --user-llm gpt-4.1 --num-trials 1 --task-ids 5 --log-level DEBUG 2>&1 | tee debug.log\n```")
        return

    # Parse and display messages
    try:
        messages = parse_log_file(log_file)

        if not messages:
            st.warning("No messages found in log file")
            return

        st.sidebar.success(f"Found {len(messages)} messages")

        # Display messages
        for i, msg in enumerate(messages):
            msg_type = msg['type']

            # Skip based on filter settings
            if msg_type == 'system' and not show_system:
                continue
            if msg_type == 'tool_outputs' and not show_tool_outputs:
                continue
            if msg_type == 'tool' and not show_tools:
                continue

            # Display USER messages
            if msg_type == 'user':
                with st.chat_message("user"):
                    st.markdown(msg['content'])

            # Display ASSISTANT messages
            elif msg_type == 'assistant':
                with st.chat_message("assistant"):
                    if msg.get('label'):
                        st.caption(msg['label'])
                    if msg.get('content'):
                        st.markdown(msg['content'])
                    if msg.get('tool_calls'):
                        st.code(msg['tool_calls'], language='python')

            # Display SYSTEM messages (injections)
            elif msg_type == 'system':
                with st.expander(f"🔧 {msg.get('label', 'System Injection')}", expanded=False):
                    st.markdown(msg['content'])

            # Display TOOL OUTPUTS messages (persistent)
            elif msg_type == 'tool_outputs':
                with st.expander(f"📊 {msg.get('label', 'Tool Outputs Summary')}", expanded=True):
                    st.markdown(msg['content'])

            # Display TOOL RESPONSE messages
            elif msg_type == 'tool':
                if show_tools:
                    with st.chat_message("assistant", avatar="🔧"):
                        st.caption(msg.get('label', 'Tool Response'))
                        # Try to format as JSON if possible
                        content = msg['content']
                        if content.strip().startswith('{'):
                            try:
                                st.json(content)
                            except:
                                st.code(content, language='json')
                        else:
                            st.code(content)

    except Exception as e:
        st.error(f"Error parsing log file: {e}")
        st.exception(e)


if __name__ == "__main__":
    main()
