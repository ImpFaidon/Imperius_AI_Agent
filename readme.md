# AI Account Manager Agent

![AI Account Manager Agent Workflow Diagram](images/workflow_diagram.jpg)

## Table of Contents

- [Introduction](#introduction)
- [Problem Solved](#problem-solved)
- [Core Concept &amp; Architecture](#core-concept--architecture)
- [Key Features](#key-features)
  - [Currently Implemented](#currently-implemented)
  - [Planned Future Features](#planned-future-features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration (.env Setup)](#configuration-env-setup)
  - [Running the Agent Locally](#running-the-agent-locally)
- [Project Structure](#project-structure)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This project aims to develop an intelligent AI agent designed to streamline and automate routine account management tasks. By integrating cutting-edge AI orchestration with external service APIs, the agent processes incoming communications, understands requests, makes decisions, and performs actions, significantly enhancing efficiency and responsiveness.

## Problem Solved

Traditional account management often involves repetitive, time-consuming tasks such as:

* Manually creating tasks from emails or brief notes.
* Fragmented communication and task assignment across different platforms.
* Lack of automated context retrieval for quick answers.

This AI agent addresses these challenges by automating the initial steps of processing communication, refining requests, and orchestrating task creation and follow-ups.

## Core Concept & Architecture

The agent is built upon an **"AI Decides & Executes"** architectural pattern, where the AI core not only understands user intent but also directly controls the execution of actions through integrated tools.

* **Event Triggering (n8n):** External events (e.g., new emails, Asana comments, Google Calendar responses) are detected by **n8n**, which acts as an initial integration layer.
* **API Entry Point (Flask REST API):** `n8n` forwards event data (via a POST request) to a dedicated **Flask REST API endpoint**, which serves as the entry point for the AI agent.
* **AI Agent Core & Orchestration (LangGraph):** The core intelligence is powered by **LangGraph** (an open-source AI-Agent framework). It manages the entire workflow as a graph, defining specific steps and transitions. An **LLM** (e.g., Ollama's Llama 3/Meltemi, or Deepseek R1 API) is integrated within LangGraph for tasks like brief refinement and future intent classification.
* **Tool Interaction (Model Context Protocol - MCP Concept):** The AI agent directly interacts with external services (Asana, Google Calendar, Gmail, RAG database) by calling **Tools**. The concept of **Model Context Protocol (MCP)** is adopted to standardize how the AI interacts with these tools, enhancing modularity and scalability.
* **Retrieval Augmented Generation (RAG):** A RAG system provides context-aware answers by retrieving relevant information from a company knowledge base (e.g., `imperius_agent_knowledge.csv`) when needed.
* **Human-in-the-Loop:** An optional human review path is integrated for complex or ambiguous cases, ensuring oversight.

## Key Features

### Currently Implemented

* **Automated Asana Task Creation:** Creates new tasks in Asana based on incoming text briefs.
* **LLM-Powered Brief Refinement:** Takes raw, informal text briefs and refines them into clear, professional, and actionable task descriptions suitable for Asana.
* **Configurable Task Attributes:** Supports setting the task name, notes, primary assignee, due date, additional followers (collaborators), and tags directly through configuration.
* **Name-to-GID Resolution:** Resolves human-readable follower names to their corresponding Asana GIDs using a configurable map.

### Planned Future Features

* **Dynamic Intent Classification:** Automatically classify incoming communications (email, Asana comment, calendar response) to determine the user's intent (e.g., "Answer Question," "Create Task," "Schedule Meeting").
* **Context-Aware Answering (RAG):** Integrate the RAG system to provide answers to questions based on company knowledge.
* **Google Calendar Integration:** Automate scheduling meetings, checking availability, and sending invitations.
* **Gmail Integration:** Automate sending context-aware replies to incoming emails.
* **Advanced Task Management:** Implement creation of subtasks, adding attachments (e.g., Dropbox links), and dynamic management of task priority (via custom fields).
* **Full Multilingual Support:** Optimize the agent's performance for Greek language processing (e.g., evaluating Meltemi models, fine-tuning).
* **Enhanced Error Handling & Robustness:** Implement sophisticated error recovery, logging, and monitoring.
* **Proactive Agent Capabilities:** Explore having the agent initiate actions based on monitoring data rather than just reacting to triggers.

## Getting Started

Follow these steps to set up and run the AI Account Manager Agent locally.

### Prerequisites

* **Python 3.11+**
* **Ollama:** For running local LLMs (like `llama3.2` or Meltemi). Download from [ollama.ai](https://ollama.ai/).
* **n8n:** A running instance of n8n (cloud or self-hosted) to set up triggers. Download from [n8n.io](https://n8n.io/).
* **Asana Account:** With API access (Personal Access Token).
* **Google Account (Gmail/Calendar):** For future integration, with API access enabled.

### Installation

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
   cd your-repo-name
   ```

   (Remember to replace `your-username/your-repo-name` with your actual repository details.)
2. **Create a virtual environment:**

   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```
3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   (You'll need to create a `requirements.txt` file in your root directory containing all the dependencies we used, e.g., `flask`, `langchain`, `langgraph`, `langchain-core`, `langchain-chroma`, `langchain-ollama`, `pandas`, `python-dotenv`, `asana`).

   ```bash
   # Example requirements.txt content:
   flask
   langchain
   langgraph
   langchain-core
   langchain-chroma
   langchain-ollama
   pandas
   python-dotenv
   asana
   ```
4. **Download Ollama Model:**
   Download the LLM you intend to use (e.g., `llama3.2`) via Ollama:

   ```bash
   ollama pull llama3.2
   # Or for Meltemi (if available and preferred):
   # ollama pull ilsp/meltemi-instruct-v1.5
   ```

   Ensure your Ollama server is running.

### Configuration (.env Setup)

Create a `.env` file in the root directory of your project (where `main.py` is located) and populate it with your API keys and GIDs:

```dotenv
# Asana API Token (from Asana My Settings -> Apps -> Personal Access Tokens)
ASANA_ACCESS_TOKEN="your_asana_personal_access_token_here"

# Asana Workspace GID (found in your Asana URL: [app.asana.com/0/YOUR_WORKSPACE_GID/](https://app.asana.com/0/YOUR_WORKSPACE_GID/)...)
ASANA_WORKSPACE_GID="your_asana_workspace_gid_here"

# Asana Project GID (found in your Asana URL: .../project/YOUR_PROJECT_GID/...)
ASANA_PROJECT_GID="your_asana_project_gid_here"

# Default Assignee GIDs (comma-separated list of Asana User GIDs for default task assignment)
# You can find your user GID in your Asana profile URL or via Asana API Explorer.
DEFAULT_ASSIGNEE_GIDS="YOUR_DEFAULT_USER_GID_1,YOUR_DEFAULT_USER_GID_2"

# Default Tag GIDs (comma-separated list of Asana Tag GIDs for default task tags)
# Create tags in Asana and get their GIDs from their URL or API Explorer.
DEFAULT_TAG_GIDS="YOUR_DEFAULT_TAG_GID_1,YOUR_DEFAULT_TAG_GID_2"

# Default Follower GIDs (comma-separated list of Asana User GIDs for default task followers)
DEFAULT_FOLLOWER_GIDS="YOUR_DEFAULT_FOLLOWER_GID_1,YOUR_DEFAULT_FOLLOWER_GID_2"

# LLM API Key (if using an external LLM API like Deepseek R1 or Google Gemini)
# DEEPSEEK_API_KEY="your_deepseek_api_key_here"
# GOOGLE_API_KEY="your_google_api_key_here"
```
