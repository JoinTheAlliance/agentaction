import os
import importlib
import json
import sys

from agentmemory import (
    create_memory,
    delete_memory,
    get_memories,
    search_memory,
    wipe_category,
)

# Create an empty dictionary to hold the actions
actions = {}


def compose_action_prompt(action, values):
    """
    Composes a prompt based on the given action and observation.

    Args:
        action: Dict representing an action.
            This action contains a 'prompt' and 'builder' key
            The prompt is a string template
            The builder is a function which injects data into the template
        values: A dictionary of values to insert into the prompt

    Returns:
        A string representing the composed prompt.
    """
    prompt = action["prompt"]
    builder = action["builder"]
    if builder is not None:
        prompt = builder(values)
    return prompt


def get_actions():
    """
    Retrieve all the actions present in the global `actions` dictionary.

    Returns:
        A dictionary of all actions.
    """
    global actions
    return actions


def add_to_action_history(action_name, action_arguments={}, success=True):
    """
    Add an executed action to the action history.

    Args:
        action_name: The name of the action that was executed.
        action_arguments: A dictionary of arguments used to execute the action.
        success: A boolean indicating whether the action was successful or not.
    """
    # if success is a boolean, convet to a string
    if isinstance(success, bool):
        success = str(success)
    action_arguments["success"] = success
    create_memory("action_history", action_name, action_arguments)


def get_action_history(n_results=20):
    """
    Retrieve the most recent executed actions.

    Args:
        n_results: Number of results to retrieve

    Returns:
        A list of actions.
    """
    memories = get_memories(
        category="action_history",
        n_results=n_results,
    )
    return memories


def get_last_action():
    """
    Retrieve the last executed action from the action history.

    Returns:
        The name of the last executed action or None if no action was found.
    """
    history = get_action_history(n_results=1)
    if len(history) == 0:
        return None
    last = history[0]["document"]
    return last


def get_available_actions(search_text, n_results=5):
    available_actions = search_actions(search_text=search_text, n_results=n_results)
    recommended_actions = []
    ignored_actions = []

    last_action = get_last_action()
    if last_action is not None:
        recommended_actions = actions[last_action]["suggestion_after_actions"]
        # get actions from named list
        recommended_action_objects = []
        for action in recommended_actions:
            recommended_action_objects.append(get_action_from_memory(action))
        ignored_actions = actions[last_action]["never_after_actions"]
        ignored_action_objects = []
        for action in ignored_actions:
            ignored_action_objects.append(get_action_from_memory(action))
        # check if available_actions contains recommended actions, if not, add them
        for action in recommended_action_objects:
            if action not in available_actions:
                action["recommended"] = True
                available_actions.append(action)
        # for each action in ignored, delete from available
        for action in ignored_action_objects:
            if action in available_actions:
                available_actions.remove(action)

    return available_actions


def get_action_from_memory(action_name):
    """
    Retrieve an action from memory based on the action's name.

    Args:
        action_name: The name of the action to retrieve.

    Returns:
        A dictionary representing the action.
    """
    action = get_memories("actions", filter_metadata={"name": action_name}, n_results=1)
    if len(action) == 0:
        return None
    return action[0]


def search_actions(search_text, n_results=5):
    """
    Searches for actions based on a query text.

    Args:
        search_text: Query text used to search for actions.
        n_results: Maximum number of results to return.

    Returns:
        A list of dictionaries representing the found actions.
    """
    search_results = search_memory(
        "actions", search_text=search_text, n_results=n_results
    )

    return search_results


def use_action(function_name, arguments):
    """
    Execute a specific action by its function name.

    Arguments:
    function_name (str): The name of the action's function to execute.
    arguments (dict): The arguments required by the action's function.

    Returns:
    dict: Contains the "success" key
            True if the action was found and executed, otherwise False.
            If the action was found and executed, also contains "result" key
    """
    if function_name not in actions:
        add_to_action_history(function_name, arguments, success=False)
        return {"success": False, "response": "Action not found"}

    add_to_action_history(function_name, arguments)
    result = actions[function_name]["handler"](arguments)

    return {"success": True, "result": result}


def add_action(name, action):
    """
    Add an action to the actions dictionary and 'actions' collection in memory.

    Arguments:
    name (str): The name of the action.
    action (dict): The action data to be added.

    Returns:
    None
    """
    actions[name] = action
    create_memory(
        "actions",
        f"{name} - {action['function']['description']}",
        {"name": name, "function": json.dumps(action["function"])},
        id=name,
    )


def get_action(name):
    """
    Retrieve a specific action by its name from the 'actions' dictionary.

    Arguments:
    name (str): The name of the action to retrieve.

    Returns:
        dict or None: The action if found, otherwise None.
    """
    if name in actions:
        return actions[name]
    return None


def remove_action(name):
    """
    Remove a specific action by name

    Arguments:
    name (str): The name of the action to remove.

    Returns:
    None
    """
    if name in actions:
        del actions[name]
        delete_memory("actions", name)
        return True
    return False


def import_actions(actions_dir):
    """
    Import all the actions present in the 'actions_dir' directory
    First, check if get_actions function exists inside python file
    The actions returned are then added to the 'actions' dictionary.

    Returns:
    None
    """

    actions_dir = os.path.abspath(actions_dir)
    sys.path.insert(0, actions_dir)

    for filename in os.listdir(actions_dir):
        if filename.endswith(".py"):
            module_name = filename[:-3]  # filename without .py
            module = importlib.import_module(module_name)

            if hasattr(module, "get_actions"):
                action_funcs = module.get_actions()

                for i in range(len(action_funcs)):
                    name = action_funcs[i]["function"]["name"]
                    add_action(name, action_funcs[i])
    # Remove the added path after done with imports
    sys.path.remove(actions_dir)


def clear_actions():
    """
    Wipe the 'actions' collection in memory and reset the 'actions' dictionary.

    Returns:
    None
    """
    wipe_category("actions")
    global actions
    actions = {}


def get_formatted_actions(search_text):
    """
    Retrieve a dict containing the available actions in several formats

    Args:
        search_text: Find most revelant actions whith are available.

    Returns:
        {
        "available_actions": a list of available actions in memory format
        "formatted_actions": a list of actions as a string
        "short_actions": a list of actions names as a string, comma separated
    }
    """
    header_text = "Available actions for me to choose from:"
    available_actions = get_available_actions(search_text, n_results=5)

    # sort available_actions so that recommended are first
    # recommended are action["metadata"].get("recommended", None)
    available_actions = sorted(
        available_actions,
        key=lambda x: x.get("recommended", None) is True,
        reverse=True,
    )

    def create_formatted_actions(actions):
        formatted_actions = []
        for action in actions:
            if action.get("recommended", None) is True:
                formatted_actions.append(f"(recommended) {action['document']}")
            else:
                formatted_actions.append(action["document"])
        # join the actions with a newline
        return "\n".join(formatted_actions)

    short_actions = "Available actions (name): " + ", ".join(
        [k["metadata"]["name"] for k in available_actions]
    )

    formatted_actions = (
        header_text + "\n" + create_formatted_actions(available_actions) + "\n"
    )

    return {
        "available_actions": available_actions,
        "formatted_actions": formatted_actions,
        "short_actions": short_actions,
    }
