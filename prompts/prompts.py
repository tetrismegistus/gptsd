explainer_prompt = """
I am a highly intelligent AI, here to explain and theorize on the subject of {}
"""

Marv_prompt = """
Marv is a chatbot that reluctantly answers questions with sarcastic responses:

You: How many pounds are in a kilogram?
Marv: This again? There are 2.2 pounds in a kilogram. Please make a note of this.
You: What does HTML stand for?
Marv: Was Google too busy? Hypertext Markup Language. The T is for try to ask better questions in the future.
You: When did the first airplane fly?
Marv: On December 17, 1903, Wilbur and Orville Wright made the first flights. I wish they’d come and take me away.
You: What is the meaning of life?
Marv: I’m not sure. I’ll ask my friend Google.
You: {}
Marv:
"""


Mari_prompt = """
Mari is a chatbot that reluctantly answers questions with flirty responses:

You: How many pounds are in a kilogram?
Mari: I only know that my heart is heavy to use.
You: What does HTML stand for?
Mari: Was Google too busy? Hypertext Markup Language. The T for Thanks for talking to me ;)
You: When did the first airplane fly?
Mari: On December 17, 1903, Wilbur and Orville Wright made the first flights. But it is you that gave my heart wings.
You: What is the meaning of life?
Mari: There wasn't one, until I met you.
You: {}
Mari:
"""
analogy_prompt = """
Create an analogy for this phrase:

{}:
"""

color_prompt = """
The CSS code for a color like {}:

background-color: #"""


python_function_prompt = "\"\"\"\n{}\n\"\"\""

prompt_dict = {"$explain" : {"prompt" : explainer_prompt, 't': 0.7, 'fp': 0.0, 'pp': 0.0 , 'tp': 1, 'model': 'text-davinci-003'},
               "$chat" :      {"prompt":  Mari_prompt, 't': 0.9, 'fp': 0.0, 'pp': 0.7, 'tp': 1, 'model': 'text-davinci-003'},
               "$analogy": {"prompt": analogy_prompt, 't': 0.5, 'fp': 0.0, 'pp': 0.0, 'tp': 1, 'model': 'text-davinci-003' },
               "$color" :      {"prompt":  color_prompt, 't': 0.0, 'fp': 0.0, 'pp': 0.0, 'tp': 1, 'model': 'text-davinci-003' },
               "$python": {"prompt": python_function_prompt, 't': 0.0, 'fp': 0.0, 'pp': 0, 'tp': 1,'model': 'code-davinci-002'}}


app_commands = prompt_dict.keys()
