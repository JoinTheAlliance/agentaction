import os
import shutil

from agentaction import (
    add_to_action_history,
    get_action_history,
    get_last_action,
    get_available_actions,
    get_action_from_memory,
    search_actions,
    use_action,
    add_action,
    get_action,
    remove_action,
    import_actions,
    clear_actions,
    get_actions,
)
from agentmemory import wipe_all_memories

from agentaction.main import get_formatted_actions


def setup_test_action():
    return {
        "function": {
            "name": "test",
            "description": "A test action",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "Some test input",
                    },
                },
            },
            "required": ["input"],
        },
        "suggestion_after_actions": [],
        "never_after_actions": [],
        "handler": lambda args: { "success": True, "output": args["input"] },
    }


def cleanup():
    wipe_all_memories()


def test_add_to_action_history():
    cleanup()  # Ensure clean state before test
    add_to_action_history("test 0", {"input": "test 0"})
    history = get_action_history(n_results=1)
    print("history")
    print(history)
    assert len(history) == 1 and history[0]["document"] == "test 0"

    # add 30 history items
    for i in range(30):
        add_to_action_history("test " + str(i), {"input": "test " + str(i)})
    history = get_action_history(n_results=20)
    assert len(history) == 20  # Should only return 20 results
    assert history[0]["document"] == "test 29"  # Should be the last item
    assert history[-1]["document"] == "test 10"  # Should be the first item
    cleanup()  # Cleanup after the test


def test_get_last_action():
    cleanup()  # Ensure clean state before test
    assert get_last_action() is None  # Should be None when no history
    add_to_action_history("test first", {"input": "test first"})
    add_to_action_history("test last", {"input": "test last"})
    assert get_last_action() == "test last"
    cleanup()  # Cleanup after the test


def test_add_and_use_action():
    cleanup()  # Ensure clean state before test
    test_action = setup_test_action()
    add_action("test", test_action)
    assert get_action("test") is not None  # Action should now exist
    result = use_action("test", {"input": "test"})
    print('result is')
    print(result)
    assert result["success"] and result["output"] == "test"
    cleanup()  # Cleanup after the test


def test_remove_action():
    cleanup()  # Ensure clean state before test
    test_action = setup_test_action()
    add_action("test", test_action)
    remove_action("test")
    assert get_action("test") is None  # Action should not exist after removal
    cleanup()  # Cleanup after the test


def test_search_actions():
    cleanup()  # Ensure clean state before test
    test_action = setup_test_action()
    add_action("test", test_action)
    search_results = search_actions("test")
    assert len(search_results) > 0  # At least one action should be found
    cleanup()  # Cleanup after the test


def test_get_available_actions():
    cleanup()  # Ensure clean state before test
    test_action = setup_test_action()
    add_action("test", test_action)
    add_to_action_history(
        "test", {"input": "test"}
    )  # Add an action to history so there is a "last action"
    available_actions = get_available_actions("test")
    assert len(available_actions) > 0  # Should be at least one action
    cleanup()  # Cleanup after the test


def get_get_action_from_memory():
    cleanup()  # Ensure clean state before test
    test_action = setup_test_action()
    add_action("test", test_action)

    memory = get_action_from_memory("test")
    assert memory is not None
    cleanup()  # Cleanup after the test


# Define a directory for testing import_actions
TEST_DIR = "test_actions_dir"


def setup_test_action_file(filename, action_names):
    """
    Create a Python file with a get_actions function that returns a list of
    dummy actions.

    Args:
        filename: Name of the file to create.
        action_names: List of action names to include in the created file.
    """
    with open(filename, "w") as f:
        f.write("def get_actions():\n")
        f.write("    return [\n")
        for name in action_names:
            f.write(
                f"""        {{
            "function": {{
                "name": "{name}",
                "description": "A test action",
                "parameters": {{
                    "type": "object",
                    "properties": {{
                        "input": {{
                            "type": "string",
                            "description": "Some test input",
                        }},
                    }},
                }},
                "required": ["input"],
            }},
            "suggestion_after_actions": [],
            "never_after_actions": [],
            "handler": lambda args: args["input"],
        }},\n"""
            )
        f.write("    ]\n")


def setup_test_directory():
    """
    Setup a test directory with Python files containing dummy actions.
    """
    # if the test directory already exists, remove it
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.mkdir(TEST_DIR)
    # create a file at os.path.join(TEST_DIR, "__init__.py")
    open(os.path.join(TEST_DIR, "__init__.py"), "w").close()
    setup_test_action_file(
        os.path.join(TEST_DIR, "actions1.py"), ["action1", "action2"]
    )
    setup_test_action_file(
        os.path.join(TEST_DIR, "actions2.py"), ["action3", "action4"]
    )


def teardown_test_directory():
    """
    Remove the test directory and all its contents.
    """
    shutil.rmtree(TEST_DIR)


def test_import_actions():
    cleanup()  # Ensure clean state before test
    setup_test_directory()  # Create a test directory with action files

    import_actions(TEST_DIR)  # Add actions from test directory
    actions = get_actions()

    # Check that all actions from the test files have been added
    assert "action1" in actions
    assert "action2" in actions
    assert "action3" in actions
    assert "action4" in actions

    teardown_test_directory()  # Cleanup the test directory
    cleanup()  # Cleanup after the test


def test_clear_actions():
    cleanup()  # Ensure clean state before test

    # Add some actions
    test_action = setup_test_action()
    add_action("test1", test_action)
    add_action("test2", test_action)

    # Verify actions were added
    assert "test1" in get_actions()
    assert "test2" in get_actions()

    clear_actions()  # Clear all actions

    # Verify that no actions exist after clearing
    assert get_actions() == {}

    cleanup()  # Cleanup after the test


def test_get_actions():
    cleanup()  # Ensure clean state before test

    # Add some actions
    test_action = setup_test_action()
    add_action("test1", test_action)
    add_action("test2", test_action)

    actions = get_actions()

    # Verify that the actions have been added
    assert "test1" in actions
    assert "test2" in actions

    cleanup()  # Cleanup after the test


def test_get_formatted_actions_normal():
    cleanup()  # Ensure clean state before test

    # Add some actions
    test_action = setup_test_action()
    add_action("test1", test_action)
    add_action("test2", test_action)
    add_action("test3", test_action)

    result = get_formatted_actions("test")

    # Verify that the actions have been included in the available actions
    action_names = [
        action["metadata"]["name"] for action in result["available_actions"]
    ]
    assert "test1" in action_names
    assert "test2" in action_names
    assert "test3" in action_names

    # Verify that the formatted actions includes the action names
    assert "test1" in result["formatted_actions"]
    assert "test2" in result["formatted_actions"]
    assert "test3" in result["formatted_actions"]

    # Verify that the short actions includes the action names
    assert "test1" in result["short_actions"]
    assert "test2" in result["short_actions"]
    assert "test3" in result["short_actions"]

    cleanup()  # Cleanup after the test


def test_get_formatted_actions_no_actions():
    cleanup()  # Ensure clean state before test

    result = get_formatted_actions("test")

    # There should be no available actions
    assert len(result["available_actions"]) == 0

    # The formatted actions should only include the header text
    assert (
        result["formatted_actions"].strip()
        == "Available actions for me to choose from:"
    )

    # The short actions should also indicate no actions available
    assert result["short_actions"].strip() == "Available actions (name):"

    cleanup()  # Cleanup after the test
