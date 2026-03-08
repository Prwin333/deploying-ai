"""
Chef Byte  - An AI Chef Assistant
Main application entry point with Gradio chat interface.

Usage:
    cd 05_src/assignment2_chat
    python app.py
"""

import sys
import os

# Ensure the assignment2_chat directory is on the path
sys.path.insert(0, os.path.dirname(__file__))

import gradio as gr
from chat.interface import generate_response, reset_conversation
from utils.helpers import check_environment, check_knowledge_base


def chat_fn(message: str, history: list) -> str:
    """Gradio chat function."""
    return generate_response(message)


def main():
    # Startup checks
    print("=" * 50)
    print("Chef Byte  - Starting up!")
    print("=" * 50)

    for check in check_environment():
        print(check)
    print(check_knowledge_base())
    print("=" * 50)

    # Build Gradio interface
    with gr.Blocks(
        title="Chef Byte",
        theme=gr.themes.Soft(
            primary_hue="orange",
            secondary_hue="amber",
        ),
    ) as demo:
        gr.Markdown(
            """
            # Chef Byte  - Your AI Chef Assistant

            *Buongiorno, amico!* I'm **Chef Byte**, your passionate AI cooking companion!
            I can help you with:

            - **Recipe Search** - Find recipes by name or ingredient
            - **Food Knowledge** - Ask about nutrition, cooking techniques, and food science
            - **Web Search** - Get the latest food trends and restaurant recommendations

            *Let's cook up something amazing together!*
            """
        )

        chatbot = gr.ChatInterface(
            fn=chat_fn,
            type="messages",
            chatbot=gr.Chatbot(
                height=500,
                placeholder="Ask Chef Byte anything about food, recipes, or cooking!",
                type="messages",
            ),
            textbox=gr.Textbox(
                placeholder="Type your message here... (e.g., 'Find me a pasta recipe' or 'What is umami?')",
                container=False,
                scale=7,
            ),
            title=None,
        )

        gr.Markdown(
            """
            ---
            *Chef Byte is an AI assistant and may occasionally make mistakes.
            Always verify cooking temperatures and food safety information from official sources.*
            """
        )

    demo.launch(share=False)


if __name__ == "__main__":
    main()