from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

load_dotenv()

# Initialize the chat model used by the application
llm = init_chat_model(model="gpt-4o-mini")


class MessageClassifier(BaseModel):
    # Structured output model used to enforce the classifier's response shape
    message_type: Literal["ventas", "soporte"] = Field(
        ...,
        description="Clasifica el tipo de mensaje como 'ventas' o 'soporte'.",
    )


class State(TypedDict):
    # The graph state holds the conversation messages and optional metadata
    messages: Annotated[list, add_messages]
    message_type: str | None


def classify_message(state: State) -> State:
    # Use the last user message to determine whether it's a sales or support request
    last_message = state["messages"][-1]
    # Create an LLM call that produces structured output matching MessageClassifier
    classifier_llm = llm.with_structured_output(MessageClassifier)

    result = classifier_llm.invoke([
        {"role": "system", "content": "Eres un clasificador de mensajes. Clasifica el siguiente mensaje como 'ventas' o 'soporte'."},
        {"role": "user", "content": last_message.content}
    ])

    # Return the message_type so downstream nodes can route appropriately
    return {"message_type": result.message_type}


def techsupport_agent(state: State) -> State:
    # Handle technical support inquiries by forwarding the user's message to LLM
    last_message = state["messages"][-1]
    message = [
        {"role": "system", "content": "Eres un agente de soporte técnico. Ayuda al usuario con sus problemas técnicos."},
        {"role": "user", "content": last_message.content}
    ]
    reply = llm.invoke(message)
    # Return the assistant reply wrapped in the state's messages field
    return {"messages": [reply]}


def sales_agent(state: State) -> State:
    # Handle sales-related messages
    last_message = state["messages"][-1]
    message = [
        {"role": "system", "content": "Eres un agente de ventas. Ayuda al usuario con sus preguntas sobre productos y servicios."},
        {"role": "user", "content": last_message.content}
    ]
    reply = llm.invoke(message)
    return {"messages": [reply]}


def router(state: State) -> State:
    # Decide which agent node to invoke next based on classifier output
    message_type = state.get("message_type", "soporte")
    if message_type == "ventas":
        return {"next": "ventas__agent"}
    else:
        return {"next": "soporte__agent"}


# Create the state graph that models the conversation flow
graph_builder = StateGraph(State)

# Add processing nodes to the graph
graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("ventas__agent_nodename", sales_agent)
graph_builder.add_node("soporte__agent_nodename", techsupport_agent)
graph_builder.add_node("router", router)

# Connect the nodes: start -> classifier -> router -> (sales|support) -> end
graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")
graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {
        "ventas__agent": "ventas__agent_nodename",
        "soporte__agent": "soporte__agent_nodename",
    },
)

graph_builder.add_edge("ventas__agent_nodename", END)
graph_builder.add_edge("soporte__agent_nodename", END)

# Compile the graph into an executable object
graph = graph_builder.compile()


def run_chatbot():
    state = {"messages": [], "message_type": None}
    # Main REPL loop: accept user input, run through the graph, and print replies
    while True:
        user_input = input("Message: ")
        if user_input == "exit":
            print("Bye")
            break

        # Append the user's message to the conversation state
        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]

        # Invoke the compiled graph to process the state and produce a response
        state = graph.invoke(state)

        # If the graph returned messages, display the last assistant reply
        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Assistant: {last_message.content}")


if __name__ == "__main__":
    run_chatbot()
