from dotenv import load_dotenv
# from typing import Annotated, Literal
# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
# from langchain.chat_models import init_chat_model
# from pydantic import BaseModel, Field
# from typing_extensions import TypedDict
from app.graph import build_graph

load_dotenv()

graph = build_graph()

# Initialize the chat model used by the application
# llm = init_chat_model(model="gpt-4o-mini")


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
