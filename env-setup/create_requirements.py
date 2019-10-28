try:
    from pip._internal.operations import freeze
except ImportError:  # pip < 10.0
    from pip.operations import freeze

requirements = freeze.freeze()
with open("requirements.txt", "w") as file:
    for requirement in requirements:
        file.write(requirement + "\n")
