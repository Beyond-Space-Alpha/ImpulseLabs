import google.generativeai as genai

genai.configure(api_key="")

model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content("Explain black holes in simple terms")

print(response.text)