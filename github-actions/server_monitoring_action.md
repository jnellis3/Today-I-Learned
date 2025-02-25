# Server Monitoring with Gitea Actions

Today I learned how to create actions that execute on a schedule to monitor server health. If the server appears to be down or broken, a text message is sent using Sinch to a list of numbers.

```yaml
    - name: Check Server
      run: |
        # Check if the URL is reachable
        if curl --silent --head --fail "${{ secrets.URL }}"; then
            echo "✅ Server is up."
        else
            echo "❌ Server is down."
            curl -X POST \
            -H "Authorization: Bearer ${{ secrets.SINCH_API_KEY }}" \
            -H "Content-Type: application/json"  -d '
                {
                    "from": "${{ secrets.SINCH_NUMBER }}",
                    "to": [
                        "123456789"
                    ],
                    "body": "Website Appears Down"
                }' \
            "https://us.sms.api.sinch.com/xms/v1/${{ secrets.SINCH_GROUP }}/batches"
        fi
```