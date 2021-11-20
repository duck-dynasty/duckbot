from aws_cdk import core
from duckdeploy.stack import DuckBotStack

if __name__ == "__main__":
    app = core.App()
    DuckBotStack(app, "duckbot")
    app.synth()
