from typing import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    """Shared TypedDict describing the shape of the chat/graph state.

    This centralizes the state type so modules can import it without
    creating circular imports between node implementations and the main
    graph builder.
    """
    messages: Annotated[list,
                        add_messages]  # in new its used: List[BaseMessage]
    handling_channel:  str | None
