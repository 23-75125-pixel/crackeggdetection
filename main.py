#!/usr/bin/env python3
"""
EggGuard Pro
Application entry point
"""

import sys

def main():
    print("\nEggGuard Pro starting on http://localhost:5000\n")

    try:
        from app import app
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=False,      # set True only during development
            threaded=True
        )

    except ImportError:
        print("Error: Could not import Flask app.")
        print("Make sure dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()