from dotenv import load_dotenv
from typing import Literal
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from app.types import ChatState
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Initialize the chat model used by the application
llm = init_chat_model(model="gpt-4o-mini")


class UserIntentClassifier_output_format(BaseModel):
    # Structured output model used to enforce the classifier's response shape
    handling_channel: Literal["sales", "support"] = Field(
        ...,
        description="Clasifica el tipo de mensaje como 'ventas' o 'soporte'.",
    )


classifier_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a router for a WhatsApp bot. Classify the user's message.\n"
     "- handling_channel: 'sales' if the user asks about price, availability, buying, shipping, discounts, compatibility to purchase.\n"
     "- handling_channel: 'support' if the user reports a problem, installation issue, error, warranty, troubleshooting.\n"
     "Also choose product_family from the allowed list. If uncertain, pick the closest and lower confidence."),
    ("human", "{message}")
])


# Node implementations --------------------------------------------------------------------------------------------------------------


def node__classify_user_intent(state: ChatState) -> ChatState:

    # Use the last user message to classify whether its intent requires a sales or support request
    last_message = state["messages"][-1].content

    # Create an LLM call that produces structured output matching MessageClassifier
    classifier_llm = llm.with_structured_output(
        UserIntentClassifier_output_format)
    messages = classifier_prompt.format_messages(message=last_message)

    print("Invoking classify_user_intent_node...")
    result = classifier_llm.invoke(messages)

    # Return the handling_channel so downstream nodes can route appropriately
    return {
        "handling_channel": result.handling_channel
    }


def node__route_by_user_intent(state: ChatState) -> ChatState:
    # Router node: returns the node-key string that identifies the chosen channel agent node (sales or support)

    pf = state.get("handling_channel") or "unknown"
    print(f'Routing based on handling_channel in state: {pf}')

    # Update the state with the chosen next node key so the conditional
    # edges selector can read it. Must return a dict (state update).
    chosen = f"handle__{pf}"  # if pf in subgraphs else "handle__unknown"
    return {"next": chosen}
