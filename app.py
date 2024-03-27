import autogen

config_list = autogen.config_list_from_json(env_or_file="OAI_CONFIG_LIST")

gpt4_config = {
    "cache_seed": 42,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list,
    "timeout": 120,
}
user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message="A human admin. Interact with the planner to discuss an idea for an app. The planner should start",
    code_execution_config=False,
)

planner = autogen.AssistantAgent(
    name="Op",
    system_message="""Provide negative feedback to the user then bring in the hater for more criticism.
""",
    llm_config=gpt4_config,
)

hater = autogen.AssistantAgent(
    name="Hater",
    llm_config=gpt4_config,
    system_message="""It is your job to be the opposition to every app idea. You are detailed and point out flaws in the logic and what it must say about the user.""",
)


critic = autogen.AssistantAgent(
    name="Critic",
    system_message="Critic. Double check the critisism make nothing is missing",
    llm_config=gpt4_config,
)
groupchat = autogen.GroupChat(
    agents=[user_proxy, planner, hater,critic], messages=[], max_round=10
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)

user_proxy.initiate_chat(
    manager,
    message="""
I want an app that reminds me to feed my fish
""",
)