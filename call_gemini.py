"""
@author: Mike Travis
"""

import os
import mimetypes

from google import genai
from google.genai import types

API_KEY = os.getenv("GEMINI_API_KEY")

def count_tokens(user_query,file_paths=[]):
    client = genai.Client(api_key=API_KEY)
    contents = [user_query]
    if not isinstance(file_paths, list):
        file_paths = [file_paths]
    for file_path in file_paths:
        contents.append(client.files.upload(file=file_path))
    response  = client.models.count_tokens(
        model='gemini-2.5-pro',
        contents=contents
    )
    # for f in contents[1:]:
    #     client.files.delete(name=f.name)
    return response

async def call_gemini_api(system_prompt, user_query):
    client = genai.Client(api_key=API_KEY)
    contents = [user_query]
    response = client.models.generate_content(contents=contents,
                                      config=types.GenerateContentConfig(
                                          system_instruction=system_prompt
                                          ),
                                      model='gemini-2.5-pro',
                                      )
    return response.text

async def call_gemini_api_files(system_prompt, user_query, file_paths=[]):
    client = genai.Client(api_key=API_KEY)
    contents = [user_query]
    if not isinstance(file_paths, list):
        file_paths = [file_paths]
    for file_path in file_paths:
        contents.append(client.files.upload(file=file_path))
    response = client.models.generate_content(contents=contents,
                                      config=types.GenerateContentConfig(
                                          system_instruction=system_prompt
                                          ),
                                      model='gemini-2.5-pro',
                                      )
    # for f in contents[1:]:
    #     client.files.delete(name=f.name)
    return response.text