import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.index_documents import main

if __name__ == "__main__":
    main()