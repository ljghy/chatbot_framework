import os
import json
import requests
import func_timeout
from enum import Enum


class CommandType(Enum):
    EXIT = 1,
    UNDO = 2,
    CLEAR = 3,
    SAVE = 4,
    PROMPT = 5,
    COMPRESS_SUCCEEDED = 6
    COMPRESS_FAILED = 7


class ChatSession:

    def __init__(self, settings_filename: str):
        self._openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model_max_tokens = 4096
        self.messages = []
        self.compressed_chat = ""
        self.temperature = 1
        self.max_tokens = 0
        self.proxies = {}
        self.instantiated = True

        with open(settings_filename, "rb") as file:
            settings = json.load(file)
            self.settings = settings
            self.background = settings["background"]
            self.human_name = settings["human_name"]
            self.AI_name = settings["AI_name"]

            if "compressed_chat" in settings:
                self.compressed_chat = settings["compressed_chat"]
            if "memory" in settings:
                self.messages += settings["memory"]
            if "temperature" in settings:
                self.temperature = settings["temperature"]
            if "max_tokens" in settings:
                self.max_tokens = settings["max_tokens"]
            if "proxies" in settings:
                self.proxies = settings["proxies"]

        self.settings_filename = settings_filename

    @func_timeout.func_set_timeout(30)
    def _post_request(self, data: dict):
        response = requests.post(
            url="https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self._openai_api_key
            },
            json=data,
            proxies=self.proxies)
        return response

    def _get_response(self) -> tuple:
        data = {
            "model":
            "gpt-3.5-turbo",
            "messages": [{
                "role": "system",
                "content": self.background + self.compressed_chat
            }] + self.messages,
            "temperature":
            self.temperature
        }
        if self.max_tokens > 0:
            data["max_tokens"] = self.max_tokens

        response = None
        try:
            response = self._post_request(data)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout,
                func_timeout.exceptions.FunctionTimedOut) as e:
            return (False, repr(e))
        if response.status_code != 200:
            return (False,
                    RuntimeError("Request failed with code {}".format(
                        response.status_code)))
        else:
            return (True, json.loads(response.text))

    def process_input(self, input_buffer: str) -> tuple:
        input_buffer = input_buffer.strip()
        if input_buffer.startswith("/"):
            return self._process_command(input_buffer[1:])
        else:
            self.messages.append({"role": "user", "content": input_buffer})
            request_response = self._get_response()

            if request_response[0]:
                response = request_response[1]["choices"][0]["message"]
                usage = request_response[1]["usage"]["total_tokens"]
                self.messages.append(response)
                return (True, response["content"], usage)
            else:
                self.messages.pop()
                return (False, request_response[1], 0)

    def compress(self, summary):
        self.compressed_chat = "Chat history: " + summary
        self.messages = []

    def _get_prompt(self) -> str:
        return self.background + "\n" + self.compressed_chat + "\n" + "\n".join(
            [(msg["role"] + ": " + msg["content"]) for msg in self.messages])

    def _process_command(self, command: str):
        command = command.strip()
        cmd_dict = {
            "undo": self._cmd_undo,
            "clear": self._cmd_clear,
            "save": self._cmd_save,
            "exit": lambda: ("Exit.", CommandType.EXIT),
            "prompt": lambda: (self._get_prompt(), CommandType.PROMPT),
            "comp": self._cmd_comp
        }
        if command in cmd_dict:
            ret = cmd_dict[command]()
            return (False, ret[0], ret[1])
        else:
            return (False, "Unknown command \"{}\"".format(command), 0)

    def _cmd_undo(self):
        if len(self.messages) > 0:
            self.messages.pop()
        if len(self.messages) > 0:
            self.messages.pop()
        return ("Previous message undoed.", CommandType.UNDO)

    def _cmd_clear(self):
        self.compressed_chat = []
        self.messages = []
        return ("Chat history cleared.", CommandType.CLEAR)

    def _cmd_save(self):
        self.settings["memory"] = self.messages
        self.settings["compressed_chat"] = self.compressed_chat
        with open(self.settings_filename, "wt", encoding="utf8") as file:
            json.dump(self.settings, file, indent=4, ensure_ascii=False)
        return ("Chat saved to {}.".format(self.settings_filename),
                CommandType.SAVE)

    def _cmd_comp(self):
        self.messages.append({
            "role":
            "user",
            "content":
            "Respond with a brief summary of the chat history and the conversations above without unnecessary words."
        })
        response = self._get_response()
        self.messages.pop()
        if response[0]:
            summary = response[1]["choices"][0]["message"]["content"]
            return (summary, CommandType.COMPRESS_SUCCEEDED)
        else:
            return ("", CommandType.COMPRESS_FAILED)
