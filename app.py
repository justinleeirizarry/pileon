from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, config_list_from_json
from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socket_io = SocketIO(app)


config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

gpt4_config = {
    "cache_seed": 42,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list,
    "timeout": 120,
}

def new_print_received_message(self, message, sender):

    message_content = message.get('content') if isinstance(message, dict) else message
    print(f"PATCHED {sender.name}: {message_content}")
    socket_io.emit('message', {"sender": sender.name, "content": message_content})

GroupChatManager._print_received_message = new_print_received_message





def is_termination_msg(data):
    has_content = "content" in data and data["content"] is not None
    return has_content and "TERMINATE" in data["content"]


user_proxy = UserProxyAgent(
    name="Admin",
    system_message="A human admin. Interact with the planner to discuss an idea for an app. The planner should start",
    code_execution_config=False,
    is_termination_msg=is_termination_msg, 
    human_input_mode='NEVER',
)

planner = AssistantAgent(
    name="Op",
    system_message="""Provide negative feedback to the user then bring in the hater for more criticism.
""",
    llm_config=gpt4_config,
)

hater = AssistantAgent(
    name="Hater",
    llm_config=gpt4_config,
    system_message="""It is your job to be the opposition to every app idea. You are detailed and point out flaws in the logic and what it must say about the user.""",
)


critic = AssistantAgent(
    name="Critic",
    system_message="Critic. Double check the critisism make nothing is missing",
    llm_config=gpt4_config,
)
groupchat = GroupChat(
    agents=[user_proxy, planner, hater,critic], messages=[], max_round=10
)
manager = GroupChatManager(groupchat, llm_config=gpt4_config)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run():
    # Extract the message from the posted data
    data = request.get_json()
    user_message = data.get('message', "Default message if none provided")
    
    user_proxy.initiate_chat(manager, message=user_message)
    
    messages = user_proxy.chat_messages[manager]
    return jsonify(messages)


app.run(debug=False, port=8080)