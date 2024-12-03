from flask import Flask, render_template, request
from openai import OpenAI
from dotenv import load_dotenv
import os
import requests

app = Flask (__name__)

load_dotenv()
OPENAI_API_KEY = os.getenv ("OPENAI_API_KEY")

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
BASE_URL = 'https://api.spoonacular.com/recipes/complexSearch'

@app.route("/", methods = ["GET", "POST"])
def index():
    aiopinion = ''
    # Sends request to Spoonacular for recipe
    recipe = None
    recipe_image = None
    recipe_instructions = None
    recipe_link = None
    restrictions = []
    data = []

    if request.method == "POST":
        query = request.form ['recipe_name']
        # Here is where we added the dietary restrictions to the form
        if 'vegetarian' in request.form:
            restrictions.append ('vegetarian')
        if 'vegan' in request.form:
            restrictions.append ('vegan')
        if 'glutenFree' in request.form:
            restrictions.append ('glutenFree')
        if 'dairyFree' in request.form:
            restrictions.append ('dairyFree')
        if 'nutFree' in request.form:
            restrictions.append ('nutFree')
        if 'eggFree' in request.form:
            restrictions.append ('eggFree')
        if 'wheatFree' in request.form:
            restrictions.append ('wheatFree')

        # This creates the parameters for the API request, including the dietary restrictions
        params = {
            'query' : query,
            'apiKey' : SPOONACULAR_API_KEY,
            'diet' : ',' .join (restrictions)
        }
        
        # Requests the Spoonacular API to search for the recipes 
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # Gets the first recipe from the results 
            if data ['results']:
                recipe_data = data ['results'] [0]
                recipe = recipe_data ['title']
                recipe_image = recipe_data ['image']
                recipe_id = recipe_data ['id']
            # Gets more detailed information about the recipe
                detail_response = requests.get (
                    f' https://api.spoonacular.com/recipes/{recipe_id}/information',
                    params= {'apiKey': SPOONACULAR_API_KEY}
                )
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    recipe_instructions = detail_data.get('instructions', 'Instructions not available')
                    recipe_link = detail_data.get ('sourceURL', '')
                else :
                    recipe_instructions = 'Error fetching detailed recipe information.'
            else:
                recipe = 'No recipes found'
        else :
            recipe = 'Error fething recipe'

        # Sends a question OPENAI
        aiopinion = ''
        if data ['results']:
            system_prompt = "You are a very helpful assistant for learning recipes"
            user_prompt = "Give me an opinion about "+recipe
            client = OpenAI (api_key=OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model = "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            aiopinion = completion.choices[0].message.content

    return render_template('index.html', recipe=recipe , recipe_image=recipe_image, recipe_instructions=recipe_instructions,recipe_link=recipe_link,aiopinion=aiopinion)

if __name__ == "__main__":
    app.run(debug=True)