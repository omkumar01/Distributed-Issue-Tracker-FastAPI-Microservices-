"""
Database seeding script.
Populates the database with sample data for development/testing.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def main():
    """Run database seeding."""
    print("Seeding database with sample data...")
    # Add your seeding logic here
    print("Sample data created successfully!")


if __name__ == "__main__":
    asyncio.run(main())
