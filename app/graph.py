from langgraph.graph import StateGraph, START, END
from app.types import ChatState
from app.nodes import (
    classify_message_node,
    sales_agent_node,
    techsupport_agent_node,
    router_node,
)


def build_graph() -> StateGraph:

    # Create the state graph that models the conversation flow
    g = StateGraph(ChatState)

    # Add processing nodes to the graph
    g.add_node("classifier", classify_message_node)
    g.add_node("ventas__agent_nodename", sales_agent_node)
    g.add_node("soporte__agent_nodename", techsupport_agent_node)
    g.add_node("router", router_node)

    # Connect the nodes: start -> classifier -> router -> (sales|support) -> end
    g.add_edge(START, "classifier")
    g.add_edge("classifier", "router")
    g.add_conditional_edges(
        "router",
        lambda state: state.get("next"),
        {
            "ventas__agent": "ventas__agent_nodename",
            "soporte__agent": "soporte__agent_nodename",
        },
    )

    g.add_edge("ventas__agent_nodename", END)
    g.add_edge("soporte__agent_nodename", END)

    # Compile the graph into an executable object and return it
    return g.compile()
