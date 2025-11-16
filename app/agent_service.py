"""Agent service for managing AI agent interactions."""
import asyncio
import time
from typing import Optional
from termcolor import cprint
from app.session_manager import SessionManager

# Try to import ReActAgent, but handle gracefully if not available
try:
    from llama_stack_client.lib.agents.react.agent import ReActAgent
    from llama_stack_client import LlamaStackClient
    from llama_stack_client import NotFoundError
    from llama_stack_client.lib.agents.event_logger import EventLogger
    from llama_stack_client import APIConnectionError
    from llama_stack_client import APITimeoutError
    REACT_AGENT_AVAILABLE = True
except ImportError:
    ReActAgent = None
    REACT_AGENT_AVAILABLE = False


class AgentService:
    """Service for managing AI agent interactions."""
    
    def __init__(self, session_manager: SessionManager, base_url: str, aap_mcp_url: str, model_id: str):
        self.session_manager = session_manager
        self.agent: Optional[object] = None
        self._initialize_agent(base_url, aap_mcp_url, model_id)
    
    def _initialize_agent(self, base_url: str, aap_mcp_url: str, model_id: str):
        """Initialize the ReActAgent."""
        if not REACT_AGENT_AVAILABLE:
            print("Warning: llama-stack not available, using mock implementation")
            self.agent = None
            return
        
        try:

            client = LlamaStackClient(
                base_url=base_url,
                timeout=10.0 * 60.0
            )

            cprint(f"Inference Parameters:\n\tModel: {model_id}", "green")
            cprint(f"Using AAP MCP URL {aap_mcp_url}", "green")


            try:
                client.toolgroups.unregister(toolgroup_id="mcp::ansible-aap-server")
            except NotFoundError:
                print("Tool doesn't exist yet...")

            registered_tools = client.tools.list()
            registered_toolgroups = [t.toolgroup_id for t in registered_tools]
            if "mcp::ansible-aap-server" not in registered_toolgroups:
                print("Registering the ansible-aap-server toolgroup")
                client.toolgroups.register(
                    toolgroup_id="mcp::ansible-aap-server",
                    provider_id="model-context-protocol",
                    mcp_endpoint={"uri":aap_mcp_url},
                )
                registered_tools = client.tools.list()
                registered_toolgroups = [t.toolgroup_id for t in registered_tools]

            print(f"Your Llama Stack server is registered with the following tool groups @ {set(registered_toolgroups)} \n")

            toolset = []
            for tool in registered_tools:
                if (tool.toolgroup_id in ["mcp::ansible-aap-server", "builtin::websearch"]):
                    toolset.append(tool)
                    
            self.agent = ReActAgent(
                client=client,
                model=model_id,
                tools=["mcp::ansible-aap-server"],#, "builtin::websearch"],
                #tools=toolset
                json_response_format=True,
                sampling_params={"max_tokens":1024},
            )

        except APITimeoutError as e:
            print(f"Warning: Could not initialize ReActAgent due to API Timeout Error: {e}")
            self.agent = None
        except APIConnectionError as e:
            print(f"Warning: Could not initialize ReActAgentdue to API Connection Error: {e}")
            self.agent = None
        except Exception as e:
            print(f"Warning: Could not initialize ReActAgent: {e}")
            self.agent = None
    
    async def create_turn_async(self, session_id: str, text: str):
        """
        Create an agent turn asynchronously.
        
        Args:
            session_id: The session ID for this turn
            text: The text input for the agent
        """
        # Run the agent turn in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._execute_turn, session_id, text)
    
    def _execute_turn(self, session_id: str, text: str):
        """
        Execute the agent turn synchronously.
        
        This method runs in a thread pool to allow async execution.
        """
        accumulated_response = ""
        
        try:
            if self.agent is None:
                # Mock implementation for testing
                # Simulate a realistic response based on the input
                if "model" in text.lower() and "are you" in text.lower():
                    accumulated_response = "I am a language model assistant powered by AI. How can I help you?"
                elif "capital" in text.lower() and "china" in text.lower():
                    accumulated_response = "The capital of China is Beijing."
                else:
                    accumulated_response = f"I understand you're asking: {text}. I am an AI assistant ready to help."
                
                # Simulate some processing time and incremental updates

                words = accumulated_response.split()
                partial_response = ""
                for i, word in enumerate(words):
                    partial_response += word + " "
                    self.session_manager.update_session(session_id, partial_response.strip(), "", False)
                    time.sleep(0.1)  # Simulate processing delay
                
                # Final update with complete response
                self.session_manager.update_session(session_id, accumulated_response, accumulated_response, True)
                return
            
            # Create turn with the agent
            # The ReActAgent should support streaming or incremental updates
            # For now, we'll assume it has a create_turn method that can be called
            # and we can get incremental updates
            
            # If the agent supports streaming, we would collect chunks here
            # For now, we'll simulate the behavior
            if hasattr(self.agent, 'create_turn'):
                llama_session_id = self.agent.create_session(session_id)

                cprint("AGENT: Created new session", "yellow")

                response = self.agent.create_turn(
                    messages=[
                        {
                            "role": "user",
                            "content": text,
                        }
                    ],
                    session_id=llama_session_id,
                    stream=True
                )

                # Try to get streaming output if available
                current_role_block = ""

                for log in EventLogger().log(response):
                    # cprint(f"AGENT: Got update {log}", "yellow")
                    accumulated_response += f"{log}"

                    if log.role is not None:
                        current_role_block = log.content
                    else:
                        current_role_block += log.content

                    self.session_manager.update_session(session_id, accumulated_response, "", False)
                
                cprint(f"AGENT: Final answer: {current_role_block}", "yellow")
                
                self.session_manager.update_session(session_id, accumulated_response, current_role_block, True)


                ### HMMM, this section only seems to work for the first block of work, not subsequent ones...

                # for chunk in response:
                #     if hasattr(chunk, "event") and hasattr(chunk.event, "payload") and hasattr(chunk.event.payload, "delta"):
                #         accumulated_response += f"{chunk.event.payload.delta.text}"
                #         self.session_manager.update_session(session_id, accumulated_response, "", False)

                #     final_chunk = chunk

                # cprint(f"AGENT: Final answer: {final_chunk.event.payload.turn.output_message.content}", "yellow")
                
                # self.session_manager.update_session(session_id, accumulated_response, f"{final_chunk.event.payload.turn.output_message.content}", True)
                
                
                
                cprint("AGENT: Session Complete", "yellow")

            else:
                # Fallback: simulate agent response
                accumulated_response = f"Response to: {text}"
                self.session_manager.update_session(session_id, accumulated_response, "", True)
                
        except Exception as e:
            error_message = f"Error during agent execution: {str(e)}"
            accumulated_response = error_message
            self.session_manager.update_session(session_id, accumulated_response, "", True)
