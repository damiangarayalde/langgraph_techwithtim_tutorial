from typing import TypedDict, List
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class ChatState(TypedDict):
    """Shared TypedDict describing the shape of the chat/graph state.

    This centralizes the state type so modules can import it without
    creating circular imports between node implementations and the main
    graph builder.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    handling_channel:  str | None
