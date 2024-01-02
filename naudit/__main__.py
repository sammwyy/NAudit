import colorama
import naudit
import sys

if __name__ == '__main__':
    # Initialize colorama
    colorama.init(autoreset=True)

    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3:
        print("Python 3 or greater is required.")
        sys.exit(1)

    # Run the main function
    naudit.main()
