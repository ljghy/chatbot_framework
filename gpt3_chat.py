import os
import sys
import json
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")  # set your own API key

background = ""
human_name = ""
AI_name = ""
conversation_list = []

if len(sys.argv) == 1:
    exit()

settings = {}
settings_file_name = sys.argv[1]
with open(settings_file_name, "rb") as file:
    settings = json.load(file)
    background = settings["background"]
    human_name = settings["human_name"]
    AI_name = settings["AI_name"]
    if "memory" in settings:
        conversation_list = settings["memory"]

blank_converation = "\n{human_name}: {{}}\n{AI_name}: ".format(
    human_name=human_name, AI_name=AI_name)

while 1:
    human_input = input(human_name + ": ")
    if human_input == "!exit":
        settings["memory"] = conversation_list
        with open(settings_file_name, "wt", encoding="utf8") as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)
        break
    if human_input == "!undo":
        if len(conversation_list) > 0:
            conversation_list.pop()
        continue

    idx = len(conversation_list)
    conversation_list.append(blank_converation)
    conversation_list[idx] = conversation_list[idx].format(human_input)
    prompt = background + "".join(conversation_list)

    success = True
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=[human_name + ":", AI_name + ":"])
    except openai.error.RateLimitError:
        print("Request too fast")
        success = False

    if success:
        AI_response = response["choices"][0]["text"]
        print(AI_name + ": " + AI_response)
        conversation_list[len(conversation_list) - 1] += AI_response
    else:
        conversation_list.pop()
