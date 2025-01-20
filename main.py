import os
from dotenv import load_dotenv
import openai
import streamlit as st

# Load environment variables
load_dotenv()

# Retrieve the OpenAI API key from the .env file
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("OpenAI API key is missing. Please set it in the .env file.")
    st.stop()

# Set the API key for the OpenAI client
openai.api_key = openai_api_key

# Initialize OpenAI client
client = openai.OpenAI(api_key=openai_api_key)

model = "gpt-4o-mini"  # "gpt-3.5-turbo-16k"

# Hardcoded IDs for testing
thread_id = None
assis_id = "asst_3aVO0JzlWpj2iJoXGGann5Sc"

# Initialize session state
if "file_id_list" not in st.session_state:
    st.session_state.file_id_list = []

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Set up page
st.set_page_config(page_title="Help Desk Agent - Chat and Learn", page_icon=":books:")

# Function to upload a file to OpenAI
def upload_to_openai(filepath):
    with open(filepath, "rb") as file:
        response = client.files.create(file=file.read(), purpose="assistants")
    return response.id

# Sidebar for file uploads
st.sidebar.title("Help Desk Sidebar")
file_uploaded = st.sidebar.file_uploader("Upload a file", type=["pdf"], key="file_upload")

# Upload File Section
if st.sidebar.button("Upload File"):
    if file_uploaded:
        with open(file_uploaded.name, "wb") as f:
            f.write(file_uploaded.getbuffer())
        file_id = upload_to_openai(file_uploaded.name)
        st.session_state.file_id_list.append(file_id)
        st.sidebar.success(f"Uploaded File ID: {file_id}")

# Display Uploaded Files
if st.session_state.file_id_list:
    st.sidebar.write("Uploaded File IDs:")
    for file_id in st.session_state.file_id_list:
        st.sidebar.text(file_id)

# Add some spacing between file IDs and "Start Chatting" button
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)

# Start Chatting Section
if st.session_state.file_id_list:
    if st.sidebar.button("Start Chatting"):
        st.session_state.start_chat = True
        if not st.session_state.thread_id:
            try:
                chat_thread = client.beta.threads.create()
                st.session_state.thread_id = chat_thread.id
                st.sidebar.write("New thread started!")
                st.write("Thread ID:", chat_thread.id)
            except Exception as e:
                st.error(f"Error creating thread: {e}")
else:
    st.sidebar.warning("Please upload at least one file to start chatting.")

# Main Interface
st.title("Help Desk")
st.write("Learn fast by chatting with your documents.")

if st.session_state.start_chat:
    st.write("Chat session started. Type your questions below!")

    # Display existing messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"**User:** {message['content']}")
        elif message["role"] == "assistant":
            st.markdown(f"**Assistant:** {message['content']}")

    # Chat input box
    prompt = st.text_input("Type your question here...")
    if prompt:
        # Append the user message to the session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f"**User:** {prompt}")

        # Send the user message to the assistant
        try:
            # Send the message to the assistant
            user_message = client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=prompt
            )

            # Trigger a response run by the assistant
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assis_id,
                instructions="""Please answer the user's questions using the provided files only."""
            )

            # Poll the run for completion
            while run.status != "completed":
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id, run_id=run.id
                )

            # Retrieve the assistant's response
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            assistant_messages = [
                message for message in messages.data
                if message.role == "assistant" and message.run_id == run.id
            ]

            # Display the assistant's response
            for message in assistant_messages:
                assistant_response = message.content[0].text  # Access content correctly
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                st.markdown(f"**Assistant:** {assistant_response}")

        except Exception as e:
            st.error(f"Error communicating with assistant: {e}")
else:
    st.write("Upload a file and click 'Start Chatting' to begin.")
