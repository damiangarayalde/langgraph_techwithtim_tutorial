from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from app.types import ChatState

load_dotenv()

# Initialize the chat model used by the application
llm = init_chat_model(model="gpt-4o-mini")


class UserIntentClassifier_output_format(BaseModel):
    # Structured output model used to enforce the classifier's response shape
    handling_channel: Literal["sales", "support"] = Field(
        ...,
        description="Clasifica el tipo de mensaje como 'ventas' o 'soporte'.",
    )
    product_family: Literal["TPMS", "AA", "CLIMATIZADOR",
                            "GENKI", "CARJACK", "MAYORISTA", "CALDERA", "UNKNOWN"]
    confidence: float


# Node implementations --------------------------------------------------------------------------------------------------------------


def node__classify_user_intent(state: ChatState) -> ChatState:

    # Use the last user message to classify whether its intent requires a sales or support request
    last_message = state["messages"][-1]

    # Create an LLM call that produces structured output matching MessageClassifier
    classifier_llm = llm.with_structured_output(
        UserIntentClassifier_output_format)

    message = [
        {"role": "system", "content": "Eres un clasificador de mensajes. Clasifica el siguiente mensaje como 'ventas' o 'soporte'."},
        {"role": "user", "content": last_message.content}
    ]
    print("Invoking classify_user_intent_node...")
    result = classifier_llm.invoke(message)

    # Return the handling_channel so downstream nodes can route appropriately
    return {
        "handling_channel": result.handling_channel,
        "product_family": result.product_family,
        "confidence": result.confidence
    }

# Router node: returns the node-key string that identifies the chosen channel agent node (sales or support)


def node__route_by_user_intent(state: ChatState) -> ChatState:
    pf = state.get("handling_channel") or "unknown"
    print(f'Routing based on handling_channel in state: {pf}')

    # Update the state with the chosen next node key so the conditional
    # edges selector can read it. Must return a dict (state update).
    chosen = f"handle__{pf}"  # if pf in subgraphs else "handle__unknown"
    return {"next": chosen}

# def node__techsupport_agent(state: ChatState) -> ChatState:
#     # Handle technical support inquiries by forwarding the user's message to LLM
#     last_message = state["messages"][-1]
#     message = [
#         {"role": "system", "content": "Eres un agente de soporte técnico. Ayuda al usuario con sus problemas técnicos."},
#         {"role": "user", "content": last_message.content}
#     ]
#     print("Invoking techsupport_agent_node...")
#     reply = llm.invoke(message)
#     # Return the assistant reply wrapped in the state's messages field
#     return {"messages": [reply]}


# def node__sales_agent(state: ChatState) -> ChatState:
#     # Handle sales-related messages
#     last_message = state["messages"][-1]
#     message = [
#         {"role": "system", "content": "Eres un agente de ventas. Ayuda al usuario con sus preguntas sobre productos y servicios."},
#         {"role": "user", "content": last_message.content}
#     ]
#     print("Invoking sales_agent_node...")
#     reply = llm.invoke(message)
#     return {"messages": [reply]}
