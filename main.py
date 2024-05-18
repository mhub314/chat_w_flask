# import openai
# import os
# from dotenv import load_dotenv

# load_dotenv()
# openai.api_key = os.getenv("CHATGPT_KEY")

# def chat_with_gpt(prompt):
#     response = openai.ChatCompletion.create(
#         model = "gpt-3.5-turbo",
#         messages=[{"role":"user", "content":prompt}]
#     )

#     return response.choices[0].message.content.strip()

# if __name__ == "__main__":
#     while True:
        
#         user_input = input("You: ")
#         if user_input.lower() in ["quit", "exit", "bye"]:
#             break

#         response = chat_with_gpt(user_input)
#         print("MovieBuddy: ", response)