# Github Markdown API

We are implementing a new feature in Engineering Equation Solver that allows users to ask a chatbot questions. The result returned is markdown, and converting to html has proven to be challenging. Fortunately, Github has a free API for this. The headers of the response will specify rate limits.

**NOTE:** This API can be used unauthenticated (rate limits will be much lower). Otherwise, use a fine grained access token.
 
```javascript
async function render(markdown) {
    return (await fetch('https://api.github.com/markdown', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'mode': 'markdown', 'text': markdown})
    })).text();
}
```

```python
import httpx

body = """
# Example

This is example Markdown
"""

response = httpx.post(
    "https://api.github.com/markdown",
    json={
        # mode=gfm would expand #13 issue links, provided you pass
        # context=simonw/datasette too
        "mode": "markdown",
        "text": body,
    },
    headers=headers,
)
if response.status_code == 200:
    markdown_as_html = response.text
```