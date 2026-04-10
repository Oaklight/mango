import ast


def edit_distance(s1: str, s2: str):
    s1 = s1.lower()
    s2 = s2.lower()

    m = len(s1) + 1
    n = len(s2) + 1

    dp = [[0] * n for _ in range(m)]

    for i in range(m):
        dp[i][0] = i

    for j in range(n):
        dp[0][j] = j

    for i in range(1, m):
        for j in range(1, n):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + 1)

    # Compute the normalized score
    max_len = max(len(s1), len(s2))
    score = 1 - dp[m - 1][n - 1] / max_len if max_len != 0 else 0
    return score


def parse_raw_output(raw_output: str | list, key_mapping=None):
    """
    raw_output is in the format of ... [{'location_before:','action:','location_after'}...]..., need to extract the path
    key_mapping may vary with llms
    use regex to extract the path
    find the first '[' and the first ']'
    extract the string between the two brackets
    check if the list is in the correct format

    """
    location_before_key = "location_before"
    action_key = "action"
    location_after_key = "location_after"
    if key_mapping is not None:
        location_before_key = key_mapping["location_before"]
        action_key = key_mapping["action"]
        location_after_key = key_mapping["location_after"]

    if isinstance(raw_output, str):
        raw_output = raw_output.strip()

        first_bracket_open_index = raw_output.find("[")
        first_bracket_close_index = raw_output.find("]")
        error_info = None
        try:
            path = ast.literal_eval(
                raw_output[first_bracket_open_index : first_bracket_close_index + 1]
            )
        except (ValueError, SyntaxError):
            error_info = f"raw_output is not in correct format: {raw_output}"
            return None, error_info
    elif isinstance(raw_output, list):
        path = raw_output
    else:
        error_info = f"raw_output should be either str or list: {raw_output} ({type(raw_output)})"
        return None, error_info

    if not isinstance(path, list) or len(path) == 0:
        error_info = (
            f"raw_output is not in correct format: {raw_output} ({type(raw_output)})"
        )
        return None, error_info
    for edge in path:
        if (
            location_before_key not in edge.keys()
            or location_after_key not in edge.keys()
            or action_key not in edge.keys()
        ):
            error_info = f"path edge key error: {edge}"
            return None, error_info
        elif (
            not isinstance(edge[location_before_key], str)
            or not isinstance(edge[location_after_key], str)
            or not isinstance(edge[action_key], str)
        ):
            error_info = f"path edge value error: {edge}"
            return None, error_info

    return path, None
