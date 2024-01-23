def process_again(acts):
    for i, a in enumerate(acts):
        if a.lower() == "again":
            acts[i] = acts[i - 1]
    return acts
