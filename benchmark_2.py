"""Benchmark Appwrite."""
import os
import time
import random
from dataclasses import dataclass
from multiprocessing.pool import ThreadPool
import urllib3
import faker
from appwrite.client import Client
from appwrite.services.databases import Databases
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
fake = faker.Faker()

appwrite_client = Client()
(appwrite_client
  .set_endpoint("https://localhost/v1")
  .set_project(os.environ["APPWRITE_PROJECT"])
  .set_key(os.environ["APPWRITE_KEY"])
  .set_self_signed()
)
appwrite_db = Databases(appwrite_client, "benchmark")
N_THREADS = 100
pool = ThreadPool(N_THREADS)

@dataclass
class User:
    """Mockup data structure."""
    name: str
    country: str
    age: int
    hair_color: str
    company: str
    bio: str
    address: str

def generate_mockup_data(size: int) -> list[User]:
    """Generate a list of users."""
    users = []
    colors = ["blue", "black", "red", "green", "white", "bald"]
    for _ in range(size):
        users.append(User(
            name=fake.name(),
            country=fake.country(),
            age=random.randint(3, 90),
            hair_color=random.choice(colors),
            company=fake.company(),
            bio=fake.text(),
            address=fake.address(),
        ))
    return users

def setup_appwrite_db():
    """Create the database in Appwrite."""
    appwrite_db.create("benchmark")
    appwrite_db.create_collection(
        collection_id="benchmark",
        name="benchmark",
        permission='["read(any)", "write(any)", "update(any)", "delete(any)"]',
        read=[],
        write=[],
    )
    appwrite_db.create_string_attribute(
        collection_id="benchmark",
        key="name",
        size=100,
        required=True,
        array=False,
    )
    appwrite_db.create_string_attribute(
        collection_id="benchmark",
        key="country",
        size=100,
        required=True,
        array=False,
    )
    appwrite_db.create_integer_attribute(
        collection_id="benchmark",
        key="age",
        required=True,
        array=False,
    )
    appwrite_db.create_string_attribute(
        collection_id="benchmark",
        key="hair_color",
        size=100,
        required=True,
        array=False,
    )
    appwrite_db.create_string_attribute(
        collection_id="benchmark",
        key="company",
        size=100,
        required=True,
        array=False,
    )
    appwrite_db.create_string_attribute(
        collection_id="benchmark",
        key="bio",
        size=10000,
        required=True,
        array=False,
    )
    appwrite_db.create_string_attribute(
        collection_id="benchmark",
        key="address",
        size=1000,
        required=True,
        array=False,
    )

def cleanup_appwrite_db():
    """Remove appwrite collection."""
    appwrite_db.delete_collection(collection_id="benchmark")
    appwrite_db.delete()

ids = []

def populate_appwrite():
    """Generate data and send it to appwrite."""
    global ids
    data = generate_mockup_data(1_000)
    for user in data:
        doc = appwrite_db.create_document(
            collection_id="benchmark",
            document_id="unique()",
            data={
                "name": user.name,
                "country": user.country,
                "age": user.age,
                "hair_color": user.hair_color,
                "company": user.company,
                "bio": user.bio,
                "address": user.address,
            }
        )
        ids.append(doc["$id"])

def benchmark_appwrite_read(ids: list[str]):
    """Test reading in appwrite."""
    for document_id in ids:
        appwrite_db.get_document(
            collection_id="benchmark",
            document_id=document_id,
        )

def main():
    """Entrypoint."""
    cleanup_appwrite_db()
    setup_appwrite_db()
    for _ in range(N_THREADS):
        pool.apply_async(populate_appwrite)
    pool.close()
    pool.join()

    time_before = time.time()
    benchmark_appwrite_read(ids[:1000])
    time_after = time.time()
    print(f"Average read: {(time_after - time_before) / 1000:.4f}s")

if __name__ == "__main__":
    main()
