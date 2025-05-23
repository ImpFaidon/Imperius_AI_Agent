# main.py
from typing import TypedDict 
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from tools import create_asana_task, ASANA_WORKSPACE_GID, ASANA_PROJECT_GID, DEFAULT_ASSIGNEE_GIDS

# Define your LLM (make sure Ollama server is running with llama3.2 model)
llm = OllamaLLM(model="ilsp/meltemi-instruct-v1.5")

# Define the brief refinement chain
refinement_prompt_template = """
Μετάτρεψε την παρακάτω "Αρχική Περιγραφή" σε μια σαφή και επαγγελματική "Επεξεργασμένη Περιγραφή Εργασίας" κατάλληλη για το Asana.
Η απάντησή σου πρέπει να περιέχει ΜΟΝΟ την επεξεργασμένη περιγραφή εργασίας.

Αρχική Περιγραφή:
{raw_brief}

Επεξεργασμένη Περιγραφή Εργασίας:
"""
refinement_prompt = ChatPromptTemplate.from_template(refinement_prompt_template)
refinement_chain = refinement_prompt | llm

# Define a simple state for LangGraph
class AgentState(TypedDict): 
    refined_brief: str
    asana_task_result: dict

# Define the nodes of the LangGraph
def refine_brief_node(state: AgentState):
    raw_brief = state["raw_brief"] # Access via dictionary key if TypedDict
    refined_brief = refinement_chain.invoke({"raw_brief": raw_brief})
    print(f"\n--- Επεξεργασμένη Περιγραφή (Refined Brief) ---\n{refined_brief}\n--------------------")
    return {"refined_brief": refined_brief}

def create_asana_task_node(state: AgentState):
    refined_brief = state["refined_brief"] # Access via dictionary key if TypedDict
    if not refined_brief:
        return {"asana_task_result": {"status": "error", "message": "Λείπει η επεξεργασμένη περιγραφή."}}

    task_name = refined_brief.split('\n')[0][:250]
    task_notes = refined_brief

    result = create_asana_task.invoke({"task_name": task_name, "task_notes": task_notes, "assignees_gids": DEFAULT_ASSIGNEE_GIDS})
    print(f"\n--- Αποτέλεσμα Δημιουργίας Εργασίας Asana ---\n{result}\n--------------------")
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
    # 3. Translated UI messages
    print("Έναρξη Agent Δημιουργίας Task στο Asana (q για έξοδο)")
    print("--------------------------------------")

    while True:
        brief_input = input("\nΕισαγάγετε μια περιγραφή για μια νέα εργασία Asana (πληκτρολογήστε 'q' για έξοδο): ")
        if brief_input.lower() == 'q':
            break

        # Pass the initial state as a dictionary
        initial_state = {"raw_brief": brief_input, "refined_brief": "", "asana_task_result": {}} # Initialize all keys, even if empty
        final_state = app.invoke(initial_state)
        print(f"\n--- Τελική Κατάσταση ---\n{final_state}\n--------------------")