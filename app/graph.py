from langgraph.graph import StateGraph, START, END
from app.types import ChatState
from app.nodes import (
    node__determine_user_intent,
    node__sales_agent,
    node__techsupport_agent,
    node__handle_user_intent,
)


def build_graph() -> StateGraph:

    # Create the state graph that models the conversation flow
    g = StateGraph(ChatState)

    # Add processing nodes to the graph
    g.add_node("determine_user_intent", node__determine_user_intent)
    g.add_node("ventas__agent", node__sales_agent)
    g.add_node("soporte__agent", node__techsupport_agent)
    g.add_node("handle_user_intent", node__handle_user_intent)

    # Connect the nodes: start -> determine_intent -> handle_user_intent -> (sales|support) -> end
    g.add_edge(START, "determine_user_intent")
    g.add_edge("determine_user_intent", "handle_user_intent")
    g.add_conditional_edges(
        "handle_user_intent",
        lambda state: state.get("next"),
        {
            "ventas__agent": "ventas__agent",
            "soporte__agent": "soporte__agent",
        },
    )
    g.add_edge("ventas__agent", END)
    g.add_edge("soporte__agent", END)

    # Compile the graph into an executable object and return it
    return g.compile()
