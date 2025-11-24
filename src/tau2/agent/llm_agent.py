import json
from copy import deepcopy
from pathlib import Path
from typing import List, Optional

from loguru import logger
from pydantic import BaseModel

from tau2.agent.base import (
    LocalAgent,
    ValidAgentInputMessage,
    is_valid_agent_history_message,
)
from tau2.data_model.message import (
    APICompatibleMessage,
    AssistantMessage,
    Message,
    MultiToolMessage,
    SystemMessage,
    ToolMessage,
    UserMessage,
)
from tau2.data_model.tasks import Action, Task
from tau2.environment.tool import Tool, as_tool
from tau2.utils.llm_utils import generate

AGENT_INSTRUCTION = """
You are a customer service agent that helps the user according to the <policy> provided below.
In each turn you can either:
- Send a message to the user.
- Make a tool call.
You cannot do both at the same time.

Try to be helpful and always follow the policy. Always make sure you generate valid JSON only.
""".strip()

SYSTEM_PROMPT = """
<instructions>
{agent_instruction}
</instructions>
<policy>
{domain_policy}
</policy>
""".strip()


class LLMAgentState(BaseModel):
    """The state of the agent."""

    system_messages: list[SystemMessage]
    messages: list[APICompatibleMessage]
    tool_outputs: list[dict] = []  # Track all tool calls and responses


class LLMAgent(LocalAgent[LLMAgentState]):
    """
    An LLM agent that can be used to solve a task.
    """

    def __init__(
        self,
        tools: List[Tool],
        domain_policy: str,
        llm: Optional[str] = None,
        llm_args: Optional[dict] = None,
    ):
        """
        Initialize the LLMAgent.
        """
        super().__init__(tools=tools, domain_policy=domain_policy)
        self.llm = llm
        self.llm_args = deepcopy(llm_args) if llm_args is not None else {}

    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT.format(
            domain_policy=self.domain_policy, agent_instruction=AGENT_INSTRUCTION
        )

    def get_init_state(
        self, message_history: Optional[list[Message]] = None
    ) -> LLMAgentState:
        """Get the initial state of the agent.

        Args:
            message_history: The message history of the conversation.

        Returns:
            The initial state of the agent.
        """
        if message_history is None:
            message_history = []
        assert all(is_valid_agent_history_message(m) for m in message_history), (
            "Message history must contain only AssistantMessage, UserMessage, or ToolMessage to Agent."
        )
        return LLMAgentState(
            system_messages=[SystemMessage(role="system", content=self.system_prompt)],
            messages=message_history,
        )

    def generate_next_message(
        self, message: ValidAgentInputMessage, state: LLMAgentState
    ) -> tuple[AssistantMessage, LLMAgentState]:
        """
        Respond to a user or tool message.
        """
        if isinstance(message, MultiToolMessage):
            state.messages.extend(message.tool_messages)
        else:
            state.messages.append(message)
        messages = state.system_messages + state.messages
        assistant_message = generate(
            model=self.llm,
            tools=self.tools,
            messages=messages,
            **self.llm_args,
        )
        state.messages.append(assistant_message)
        return assistant_message, state

    def set_seed(self, seed: int):
        """Set the seed for the LLM."""
        if self.llm is None:
            raise ValueError("LLM is not set")
        cur_seed = self.llm_args.get("seed", None)
        if cur_seed is not None:
            logger.warning(f"Seed is already set to {cur_seed}, resetting it to {seed}")
        self.llm_args["seed"] = seed


AGENT_GT_INSTRUCTION = """
You are testing that our user simulator is working correctly.
User simulator will have an issue for you to solve.
You must behave according to the <policy> provided below.
To make following the policy easier, we give you the list of resolution steps you are expected to take.
These steps involve either taking an action or asking the user to take an action.

In each turn you can either:
- Send a message to the user.
- Make a tool call.
You cannot do both at the same time.

Try to be helpful and always follow the policy. Always make sure you generate valid JSON only.
""".strip()

SYSTEM_PROMPT_GT = """
<instructions>
{agent_instruction}
</instructions>
<policy>
{domain_policy}
</policy>
<resolution_steps>
{resolution_steps}
</resolution_steps>
""".strip()


