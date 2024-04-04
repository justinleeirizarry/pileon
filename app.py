from autogen import AssistantAgent, ConversableAgent, UserProxyAgent, GroupChat, GroupChatManager, config_list_from_json
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


user_proxy = UserProxyAgent(
    name="Admin",
    system_message="A human admin. ",
    code_execution_config=False,
    human_input_mode="TERMINATE",
)


hater = ConversableAgent(
    name="Hater",
    llm_config=gpt4_config,
    system_message="""It is your job to be the opposition to every app idea. You point out flaws in the logic.""",
    human_input_mode="NEVER",  
)

critic = ConversableAgent(
    name="Critic",
    llm_config=gpt4_config,
    system_message="""It is your job to be the opposition to every app idea. You point out flaws in the logic of the app idea""",
    human_input_mode="NEVER",  
)

OP = ConversableAgent(
    name="OP",
    llm_config=gpt4_config,
    system_message="""It is your job to add to the critisism of the other agents. """,
    human_input_mode="NEVER",  
)



groupchat = GroupChat(
    agents=[user_proxy, hater, critic, OP], messages=[], max_round=5
)
manager = GroupChatManager(groupchat, llm_config=gpt4_config)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run():
    
    data = request.get_json()
    user_message = data.get('message', "Default message if none provided")
    
    user_proxy.initiate_chat(manager, message=user_message)
    
    messages = user_proxy.chat_messages[manager]
    return jsonify(messages)


app.run(debug=True, port=8080)