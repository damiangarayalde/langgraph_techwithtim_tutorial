from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from prompt_toolkit import prompt
from app.types import ChatState


def make_route_subgraph(route_id: str) -> StateGraph:
    """Construct a StateGraph subgraph for a given route.

    Parameters:
    - route_id (str): Key used to lookup route configuration in
        `config/routes.yaml` and to locate route-specific indexes/prompts.

    Returns:
    - A compiled `StateGraph` ready to be invoked by the application.
    """

    # Load the route-specific prompt and configuration values

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

    def generate(state: ChatState) -> ChatState:
        """Generate an answer using the LLM.
        """

        # Handle technical support inquiries by forwarding the user's message to LLM
        user_text = state["messages"][-1]
        print(f"Invoking node for handling route: {route_id}...")

        message = [
            {"role": "system",
                "content": f"Eres un agente que responde consultas de {route_id}."},
            {"role": "user", "content": user_text.content}
        ]
        reply = llm.invoke(message)
        # Return the assistant reply wrapped in the state's messages field
        return {"messages": [reply]}

    g = StateGraph(ChatState)
    g.add_node("generate", generate)
    g.add_edge(START, "generate")
    g.add_edge("generate", END)
    return g.compile()
