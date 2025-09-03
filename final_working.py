import modal

# Very minimal container
image = modal.Image.debian_slim(python_version="3.11").pip_install("streamlit==1.49.1")

app = modal.App(name="fashion-news-aggregator", image=image)

@app.function(image=image, timeout=300)
@modal.web_server(8000)
def run():
    import subprocess
    import os
    
    # Create the absolute simplest Streamlit app
    app_code = """
import streamlit as st

st.title("👗 Fashion & Beauty News Aggregator")
st.success("✅ Working on Modal!")

st.write("This is a working deployment!")

if st.button("Test"):
    st.balloons()
"""
    
    with open("app.py", "w") as f:
        f.write(app_code)
    
    # Start Streamlit in the background and return immediately
    import subprocess
    subprocess.Popen([
        "streamlit", "run", "app.py", 
        "--server.port", "8000",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])

if __name__ == "__main__":
    app.serve()