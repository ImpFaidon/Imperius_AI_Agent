from flask import Flask, request, jsonify
from main import app as asana_agent_app, AgentState # Import the compiled LangGraph app and its state
import logging
import traceback

app = Flask(__name__)

logging.basicConfig(filename='api.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/create_asana_from_brief', methods=['POST'])
def create_asana_from_brief():
    try:
        data = request.get_json()
        if not data or 'brief_content' not in data:
            logging.error("Invalid request: Missing 'brief_content'")
            return jsonify({'error': 'Invalid request: Missing brief_content'}), 400

        raw_brief = data['brief_content']

        try:
            # Invoke the LangGraph app with the raw brief
            initial_state = AgentState(raw_brief=raw_brief) # Initialize state with the raw brief
            final_state = asana_agent_app.invoke(initial_state)

            # Extract the relevant part of the final state for the response
            asana_result = final_state.get("asana_task_result")
            refined_brief = final_state.get("refined_brief")

            if asana_result and asana_result.get("status") == "success":
                return jsonify({
                    'status': 'success',
                    'refined_brief': refined_brief,
                    'asana_task_id': asana_result.get("task_id"),
                    'asana_task_name': asana_result.get("task_name"),
                    'message': 'Asana task created successfully.'
                }), 200
            else:
                error_message = asana_result.get("message", "Unknown error creating Asana task.") if asana_result else "No result from Asana task creation."
                logging.error(f"Error creating Asana task: {error_message}")
                return jsonify({'status': 'error', 'message': error_message, 'refined_brief': refined_brief}), 500

        except Exception as e:
            error_message = f"Error processing brief with Llama/LangGraph: {traceback.format_exc()}"
            logging.error(error_message)
            return jsonify({'error': 'Error processing brief with Llama/LangGraph', 'details': str(e)}), 500

    except Exception as e:
        error_message = f"Unexpected API error: {traceback.format_exc()}"
        logging.error(error_message)
        return jsonify({'error': 'Unexpected API error', 'details': str(e)}), 500

if __name__ == '__main__':
    # Make sure to run your Ollama server with the model you specified (e.g., llama3.2)
    # For production, run with a WSGI server like Gunicorn
    app.run(debug=True, port=5000)