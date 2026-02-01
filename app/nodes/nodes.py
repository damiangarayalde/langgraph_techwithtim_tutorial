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


class MessageClassifier_output_format(BaseModel):
    # Structured output model used to enforce the classifier's response shape
    message_type: Literal["ventas", "soporte"] = Field(
        ...,
        description="Clasifica el tipo de mensaje como 'ventas' o 'soporte'.",
    )

# Node implementations --------------------------------------------------------------------------------------------------------------


def node__determine_user_intent(state: ChatState) -> ChatState:

    # Use the last user message to determine whether it's a sales or support request
    last_message = state["messages"][-1]

    # Create an LLM call that produces structured output matching MessageClassifier
    classifier_llm = llm.with_structured_output(
        MessageClassifier_output_format)

    message = [
        {"role": "system", "content": "Eres un clasificador de mensajes. Clasifica el siguiente mensaje como 'ventas' o 'soporte'."},
        {"role": "user", "content": last_message.content}
    ]
    print("Invoking determine_contact_reason_node...")
    result = classifier_llm.invoke(message)

    # Return the message_type so downstream nodes can route appropriately
    return {"message_type": result.message_type}


def node__techsupport_agent(state: ChatState) -> ChatState:
    # Handle technical support inquiries by forwarding the user's message to LLM
    last_message = state["messages"][-1]
    message = [
        {"role": "system", "content": "Eres un agente de soporte técnico. Ayuda al usuario con sus problemas técnicos."},
        {"role": "user", "content": last_message.content}
    ]
    print("Invoking techsupport_agent_node...")
    reply = llm.invoke(message)
    # Return the assistant reply wrapped in the state's messages field
    return {"messages": [reply]}


def node__sales_agent(state: ChatState) -> ChatState:
    # Handle sales-related messages
    last_message = state["messages"][-1]
    message = [
        {"role": "system", "content": "Eres un agente de ventas. Ayuda al usuario con sus preguntas sobre productos y servicios."},
        {"role": "user", "content": last_message.content}
    ]
    print("Invoking sales_agent_node...")
    reply = llm.invoke(message)
    return {"messages": [reply]}


def node__handle_user_intent(state: ChatState) -> ChatState:
    # Decide which agent node to invoke next based on classifier output
    message_type = state.get("message_type", "soporte")
    if message_type == "ventas":
        return {"next": "ventas__agent"}
    else:
        return {"next": "soporte__agent"}
