# A chatbot using OpenAI's GPT-3 model

A wrapper of OpenAI's GPT-3 API.

## Usage
+ Dependencies
```
pip install openai func_timeout
```

+ Set `OPENAI_API_KEY` environment variable with your own private key.

+ Run example
```
python3 ./gtp3_chat.py ./chat_example.json
```

+ Commands
```
!exit: exit and save the conversations.
!undo: undo your previous sentence.
```