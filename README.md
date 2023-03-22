# A chatbot using OpenAI's ChatGPT API

## Usage
+ Dependencies
```
pip install requests func_timeout
```

+ Set `OPENAI_API_KEY` environment variable with your own private key.

+ Run example
```
python3 ./chatbot.py ./chat_example.json
```

+ Commands
```
/exit: exit session.
/save: save current conversations.
/undo: undo previous message.
/clear: clear current conversations and chat history.
/prompt: print current full prompt.
/comp: compress current conversations into chat history.
```