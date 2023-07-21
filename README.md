# agentaction <a href="https://discord.gg/qetWd7J9De"><img style="float: right" src="https://dcbadge.vercel.app/api/server/qetWd7J9De" alt=""></a>

Action chaining and history for agents

<img src="resources/image.jpg">

# Why Use This?
This package helps manage and simplify the task of handling actions for an agent, especially a looping agent with chained functions. Actions can be anything, but the intended purpose is to work with openai function calling or other JSON/function calling LLM completion paradigms.

This package facilitates action creation, retrieval, and management, all while supporting vector search powered by chromadb to efficiently locate relevant actions.

# Installation

```bash
pip install agentaction
```

# Quickstart

Create a directory for your action modules:

```bash
mkdir actions
```

In this directory, you can create Python files (`.py`) that define your actions. Each file should define a `get_actions` function that returns a list of action dictionaries. Here is a sample action file `sample_action.py`:

```python
def sample_function(args):
    # Your function logic here
    return "Hello, " + args["name"]

def get_actions():
    return [
        {
            "prompt": "Say hello",
            "builder": None,
            "handler": sample_function,
            "suggestion_after_actions": [],
            "never_after_actions": [],
            "function": {
                "name": "sample_function",
                "description": "Says hello to a person",
                "args": ["name"]
            }
        }
    ]
```

Now you can use the action manager in your agent. Here's a simple example:

```python
from actions_manager import import_actions, use_action

# Import the actions
import_actions("./actions")

# Use an action
result = use_action("sample_function", {"name": "John"})
actions = search_actions("hello")
print(result)  # Should print: {"success": True, "result": "Hello, John"}
```

You can use the `get_available_actions` and `get_action` functions to search for and retrieve actions, respectively. And, don't forget to use the `add_to_action_history` function to keep track of which actions your agent has performed.

## Usage Guide

### Action Creation and Addition
```python
from actions_manager import add_action

action = {
    "prompt": "Action Prompt",
    "builder": None, # the function that is called to build the action prompt
    "handler": your_function_name, # the function that is called when the action is executed
    "suggestion_after_actions": ["other_action_name1", "other_action_name2"],
    "never_after_actions": ["action_name3", "action_name4"],
    "function": {
        "name": "your_function_name",
        "description": "Your function description",
        "args": ["arg1", "arg2"]
    }
}

add_action("your_function_name", action)
```

### Action Execution
```python
from actions_manager import use_action

result = use_action("your_function_name", {"arg1": "value1", "arg2": "value2"})
```

### Search for Relevant Actions
```python
from actions_manager import get_available_actions

actions = get_available_actions("query_text")
```

## API Documentation

### `compose_action_prompt(action: dict, values: dict) -> str`
Generates a prompt for a given action based on provided values.

### `get_actions() -> dict`
Retrieves all the actions present in the global `actions` dictionary.

### `add_to_action_history(action_name: str, action_arguments: dict={}, success: bool=True)`
Adds an executed action to the action history.

### `get_action_history(n_results: int=20) -> list`
Retrieves the most recent executed actions.

### `get_last_action() -> str or None`
Retrieves the last executed action from the action history.

### `get_available_actions(search_text: str) -> list`
Retrieves the available actions based on relevance and last action.

### `get_formatted_actions(search_text: str) -> list`
Retrieve a dict containing the available actions in several formats

### `get_action_from_memory(action_name) -> dict or None`
Retrieve an action from memory based on the action's name.
### `search_actions(search_text: str, n_results: int=5) -> list`
Searches for actions based on a query text.

### `use_action(function_name: str, arguments: dict) -> dict`
Executes a specific action by its function name.

### `add_action(name: str, action: dict)`
Adds an action to the actions dictionary and 'actions' collection in memory.

### `get_action(name: str) -> dict or None`
Retrieves a specific action by its name from the 'actions' dictionary.

### `remove_action(name: str) -> bool`
Removes a specific action by name.

### `import_actions(actions_dir: str)`
Imports all the actions present in the 'actions_dir' directory. The actions returned are then added to the 'actions' dictionary.

### `clear_actions()`
Wipes the 'actions' collection in memory and resets the 'actions' dictionary.


# Contributions Welcome

If you like this library and want to contribute in any way, please feel free to submit a PR and I will review it. Please note that the goal here is simplicity and accesibility, using common language and few dependencies.

<img src="resources/youcreatethefuture.jpg">
