import os
from dotenv import load_dotenv
import openai
import requests
import json

import time
import logging
from datetime import datetime
import streamlit as st


load_dotenv()

client = openai.OpenAI()

model = "gpt-4o-mini"  # "gpt-3.5-turbo-16k"

# Step 1 - Create an assistant
# assistant = client.beta.assistants.create(
#     name="Help Desk Assistant",
#     instructions="""You are a helpful IT support assistant who answers questions based on your knowledge base. Your
#     role is to provide accurate and concise answers to user queries, referencing your knowledge base to ensure
#     reliability. Focus on delivering clear, straightforward responses that directly address the user's concerns.
#     Respond efficiently, incorporating any feedback to improve your accuracy and user satisfaction. Handle all
#     information securely and adhere to company policies and ethical standards. Your ultimate goal is to assist users
#     by providing precise and helpful information, making their IT issues easier to understand and resolve.""",
#     tools=[{"type": "file_search"}],
#     model=model,
# )

# === Get the Assis ID ===
# assis_id = assistant.id
# print(assis_id)

# == Hardcoded ids to be used once the first code run is done and the assistant was created
thread_id = "thread_YY58aQAbZOd0VWOwn3lVWjnr"
assis_id = "asst_3aVO0JzlWpj2iJoXGGann5Sc"

# == Step 2. Upload files and add them to a Vector Store

# # Create a vector store caled "Documentation"
# vector_store = client.beta.vector_stores.create(name="Documentation")
#
# # Ready the files for upload to OpenAI
# file_paths = ["./TestPDF.pdf"]
# file_streams = [open(path, "rb") for path in file_paths]
#
# # Use the upload and poll SDK helper to upload the files, add them to the vector store,
# # and poll the status of the file batch for completion.
# file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
#     vector_store_id=vector_store.id, files=file_streams
# )
#
# # You can print the status and the file counts of the batch to see the result of this operation.
# print(file_batch.status)
# print(file_batch.file_counts)
#
# assistant = client.beta.assistants.update(
#     assistant_id=assis_id,
#     tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
# )

# == Step 3. Create a Thread

message = "How do I create an admin?"

# thread = client.beta.threads.create()
# thread_id = thread.id
# print(thread_id)

message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=message,
)

# == Run the Assistant
run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assis_id,
    instructions="Please be friendly to the user",
)


def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
    """
    Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
    :param thread_id: The ID of the thread.
    :param run_id: The ID of the run.
    :param sleep_interval: Time in seconds to wait between checks.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                print(f"Assistant Response: {response}")
                break
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)


# == Run it
wait_for_run_completion(client=client, thread_id=thread_id, run_id=run.id)

# === Check the Run Steps - LOGS ===
run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id)
print(f"Run Steps --> {run_steps.data[0]}")




