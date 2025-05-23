# main.py
from typing import TypedDict 
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
# Assuming tools.py contains your create_asana_task tool
from tools import create_asana_task, ASANA_WORKSPACE_GID, ASANA_PROJECT_GID, DEFAULT_ASSIGNEE_GIDS

# Define your LLM (make sure Ollama server is running with llama3.2 model)
llm = OllamaLLM(model="llama3.2")

# Define the brief refinement chain
refinement_prompt_template = """
You are an expert project manager. Your task is to take a raw, informal brief and refine it into a clear, professional, and actionable task description suitable for an Asana task.

Focus on:
- Clarity and conciseness.
- Professional tone.
- Including all essential information from the original brief.
- Avoiding informal language or slang.
- Formatting it as a straightforward text description.

Original Brief:
{raw_brief}

Refined Task Description:
"""
refinement_prompt = ChatPromptTemplate.from_template(refinement_prompt_template)
refinement_chain = refinement_prompt | llm

# Define a simple state for LangGraph
class AgentState(TypedDict): # <--- CHANGE THIS LINE TO INHERIT FROM TypedDict
    raw_brief: str
    refined_brief: str
    asana_task_result: dict

# Define the nodes of the LangGraph
def refine_brief_node(state: AgentState):
    raw_brief = state["raw_brief"] # Access via dictionary key if TypedDict
    refined_brief = refinement_chain.invoke({"raw_brief": raw_brief})
    print(f"\n--- Refined Brief ---\n{refined_brief}\n--------------------")
    return {"refined_brief": refined_brief}

def create_asana_task_node(state: AgentState):
    refined_brief = state["refined_brief"] # Access via dictionary key if TypedDict
    if not refined_brief:
        return {"asana_task_result": {"status": "error", "message": "Refined brief missing."}}

    task_name = refined_brief.split('\n')[0][:250]
    task_notes = refined_brief

    result = create_asana_task.invoke({"task_name": task_name, "task_notes": task_notes, "assignees_gids": DEFAULT_ASSIGNEE_GIDS})
    print(f"\n--- Asana Task Creation Result ---\n{result}\n--------------------")
    return {"asana_task_result": result}

# Build the LangGraph
builder = StateGraph(AgentState)

builder.add_node("refine_brief", refine_brief_node)
builder.add_node("create_asana_task", create_asana_task_node)

builder.set_entry_point("refine_brief")
builder.add_edge("refine_brief", "create_asana_task")
builder.add_edge("create_asana_task", END)

app = builder.compile()

# Simple test execution (for command line testing)
if __name__ == "__main__":
    print("\n--------------------------------------")
    print("Starting Asana Task Creation Agent (q to quit)")
    print("--------------------------------------")

    while True:
        brief_input = input("\nEnter a brief for a new Asana task: ")
        if brief_input.lower() == 'q':
            break

        # Pass the initial state as a dictionary
        initial_state = {"raw_brief": brief_input, "refined_brief": "", "asana_task_result": {}} # Initialize all keys, even if empty
        final_state = app.invoke(initial_state)
        print(f"\n--- Final State ---\n{final_state}\n--------------------")