class LLMGTAgent(LocalAgent[LLMAgentState]):
    """
    An GroundTruth agent that can be used to solve a task.
    This agent will receive the expected actions.
    """

    def __init__(
        self,
        tools: List[Tool],
        domain_policy: str,
        task: Task,
        llm: Optional[str] = None,
        llm_args: Optional[dict] = None,
        provide_function_args: bool = True,
    ):
        """
        Initialize the LLMAgent.
        If provide_function_args is True, the resolution steps will include the function arguments.
        """
        super().__init__(tools=tools, domain_policy=domain_policy)
        assert self.check_valid_task(task), (
            f"Task {task.id} is not valid. Cannot run GT agent."
        )
        self.task = task
        self.llm = llm
        self.llm_args = deepcopy(llm_args) if llm_args is not None else {}
        self.provide_function_args = provide_function_args

    @classmethod
    def check_valid_task(cls, task: Task) -> bool:
        """
        Check if the task is valid.
        Only the tasks that require at least one action are valid.
        """
        if task.evaluation_criteria is None:
            return False
        expected_actions = task.evaluation_criteria.actions or []
        if len(expected_actions) == 0:
            return False
        return True

    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT_GT.format(
            agent_instruction=AGENT_GT_INSTRUCTION,
            domain_policy=self.domain_policy,
            resolution_steps=self.make_agent_instructions_from_actions(),
        )

    def get_init_state(
        self, message_history: Optional[list[Message]] = None
    ) -> LLMAgentState:
        """Get the initial state of the agent.

        Args:
            message_history: The message history of the conversation.

        Returns:
            The initial state of the agent.
        """
        if message_history is None:
            message_history = []
        assert all(is_valid_agent_history_message(m) for m in message_history), (
            "Message history must contain only AssistantMessage, UserMessage, or ToolMessage to Agent."
        )
        return LLMAgentState(
            system_messages=[SystemMessage(role="system", content=self.system_prompt)],
            messages=message_history,
        )

    def generate_next_message(
        self, message: ValidAgentInputMessage, state: LLMAgentState
    ) -> tuple[AssistantMessage, LLMAgentState]:
        """
        Respond to a user or tool message.
        """
        if isinstance(message, MultiToolMessage):
            state.messages.extend(message.tool_messages)
        else:
            state.messages.append(message)
        messages = state.system_messages + state.messages
        assistant_message = generate(
            model=self.llm,
            tools=self.tools,
            messages=messages,
            **self.llm_args,
        )
        state.messages.append(assistant_message)
        return assistant_message, state

    def set_seed(self, seed: int):
        """Set the seed for the LLM."""
        if self.llm is None:
            raise ValueError("LLM is not set")
        cur_seed = self.llm_args.get("seed", None)
        if cur_seed is not None:
            logger.warning(f"Seed is already set to {cur_seed}, resetting it to {seed}")
        self.llm_args["seed"] = seed

    def make_agent_instructions_from_actions(self) -> str:
        """
        Make agent instructions from a list of actions
        """
        lines = []
        for i, action in enumerate(self.task.evaluation_criteria.actions):
            lines.append(
                f"[Step {i + 1}] {self.make_agent_instructions_from_action(action=action, include_function_args=self.provide_function_args)}"
            )
        return "\n".join(lines)

    @classmethod
    def make_agent_instructions_from_action(
        cls, action: Action, include_function_args: bool = False
    ) -> str:
        """
        Make agent instructions from an action.
        If the action is a user action, returns instructions for the agent to give to the user.
        If the action is an agent action, returns instructions for the agent to perform the action.
        """
        if action.requestor == "user":
            if include_function_args:
                return f"Instruct the user to perform the following action: {action.get_func_format()}."
            else:
                return f"User action: {action.name}."
        elif action.requestor == "assistant":
            if include_function_args:
                return f"Perform the following action: {action.get_func_format()}."
            else:
                return f"Assistant action: {action.name}."
        else:
            raise ValueError(f"Unknown action requestor: {action.requestor}")


