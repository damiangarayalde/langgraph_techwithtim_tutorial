from langgraph.graph import StateGraph, START, END
from app.types import ChatState
from app.nodes import (
    node__classify_user_intent,
    node__sales_agent,
    node__techsupport_agent,
    node__route_by_user_intent,
)


def build_graph() -> StateGraph:

    # Create the state graph that models the conversation flow
    g = StateGraph(ChatState)

    # Add processing nodes to the graph
    g.add_node("classify_user_intent", node__classify_user_intent)
    g.add_node("ventas__agent", node__sales_agent)
    g.add_node("soporte__agent", node__techsupport_agent)
    g.add_node("route_by_user_intent", node__route_by_user_intent)

    # -------------------------------------------
    # Example: scalable product-based routing
    # In a real project `subgraphs` would map product ids to either
    # node callables or compiled StateGraph objects for each product.
    # Here we create simple placeholder handlers to demonstrate wiring.
    # subgraphs: dict[str, callable] = {}

    # def make_support_node(pid: str):
    #     def _node(state: ChatState) -> ChatState:
    #         return {"messages": [{"role": "assistant", "content": f"Handled support for product {pid}."}]}
    #     return _node

    # # Register a couple of example product handlers (alpha, beta)
    # for pid in ("alpha", "beta"):
    #     subgraphs[pid] = make_support_node(pid)
    #     g.add_node(f"support__{pid}", subgraphs[pid])

    # # Add a fallback handler for unknown products
    # def support_unknown(state: ChatState) -> ChatState:
    #     return {"messages": [{"role": "assistant", "content": "Lo siento, no encuentro ese producto."}]}

    # g.add_node("support__unknown", support_unknown)

    # # Router node: returns the node-key string that identifies the chosen support node
    # def route_by_product(state: ChatState) -> str:
    #     pf = state.get("product_family") or "unknown"
    #     return f"support__{pf}" if pf in subgraphs else "support__unknown"

    # g.add_node("route_by_product", route_by_product)

    # # Build conditional edge map: router-returned key -> node name
    # edge_map = {f"support__{pid}": f"support__{pid}" for pid in subgraphs.keys()}
    # edge_map["support__unknown"] = "support__unknown"

    # # Wire the router into the flow (from intent classifier to product router)
    # g.add_edge("classify_user_intent", "route_by_product")
    # g.add_conditional_edges("route_by_product", route_by_product, edge_map)

    # # Ensure all product support nodes flow to the END
    # for pid in subgraphs.keys():
    #     g.add_edge(f"support__{pid}", END)
    # g.add_edge("support__unknown", END)

    # -------------------------------------------

    # Connect the nodes: start -> classify_user_intent -> route_by_user_intent -> (sales|support) -> end
    g.add_edge(START, "classify_user_intent")
    g.add_edge("classify_user_intent", "route_by_user_intent")
    g.add_conditional_edges(
        "route_by_user_intent",
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
