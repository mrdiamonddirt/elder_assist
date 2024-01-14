import streamlit as st
import base64
import pyaudio
import wave
from clarifai.client.auth import create_stub
from clarifai.client.auth.helper import ClarifaiAuthHelper
from clarifai.client.user import User
from clarifai.modules.css import ClarifaiStreamlitCSS
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from google.protobuf import json_format, timestamp_pb2
import io


st.set_page_config(layout="wide")
ClarifaiStreamlitCSS.insert_default_css(st)

# APP Variables
USER_ID = 'r0wd0g'
# Your PAT (Personal Access Token) can be found in the portal under Authentification
PAT = '7621bc9789dd4fe18f4ceb1d29dc4f54'
APP_ID = 'my-first-application-4uq69s'
# Change these to make your own predictions
WORKFLOW_ID = 'assistant_flow'
AUDIO_URL = 'https://samples.clarifai.com/negative_sentence_1.wav'

# Create a gRPC stub
channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)

metadata = (('authorization', f'Key {PAT}'),)

userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID) # The userDataObject is required when using a PAT

post_workflow_results_response = stub.PostWorkflowResults(
    service_pb2.PostWorkflowResultsRequest(
        workflow_id=WORKFLOW_ID,
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(
                    audio=resources_pb2.Audio(
                        url=AUDIO_URL
                    )
                )
            )
        ]
    ),
    metadata=metadata
)

if post_workflow_results_response.status.code != status_code_pb2.SUCCESS:
    print(post_workflow_results_response.status)
    raise Exception("Post workflow results failed, status: " + post_workflow_results_response.status.description)

# We'll get one WorkflowResult for each input we used above. Because of one input, we have here one WorkflowResult
results = post_workflow_results_response.results[0]

# Each model we have in the workflow will produce its output
for output in results.outputs:    
    model = output.model    
    print("Output for the model: `%s`" % model.id)   
    for concept in output.data.concepts:        
        print("\t%s %.2f" % (concept.name, concept.value)) 
    print(output.data.text.raw)

    if output.data.audio:
        # convert the base64 string to a buffer
        buffer = io.BytesIO(base64.b64decode(output.data.audio.base64))
        
        # create a temporary WAV file
        with wave.open('output.wav', 'wb') as wave_file:
            wave_file.setnchannels(1)
            wave_file.setsampwidth(2)
            wave_file.setframerate(24000)
            wave_file.writeframes(buffer.getvalue())

        # play the audio using PyAudio
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wave_file.getsampwidth()),
                        channels=wave_file.getnchannels(),
                        rate=wave_file.getframerate(),
                        output=True)
        stream.write(buffer.getvalue())
        stream.close()
        p.terminate()


# Uncomment this line to print the full Response JSON
#print(results) 