AGENT_SOLO_INSTRUCTION = """
You are a customer service agent that helps the user according to the <policy> provided below.
You will be provided with a ticket that contains the user's request.
You will need to plan and call the appropriate tools to solve the ticket.

You cannot communicate with the user, only make tool calls.
Stop when you consider that you have solved the ticket.
To do so, send a message containing a single tool call to the `{stop_function_name}` tool. Do not include any other tool calls in this last message.

Always follow the policy. Always make sure you generate valid JSON only.
""".strip()

SYSTEM_PROMPT_SOLO = """
<instructions>
{agent_instruction}
</instructions>
<policy>
{domain_policy}
</policy>
<ticket>
{ticket}
</ticket>
""".strip()


class LLMSoloAgent(LocalAgent[LLMAgentState]):
    """
    An LLM agent that can be used to solve a task without any interaction with the customer.
    The task need to specify a ticket format.
    """

    STOP_FUNCTION_NAME = "done"
    TRANSFER_TOOL_NAME = "transfer_to_human_agents"
    STOP_TOKEN = "###STOP###"

    def __init__(
        self,
        tools: List[Tool],
        domain_policy: str,
        task: Task,
        llm: Optional[str] = None,
        llm_args: Optional[dict] = None,
    ):
        """
        Initialize the LLMAgent.
        """
        super().__init__(tools=tools, domain_policy=domain_policy)
        assert self.check_valid_task(task), (
            f"Task {task.id} is not valid. Cannot run GT agent."
        )
        self.task = task
        self.llm = llm
        self.llm_args = llm_args if llm_args is not None else {}
        self.add_stop_tool()
        self.validate_tools()

    def add_stop_tool(self) -> None:
        """Add the stop tool to the tools."""

        def done() -> str:
            """Call this function when you are done with the task."""
            return self.STOP_TOKEN

        self.tools.append(as_tool(done))

    def validate_tools(self) -> None:
        """Check if the tools are valid."""
        tool_names = {tool.name for tool in self.tools}
        if self.TRANSFER_TOOL_NAME not in tool_names:
            logger.warning(
                f"Tool {self.TRANSFER_TOOL_NAME} not found in tools. This tool is required for the agent to transfer the user to a human agent."
            )
        if self.STOP_FUNCTION_NAME not in tool_names:
            raise ValueError(f"Tool {self.STOP_FUNCTION_NAME} not found in tools.")

    @classmethod
    def check_valid_task(cls, task: Task) -> bool:
        """
        Check if the task is valid.
        Task should contain a ticket and evaluation criteria.
        If the task contains an initial state, the message history should only contain tool calls and responses.
        """
        if task.initial_state is not None:
            message_history = task.initial_state.message_history or []
            for message in message_history:
                if isinstance(message, UserMessage):
                    return False
                if isinstance(message, AssistantMessage) and not message.is_tool_call():
                    return False
            return True
        if task.ticket is None:
            return False
        if task.evaluation_criteria is None:
            return False
        expected_actions = task.evaluation_criteria.actions or []
        if len(expected_actions) == 0:
            return False
        return True

    @property
    def system_prompt(self) -> str:
        agent_instruction = AGENT_SOLO_INSTRUCTION.format(
            stop_function_name=self.STOP_FUNCTION_NAME,
            stop_token=self.STOP_TOKEN,
        )
        return SYSTEM_PROMPT_SOLO.format(
            agent_instruction=agent_instruction,
            domain_policy=self.domain_policy,
            ticket=self.task.ticket,
        )

    def _check_if_stop_toolcall(self, message: AssistantMessage) -> AssistantMessage:
        """Check if the message is a stop message.
        If the message contains a tool call with the name STOP_FUNCTION_NAME, then the message is a stop message.
        """
        is_stop = False
        for tool_call in message.tool_calls:
            if tool_call.name == self.STOP_FUNCTION_NAME:
                is_stop = True
                break
        if is_stop:
            message.content = self.STOP_TOKEN
            message.tool_calls = None
        return message

    @classmethod
    def is_stop(cls, message: AssistantMessage) -> bool:
        """Check if the message is a stop message."""
        if message.content is None:
            return False
        return cls.STOP_TOKEN in message.content

    def get_init_state(
        self, message_history: Optional[list[Message]] = None
    ) -> LLMAgentState:
        """Get the initial state of the agent.

        Args:
            message_history: The message history of the conversation.

        Returns:
            The initial state of the agent.
        """
        if message_history is None:
            message_history = []
        assert all(is_valid_agent_history_message(m) for m in message_history), (
            "Message history must contain only AssistantMessage, UserMessage, or ToolMessage to Agent."
        )
        return LLMAgentState(
            system_messages=[SystemMessage(role="system", content=self.system_prompt)],
            messages=message_history,
        )

    def generate_next_message(
        self, message: Optional[ValidAgentInputMessage], state: LLMAgentState
    ) -> tuple[AssistantMessage, LLMAgentState]:
        """
        Respond to a user or tool message.
        """
        if isinstance(message, UserMessage):
            raise ValueError("LLMSoloAgent does not support user messages.")
        if isinstance(message, MultiToolMessage):
            state.messages.extend(message.tool_messages)
        elif message is None:
            assert len(state.messages) == 0, "Message history should be empty"
        else:
            state.messages.append(message)
        messages = state.system_messages + state.messages
        assistant_message = generate(
            model=self.llm,
            tools=self.tools,
            messages=messages,
            tool_choice="required",
            **self.llm_args,
        )
        if not assistant_message.is_tool_call():
            raise ValueError("LLMSoloAgent only supports tool calls.")
        message = self._check_if_stop_toolcall(assistant_message)
        state.messages.append(assistant_message)
        return assistant_message, state

    def set_seed(self, seed: int):
        """Set the seed for the LLM."""
        if self.llm is None:
            raise ValueError("LLM is not set")
        cur_seed = self.llm_args.get("seed", None)
        if cur_seed is not None:
            logger.warning(f"Seed is already set to {cur_seed}, resetting it to {seed}")
        self.llm_args["seed"] = seed


