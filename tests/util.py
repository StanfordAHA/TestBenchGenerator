import delegator

def run(cmd, cwd="."):
    print("+ " + cmd)
    result = delegator.run(cmd, cwd=cwd)
    print(result.out)
    if result.return_code:
        print(result.err)
        raise RuntimeError()
    return result
