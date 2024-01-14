import streamlit as st
from clarifai.client.auth import create_stub
from clarifai.client.auth.helper import ClarifaiAuthHelper
from clarifai.client.user import User
from clarifai.modules.css import ClarifaiStreamlitCSS
from google.protobuf import json_format, timestamp_pb2
import datetime

st.set_page_config(layout="wide")
ClarifaiStreamlitCSS.insert_default_css(st)

# This must be within the display() function.
auth = ClarifaiAuthHelper.from_streamlit(st)
stub = create_stub(auth)
userDataObject = auth.get_user_app_id_proto()

workflowid = assistant_flow


st.title("What Can i Help You With Today?")

app = stub.GetApp(service_pb2.GetAppRequest(user_app_id=userDataObject))

# send audio to workflow

workflow = stub.GetWorkflow(service_pb2.GetWorkflowRequest(workflow_id=workflowid))

workflow_input = workflow.workflow.input_template
workflow_input.input_type = "wav"
workflow_input.input_config.audio_config.language_code = "en-US"
workflow_input.input_config.audio_config.sample_rate_hertz = 44100

# add audio file
audio_file = st.file_uploader("Upload a file", type=["wav"])

# send audio to workflow
send_audio = stub.PostWorkflowResults(
    service_pb2.PostWorkflowResultsRequest(
        workflow_id=workflowid,
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(
                    audio=resources_pb2.Audio(
                        content=audio_file.read(),
                        audio_config=workflow_input.input_config.audio_config,
                    )
                )
            )
        ],
    )
)

# get response from assistant
# display response
response = send_audio.results[0].outputs[0].data.concepts[0].name

st.write(response)