AGENT_INJECTION_INSTRUCTION = """
You are a customer service agent that helps the user according to the <policy> provided below.
In each turn you can either:
- Send a message to the user.
- Make a tool call.
You cannot do both at the same time.

When you propose a tool call, you will be provided with a detailed handbook for that specific tool.
The handbook contains:
- **Prerequisites**: Information that must be collected from the user before proceeding
- **Conditional Checks**: Policy validations that must ALL pass before the tool can be executed
- Detailed argument specifications and constraints
- Examples of correct and incorrect usage

IMPORTANT: After reviewing the handbook, you must RECONSIDER your action:

1. **Verify Prerequisites are satisfied**: Check if all required information has been collected from the user.
   - If ANY prerequisite information is missing → DO NOT make the tool call yet
   - Instead, ASK the user for the missing information

2. **Verify Conditional Checks pass**: Check if all policy validations are satisfied.
   - If ANY conditional check fails → DO NOT make the tool call
   - Instead, choose one of these alternatives:
     a) Ask clarifying questions to gather information that might satisfy the checks
     b) Explain to the user why the action cannot be performed according to policy
     c) Suggest an alternative action or tool that better fits the situation

3. **Proceed with tool call ONLY if**:
   - All Prerequisites have been collected
   - All Conditional Checks pass
   - All arguments are provided with correct types and formats

Try to be helpful and always follow the policy. Always make sure you generate valid JSON only.
""".strip()

SYSTEM_PROMPT_INJECTION = """
<instructions>
{agent_instruction}
</instructions>
<policy>
{domain_policy}
</policy>
""".strip()


