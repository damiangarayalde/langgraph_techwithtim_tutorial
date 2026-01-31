from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage
from typing import Annotated, Literal
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    """Shared TypedDict describing the shape of the chat/graph state.

    This centralizes the state type so modules can import it without
    creating circular imports between node implementations and the main
    graph builder.
    """
    messages: Annotated[list,
                        add_messages]  # in new its used: List[BaseMessage]
    route:  str | None
    attempts: Dict[str, int]
    retrieved: Optional[List[Dict[str, Any]]]
    answer:  str | None
    message_type:  str | None
