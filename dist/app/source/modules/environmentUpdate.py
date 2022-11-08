from .environmentSetup import *


def updateEnv(updateDict):
    basedir = os.environ["basedir"]
    for key in updateDict:
        keyEnvFile = "_".join(key.upper().split(" "))
        set_key(os.path.join(basedir, "source", ".env"), keyEnvFile, updateDict[key])
