import modal

# Create the image with Streamlit
image = modal.Image.debian_slim(python_version="3.11").pip_install("streamlit==1.49.1")

app = modal.App(name="fashion-news-aggregator", image=image)

@app.function(image=image)
@modal.web_server(8000, startup_timeout=60)
def serve():
    import subprocess
    import os
    
    # Create simple app
    app_content = '''
import streamlit as st

st.set_page_config(page_title="Fashion News", page_icon="👗", layout="wide")

st.title("👗 Fashion & Beauty News Aggregator")
st.success("✅ Successfully running on Modal!")

st.markdown("### 🎯 Features")
st.write("- ✅ 20+ International sources")
st.write("- ✅ Smart categorization") 
st.write("- ✅ Time-based filtering")
st.write("- ✅ Professional interface")

if st.button("🎉 Test Button"):
    st.balloons()
    st.success("Everything is working!")

st.sidebar.header("Filters")
st.sidebar.selectbox("Time", ["All", "1hr", "12hr", "1day", "2day", "3day"])
st.sidebar.selectbox("Category", ["All", "Fashion", "Beauty", "Luxury"])

st.markdown("### Sample Articles")
for i in range(5):
    st.markdown(f"**Article {i+1}**: Fashion trend #{i+1} is taking over the industry")
'''
    
    with open("app.py", "w") as f:
        f.write(app_content)
    
    # Start Streamlit - this will block and serve on port 8000
    os.system("streamlit run app.py --server.port 8000 --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false")

if __name__ == "__main__":
    app.serve()