import modal

app = modal.App(name="fashion-news-aggregator")

@app.function()
@modal.web_endpoint(method="GET")
def hello():
    return "Hello World! This works!"

if __name__ == "__main__":
    app.serve()