import streamlit as st
import subprocess
import os
from pathlib import Path

st.title("🧪 ARC Tests")

# Environment Variables Configuration
st.subheader("Environment Variables")
with st.expander("Set API Keys and Configuration"):
    google_key = st.text_input(
        "GOOGLE_API_KEY", 
        value=os.environ.get("GOOGLE_API_KEY", ""),
        type="password"
    )
    openai_key = st.text_input(
        "OPENAI_API_KEY", 
        value=os.environ.get("OPENAI_API_KEY", ""),
        type="password"
    )
    anthropic_key = st.text_input(
        "ANTHROPIC_API_KEY", 
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        type="password"
    )
    openrouter_key = st.text_input(
        "OPENROUTER_API_KEY", 
        value=os.environ.get("OPENROUTER_API_KEY", ""),
        type="password"
    )
    
    if st.button("Set Environment Variables"):
        if google_key:
            os.environ["GOOGLE_API_KEY"] = google_key
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        if openrouter_key:
            os.environ["OPENROUTER_API_KEY"] = openrouter_key
        st.success("Environment variables set!")

# Available models and providers
MODELS = {
    "google": ["gemini-flash-1.5", "gemini-2.0-flash-exp"],
    "openai": ["gpt-4-turbo-preview", "gpt-3.5-turbo"],
    "anthropic": [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-5-sonnet-20240620",
        "claude-3-haiku-20240307",
        "claude-3-sonnet-20240229"
    ],
    "openrouter": [
        "google/gemini-flash-1.5",
        "deepseek/deepseek-chat",
        "google/gemini-2.0-flash-exp:free",
        "google/gemini-exp-1206:free",
        "meta-llama/llama-3.3-70b-instruct",
        "qwen/qwq-32b-preview",
        "qwen/qwen-2.5-72b-instruct",
        "anthropic/claude-3.5-sonnet:beta",
        "nvidia/llama-3.1-nemotron-70b-instruct",
        "openai/o1-mini",
        "openai/o1-preview",
        "cohere/command-r7b-12-2024"
    ],
    "langchain": ["gpt-4-turbo-preview", "claude-3-opus-20240229"]
}

# Create two columns for parallel and sequential tests
col1, col2 = st.columns(2)

with col1:
    st.subheader("Parallel Tests")
    parallel_provider = st.selectbox(
        "Select Provider (Parallel)",
        list(MODELS.keys()),
        key="parallel_provider"
    )
    parallel_model = st.selectbox(
        "Select Model (Parallel)",
        MODELS[parallel_provider],
        key="parallel_model"
    )
    
    if st.button("Run Parallel Tests"):
        model_path = f"{parallel_model}"
        with st.spinner(f"Running parallel tests with {model_path}..."):
            try:
                # Initialize session state if not exists
                if 'parallel_process' not in st.session_state:
                    st.session_state.parallel_process = None
                    st.session_state.parallel_output = ""
                    st.session_state.parallel_output_container = st.empty()
                
                # Start the process if not already running
                if st.session_state.parallel_process is None:
                    st.session_state.parallel_process = subprocess.Popen(
                        ["bash", "-c", f"source ~/.installs/arc-test/bin/activate && python3 -u run_parallel.py --model {parallel_model}"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        env=os.environ,
                        bufsize=1,
                        universal_newlines=True
                    )
                
                # Check process status and update output
                if st.session_state.parallel_process.poll() is None:
                    # Process is still running
                    line = st.session_state.parallel_process.stdout.readline()
                    if line:
                        st.session_state.parallel_output += line
                        st.session_state.parallel_output_container.code(st.session_state.parallel_output)
                else:
                    # Process completed
                    if st.session_state.parallel_process.returncode == 0:
                        st.success("Parallel tests completed successfully!")
                    else:
                        st.error("Parallel tests failed")
                    st.session_state.parallel_process = None
                
                # Create separate containers for stdout and stderr
                stdout_container = st.empty()
                stderr_container = st.empty()
                stdout_content = ""
                stderr_content = ""
                
                # Stream both stdout and stderr simultaneously
                while process.poll() is None:
                    # Read stdout
                    stdout_line = process.stdout.readline()
                    if stdout_line:
                        stdout_content += stdout_line
                        stdout_container.code(stdout_content)
                        process.stdout.flush()
                    
                    # Read stderr
                    stderr_line = process.stderr.readline()
                    if stderr_line:
                        stderr_content += stderr_line
                        stderr_container.code(stderr_content)
                        process.stderr.flush()
                
                # Create a container for live output
                output_container = st.empty()
                output = ""
                
                # Stream the output live with explicit flushing
                while process.poll() is None:
                    line = process.stdout.readline()
                    if line:
                        output += line
                        output_container.code(output)
                        process.stdout.flush()
                    
                # Capture any remaining output with explicit flushing
                stdout, stderr = process.communicate()
                output += stdout
                process.stdout.flush()
                process.stderr.flush()
                
                if process.returncode == 0:
                    st.success("Parallel tests completed successfully!")
                    output_container.code(output)
                else:
                    st.error("Parallel tests failed")
                    output_container.code(stderr)
            except Exception as e:
                st.error(f"Error running parallel tests: {str(e)}")

with col2:
    st.subheader("Sequential Tests")
    sequential_provider = st.selectbox(
        "Select Provider (Sequential)",
        list(MODELS.keys()),
        key="sequential_provider"
    )
    sequential_model = st.selectbox(
        "Select Model (Sequential)",
        MODELS[sequential_provider],
        key="sequential_model"
    )
    try:
        process = subprocess.Popen(
            ["/bin/bash", "-c", f"source ~/.installs/arc-test/bin/activate && python3 -u run_sequential.py --provider {sequential_provider} --model {sequential_model}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ,
            bufsize=1,
            universal_newlines=True
        )
        
        # Create a container for live output
        output_container = st.empty()
        output = ""
        
        # Stream the output live
        while process.poll() is None:
            line = process.stdout.readline()
            if line:
                output += line
                output_container.code(output)
            
        # Capture any remaining output
        stdout, stderr = process.communicate()
        output += stdout
        
        if process.returncode == 0:
            st.success("Sequential tests completed successfully!")
            output_container.code(output)
        else:
            st.error("Sequential tests failed")
            output_container.code(stderr)
    except Exception as e:
        st.error(f"Error running sequential tests: {str(e)}")

# Command output display
st.subheader("Command Output")
command_output = st.empty()
