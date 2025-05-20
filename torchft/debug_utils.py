def write_debug_log(msg: str) -> None:
    """
    Helper function to write a message to debug.log.
    """
    with open("debug.log", "a") as f:
        f.write(msg + "\n")