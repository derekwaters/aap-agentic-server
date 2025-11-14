# AAP Agentic Server Specification

## Summary

The AAP Agentic Server will implement a microservice to allow for API calls to initiate and check the status of Agentic AI workflows.

## Requirements

1) The AAP Agentic Server should be implemented in Python
2) The AI Agent implementation will use the llama-stack ReActAgent module
3) The REST API will implement the endpoint defined in the API Definition below
4) The execution of the AI Agent should be asynchronous

## API Definition

### Send Chat
Endpoint:   /api/send_chat
Method:     POST
Inputs:     text - a String containing the text to pass to the AI Agent create_turn call
Outputs:    session_id - a String containing the agent session id

This endpoint will allow a client to post a chat message that will be submitted to the AI Agent asynchronously. The agent's session id should be returned for use in other API calls.

### Get Chat
Endpoint:   /api/get_chat
Method:     POST
Inputs:     session_id - a String containing the agent session id
Outputs:    response - a String containing the latest accrued updated output from the AI Agent create_turn call
            chat_complete - a Boolean indicating whether the AI Agent turn has finished and processing is complete

This endpoint should retrieve any ongoing output from the AI Agent turn and return it to the client. Note that this may be called asynchronously so the agent may still be processing and sending output. If the agent turn has completed, this endpoint should return the completion status.

## Test Cases

The following test cases should be implemented:

1) Use send_chat to send the following chat message: 'What model are you?'. Use get_chat calls to retrieve the output, and verify that a response eventually receives the chat_complete value as true.

2) Repeat the first test, but make a request to get_chat after chat_complete is true. Verify that no error results.

3) Use send_chat to send the following chat message: 'What model are you?'. Before calling get_chat, use send_chat to send another request with the following chat message: 'What is the capital of China?'. Call get_chat with the first session_id and verify that results are received.

