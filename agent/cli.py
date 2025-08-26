from __future__ import annotations
import argparse, os
from dotenv import load_dotenv
from agent.core import handle_user_input

def main():
    load_dotenv()
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True, help="User prompt to send to the agent.")
    args = ap.parse_args()
    print(handle_user_input(args.prompt))

if __name__ == "__main__":
    main()
