# Forthright: Seemingly call Server Functions Client Side

A friend of mine introduced me to a new python package he created called [forthwright](https://github.com/mariusfacktor/forthright/tree/main). This is a Flask wrapper that allows you to wrap functions on the server for execution on the client.

It works by serializing the arguments before sending to the server (therefor you can only pass by value) and then unserializing on the server using pickle.

Example:

```
# backend.py
from forthright import forthright_server
from flask import Flask

app = Flask(__name__)
frs = forthright_server(app)

def add_and_sub(numA, numB):
    return numA + numB, numA - numB

frs.export_functions(add_and_sub)

if __name__ == '__main__':
    app.run(port=8000)
```

```
# client.py
from forthright import forthright_client

url = 'http://127.0.0.1:8000'
frc = forthright_client(url)
frc.import_functions('add_and_sub')

sum, diff = frc.add_and_sub(8, 2)
print('%d %d' %(sum, diff)) # -> 10 6
```

This idea seems to be pretty useful, as I typically don't enjoy working with json in python because of how cumbersome it can be. I think in the future it would be cool to see the ability to pass by reference/work with objects on the server with some form of saved state.