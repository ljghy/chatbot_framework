import sys
from chat_session import ChatSession, CommandType
import os
if os.name == "posix":
    import readline

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No input file.")
        exit()

    session = None
    try:
        session = ChatSession(sys.argv[1])
    except FileNotFoundError:
        print("File not found.")
        exit()

    while 1:
        human_input = input(session.human_name + ": ")

        ret = session.process_input(human_input)
        if ret[0]:  # get response
            print("{}: {}\n[token usage: {}({:.0f}%)]".format(
                session.AI_name, ret[1], ret[2],
                100 * ret[2] / session.model_max_tokens))
        else:
            if ret[2] == CommandType.EXIT:
                save = input("Save the session? (y|n) ")
                if save.strip() == "y":
                    session.process_input("/save")
                exit()
            elif ret[2] == CommandType.COMPRESS_SUCCEEDED:
                confirm = input("Chat summary: {}\nConfirm? (y|n) ".format(
                    ret[1]))
                if confirm.strip() == "y":
                    session.compress(ret[1])
            else:
                print(ret[1])