class LLMInjectionAgent(LLMAgent):
    """
    An LLM agent with inference-time handbook injection.

    When the agent proposes a tool call, this agent:
    1. Intercepts the tool call proposal
    2. Rolls back the conversation by one step
    3. Injects the relevant tool handbook into the context
    4. Regenerates the response with the handbook
    5. Executes the final action (which may be revised)

    This allows the model to make more informed tool calls by having
    access to detailed tool documentation at decision time.
    """

    def __init__(
        self,
        tools: List[Tool],
        domain_policy: str,
        handbook_dir: Path,
        llm: Optional[str] = None,
        llm_args: Optional[dict] = None,
        max_injection_depth: int = 3,
    ):
        """
        Initialize the LLMInjectionAgent.

        Args:
            tools: List of tools available to the agent
            domain_policy: The domain policy text
            handbook_dir: Directory containing tool handbook markdown files
            llm: LLM model name
            llm_args: Additional arguments for the LLM
            max_injection_depth: Maximum number of recursive injections per turn
        """
        super().__init__(tools=tools, domain_policy=domain_policy, llm=llm, llm_args=llm_args)
        self.handbook_dir = Path(handbook_dir)
        self.max_injection_depth = max_injection_depth
        self.handbooks: dict[str, str] = {}
        self._load_handbooks()

    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT_INJECTION.format(
            domain_policy=self.domain_policy,
            agent_instruction=AGENT_INJECTION_INSTRUCTION
        )

    def _load_handbooks(self) -> None:
        """
        Load all tool handbooks from the handbook directory.

        Scans for files matching *_handbook.md pattern and extracts
        tool names by removing the _handbook.md suffix.
        """
        if not self.handbook_dir.exists():
            logger.warning(f"Handbook directory does not exist: {self.handbook_dir}")
            return

        handbook_files = list(self.handbook_dir.glob("*_handbook.md"))
        logger.info(f"Loading {len(handbook_files)} handbooks from {self.handbook_dir}")

        for handbook_file in handbook_files:
            # Extract tool name: book_reservation_handbook.md -> book_reservation
            tool_name = handbook_file.stem.replace("_handbook", "")

            try:
                with open(handbook_file, "r", encoding="utf-8") as f:
                    self.handbooks[tool_name] = f.read()
                logger.debug(f"Loaded handbook for tool: {tool_name}")
            except Exception as e:
                logger.error(f"Failed to load handbook {handbook_file}: {e}")

        # Check if all tools have handbooks
        tool_names = {tool.name for tool in self.tools}
        for tool_name in tool_names:
            if tool_name not in self.handbooks:
                logger.warning(f"No handbook found for tool: {tool_name}")

    def _get_handbook_for_tool(self, tool_name: str) -> Optional[str]:
        """
        Get the handbook content for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Handbook content as string, or None if not found
        """
        handbook = self.handbooks.get(tool_name)
        if handbook is None:
            logger.warning(f"Handbook not found for tool: {tool_name}")
        return handbook

    def _track_tool_outputs(self, tool_messages: list[ToolMessage], state: LLMAgentState) -> None:
        """
        Track tool outputs by matching ToolMessages with their corresponding ToolCalls.
        Only tracks 'get_*' tools (e.g., get_user_details, get_reservation_details).

        Args:
            tool_messages: List of ToolMessages to track
            state: Current agent state containing message history
        """
        # Build a map of tool call id -> ToolCall by scanning message history backwards
        tool_call_map = {}
        for msg in reversed(state.messages):
            if isinstance(msg, AssistantMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    if tc.id not in tool_call_map:
                        tool_call_map[tc.id] = tc

        # Match each ToolMessage with its ToolCall and record the output
        # Only track get_* tools (information gathering, not actions)
        for tool_msg in tool_messages:
            if tool_msg.id in tool_call_map:
                tool_call = tool_call_map[tool_msg.id]

                # Only track get_* tools
                if not tool_call.name.startswith('get_'):
                    logger.debug(f"Skipping non-get tool: {tool_call.name}")
                    continue

                state.tool_outputs.append({
                    "tool_name": tool_call.name,
                    "arguments": tool_call.arguments,
                    "response": tool_msg.content,
                    "turn": len(state.messages),  # Current turn index
                    "error": tool_msg.error,
                })
                logger.debug(f"Tracked tool output: {tool_call.name} with {len(str(tool_msg.content))} chars response")

        # Update the persistent tool outputs system message
        self._update_tool_outputs_system_message(state)

    def _update_tool_outputs_system_message(self, state: LLMAgentState) -> None:
        """
        Update the persistent tool outputs system message in state.system_messages.
        Creates the message if it doesn't exist, updates it if it does.

        Args:
            state: Current agent state
        """
        # Create the tool outputs content
        content = self._format_tool_outputs(state.tool_outputs)

        if not content:
            # No tool outputs to show - remove the message if it exists
            state.system_messages = [
                msg for msg in state.system_messages
                if not (msg.role == "system" and "TOOL OUTPUTS SUMMARY" in msg.content)
            ]
            return

        # Create the system message
        tool_outputs_msg = SystemMessage(role="system", content=content)

        # Find and replace existing tool outputs message, or append if not found
        found = False
        for i, msg in enumerate(state.system_messages):
            if msg.role == "system" and "TOOL OUTPUTS SUMMARY" in msg.content:
                state.system_messages[i] = tool_outputs_msg
                found = True
                logger.info(f"\n{'='*80}\nSYSTEM [TOOL OUTPUTS UPDATED]:\n{content}\n{'='*80}")
                break

        if not found:
            # Insert after the first system message (the main system prompt)
            if len(state.system_messages) > 0:
                state.system_messages.insert(1, tool_outputs_msg)
            else:
                state.system_messages.append(tool_outputs_msg)
            logger.info(f"\n{'='*80}\nSYSTEM [TOOL OUTPUTS CREATED]:\n{content}\n{'='*80}")

    def _format_tool_outputs(self, tool_outputs: list[dict]) -> str:
        """
        Format tool outputs into a readable string.

        Args:
            tool_outputs: List of tool output dictionaries

        Returns:
            Formatted string, or empty string if no outputs
        """
        if not tool_outputs:
            return ""

        lines = [
            "TOOL OUTPUTS SUMMARY",
            "",
            "Below are all get_* tool calls made and their responses during this conversation.",
            "Use this information to validate user claims and policy requirements:",
            ""
        ]

        for output in tool_outputs:
            tool_name = output["tool_name"]
            arguments = output["arguments"]
            response = output["response"]
            turn = output["turn"]
            error = output.get("error", False)

            lines.append(f"[Turn {turn}] {tool_name}")
            lines.append("Arguments:")
            for key, value in arguments.items():
                lines.append(f"  {key}: {json.dumps(value)}")

            if error:
                lines.append("Response: ERROR")
            else:
                # Try to format response as JSON if possible, otherwise as string
                lines.append("Response:")
                try:
                    # If response is a JSON string, parse and format it
                    if response and response.strip().startswith('{'):
                        response_obj = json.loads(response)
                        formatted_response = json.dumps(response_obj, indent=2)
                        for line in formatted_response.split('\n'):
                            lines.append(f"  {line}")
                    else:
                        lines.append(f"  {response}")
                except (json.JSONDecodeError, TypeError):
                    lines.append(f"  {response}")

            lines.append("")  # Blank line between tool outputs

        return "\n".join(lines)

    def _create_tool_outputs_message(self, state: LLMAgentState) -> Optional[SystemMessage]:
        """
        Create a system message containing all tool outputs tracked so far.

        Args:
            state: Current agent state containing tool_outputs

        Returns:
            SystemMessage with formatted tool outputs, or None if no outputs tracked
        """
        if not state.tool_outputs:
            return None

        lines = [
            "TOOL OUTPUTS SUMMARY",
            "",
            "Below are all tool calls made and their responses during this conversation.",
            "Use this information to validate against policy requirements:",
            ""
        ]

        for output in state.tool_outputs:
            tool_name = output["tool_name"]
            arguments = output["arguments"]
            response = output["response"]
            turn = output["turn"]
            error = output.get("error", False)

            lines.append(f"[Turn {turn}] {tool_name}")
            lines.append("Arguments:")
            for key, value in arguments.items():
                lines.append(f"  {key}: {json.dumps(value)}")

            if error:
                lines.append("Response: ERROR")
            else:
                # Try to format response as JSON if possible, otherwise as string
                lines.append("Response:")
                try:
                    # If response is a JSON string, parse and format it
                    if response and response.strip().startswith('{'):
                        response_obj = json.loads(response)
                        formatted_response = json.dumps(response_obj, indent=2)
                        for line in formatted_response.split('\n'):
                            lines.append(f"  {line}")
                    else:
                        lines.append(f"  {response}")
                except (json.JSONDecodeError, TypeError):
                    lines.append(f"  {response}")

            lines.append("")  # Blank line between tool outputs

        content = "\n".join(lines)
        return SystemMessage(role="system", content=content)

    def _create_handbook_system_message(self, handbooks: List[str]) -> SystemMessage:
        """
        Create a system message containing the tool handbook(s).

        Args:
            handbooks: List of handbook content strings

        Returns:
            SystemMessage with formatted handbook content
        """
        # Add preamble to draw attention to reconsideration
        preamble = """
⚠️ ATTENTION: You just proposed a tool call. Before proceeding, carefully review the HANDBOOK below.

CRITICAL: Check the TOOL OUTPUTS SUMMARY (in system messages above) for actual data from get_* calls.
Use this data to verify user claims and validate against policy requirements.

You MUST reconsider your decision:
- Review Tool Outputs Summary: Does actual data from get_user_details, get_reservation_details, etc. contradict user claims?
- If Prerequisites are incomplete → ASK the user for missing information (do NOT call the tool yet)
- If Conditional Checks would fail based on actual tool output data → DO NOT call the tool (explain why or suggest alternatives)
- Only proceed with the tool call if ALL conditions are satisfied and data validates user claims

Review the handbook and decide your final action:
""".strip()

        if len(handbooks) == 1:
            content = f"{preamble}\n\n<tool_handbook>\n{handbooks[0]}\n</tool_handbook>"
        else:
            # Multiple handbooks - wrap each in its own tag
            parts = [preamble, ""]
            for i, handbook in enumerate(handbooks, 1):
                parts.append(f"<tool_handbook_{i}>\n{handbook}\n</tool_handbook_{i}>")
            content = "\n\n".join(parts)

        return SystemMessage(role="system", content=content)

    def _generate_with_handbook_injection(
        self,
        message: ValidAgentInputMessage,
        state: LLMAgentState,
        depth: int = 0,
    ) -> tuple[AssistantMessage, LLMAgentState]:
        """
        Generate response with recursive handbook injection.

        This implements the core injection algorithm:
        1. Generate initial response
        2. If tool call detected, rollback and inject handbook
        3. Regenerate with handbook
        4. Recursively inject if new tool call (up to max depth)

        Args:
            message: Input message from user or tool
            state: Current agent state
            depth: Current recursion depth

        Returns:
            Final assistant message and updated state
        """
        # Track tool outputs if incoming message contains them
        if isinstance(message, MultiToolMessage):
            self._track_tool_outputs(message.tool_messages, state)
            state.messages.extend(message.tool_messages)
        elif isinstance(message, ToolMessage):
            self._track_tool_outputs([message], state)
            state.messages.append(message)
        else:
            state.messages.append(message)

        # Generate initial response
        messages = state.system_messages + state.messages
        assistant_message = generate(
            model=self.llm,
            tools=self.tools,
            messages=messages,
            **self.llm_args,
        )

        # Check if this is a tool call
        if not assistant_message.is_tool_call():
            # No tool call - just return the message
            state.messages.append(assistant_message)
            logger.info(f"\n{'='*80}\nASSISTANT [No tool call - Depth {depth}]: {assistant_message.content}\n{'='*80}")
            return assistant_message, state

        # Tool call detected - check depth limit
        if depth >= self.max_injection_depth:
            logger.warning(
                f"Max injection depth ({self.max_injection_depth}) reached. "
                f"Proceeding with tool call without further injection."
            )
            state.messages.append(assistant_message)
            tool_calls_str = ", ".join([f"{tc.name}({tc.arguments})" for tc in assistant_message.tool_calls])
            logger.info(f"\n{'='*80}\nASSISTANT [Max depth reached - Depth {depth}]:\nContent: {assistant_message.content}\nTool Calls: {tool_calls_str}\n{'='*80}")
            return assistant_message, state

        # Step 2: Roll back - don't add the assistant message to state yet
        # Step 3: Inject handbook for the proposed tool(s)
        tool_names = [tc.name for tc in assistant_message.tool_calls]
        # Deduplicate tool names to avoid adding the same handbook multiple times
        unique_tool_names = list(dict.fromkeys(tool_names))  # Preserves order

        # Filter out 'get' tools - they don't need handbook injection
        tools_needing_injection = [name for name in unique_tool_names if not name.startswith('get_')]
        skipped_tools = [name for name in unique_tool_names if name.startswith('get_')]

        if skipped_tools:
            logger.info(f"Skipping handbook injection for 'get' tools: {skipped_tools}")

        if not tools_needing_injection:
            # All tools are 'get' tools - no injection needed
            logger.info(f"All tool calls are 'get' tools: {tool_names}. Skipping handbook injection.")
            state.messages.append(assistant_message)
            tool_calls_str = ", ".join([f"{tc.name}({tc.arguments})" for tc in assistant_message.tool_calls])
            logger.info(f"\n{'='*80}\nASSISTANT [Get tools only - Depth {depth}]:\nContent: {assistant_message.content}\nTool Calls: {tool_calls_str}\n{'='*80}")
            return assistant_message, state

        # Get handbooks for tools that need injection
        handbooks = []
        for tool_name in tools_needing_injection:
            handbook = self._get_handbook_for_tool(tool_name)
            if handbook:
                handbooks.append(handbook)

        if not handbooks:
            # No handbooks available - proceed without injection
            logger.warning("No handbooks available for proposed tools. Proceeding without injection.")
            state.messages.append(assistant_message)
            return assistant_message, state

        # Create handbook system message
        handbook_message = self._create_handbook_system_message(handbooks)

        # Step 4: Regenerate with handbook injected
        # Note: Tool outputs are already in state.system_messages as a persistent message
        injection_messages = [handbook_message]

        # Log the injection
        logger.info(f"\n{'='*80}\nSYSTEM [INJECTION - Depth {depth}]:")
        logger.info(f"--- HANDBOOK ---\n{handbook_message.content}\n{'='*80}")

        # Tool outputs are already in state.system_messages, just add handbook
        messages_with_injection = state.system_messages + injection_messages + state.messages
        regenerated_message = generate(
            model=self.llm,
            tools=self.tools,
            messages=messages_with_injection,
            **self.llm_args,
        )

        # Check if the regenerated message is also a tool call
        if regenerated_message.is_tool_call():
            # Get new tool names
            new_tool_names = [tc.name for tc in regenerated_message.tool_calls]

            # If different tools are proposed, recursively inject
            if set(new_tool_names) != set(tool_names):
                logger.info(f"\nTool change detected! Original: {tool_names} -> New: {new_tool_names}. Recursively injecting at depth {depth + 1}...\n")
                # Remove the incoming message we added earlier
                if isinstance(message, MultiToolMessage):
                    state.messages = state.messages[:-len(message.tool_messages)]
                else:
                    state.messages = state.messages[:-1]

                # Recursively inject with the original message
                return self._generate_with_handbook_injection(message, state, depth + 1)

        # Add final message to state and return
        state.messages.append(regenerated_message)

        # Log final assistant response
        if regenerated_message.is_tool_call():
            tool_calls_str = ", ".join([f"{tc.name}({tc.arguments})" for tc in regenerated_message.tool_calls])
            logger.info(f"\n{'='*80}\nASSISTANT [FINAL - Depth {depth}]:\nContent: {regenerated_message.content}\nTool Calls: {tool_calls_str}\n{'='*80}")
        else:
            logger.info(f"\n{'='*80}\nASSISTANT [FINAL - Depth {depth}]: {regenerated_message.content}\n{'='*80}")

        return regenerated_message, state

    def generate_next_message(
        self, message: ValidAgentInputMessage, state: LLMAgentState
    ) -> tuple[AssistantMessage, LLMAgentState]:
        """
        Generate the next message with handbook injection.

        This overrides the parent method to implement the inference-time
        injection mechanism.

        Args:
            message: Input message from user or tool
            state: Current agent state

        Returns:
            Assistant message and updated state
        """
        # Log incoming message
        if isinstance(message, UserMessage):
            logger.info(f"\n{'='*80}\nUSER: {message.content}\n{'='*80}")
        elif isinstance(message, ToolMessage):
            logger.info(f"\n{'='*80}\nTOOL RESPONSE [{message.id}]: {message.content}\n{'='*80}")
        elif isinstance(message, MultiToolMessage):
            logger.info(f"\n{'='*80}\nMULTIPLE TOOL RESPONSES ({len(message.tool_messages)} tools)\n{'='*80}")
            for tm in message.tool_messages:
                logger.info(f"  [{tm.id}]: {tm.content}")

        return self._generate_with_handbook_injection(message, state, depth=0)
