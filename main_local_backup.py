from src.agent.agent import OpenAIFunctionAgent

if __name__ == "__main__":
    agent = OpenAIFunctionAgent()
    print("Chat với agent (gõ 'exit' hoặc 'quit' để thoát)")
    while True:
        try:
            user_input = input("Bạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nĐã thoát.")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Đã thoát.")
            break

        result = agent.run(user_input)
        print(f"Agent: {result}")
