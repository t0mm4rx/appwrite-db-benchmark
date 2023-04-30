"""Benchmark Appwrite DB and PostgreSQL."""
import os
import time
import random
from dataclasses import dataclass
import urllib3
import faker
from dotenv import load_dotenv
import psycopg2
from appwrite.client import Client
from appwrite.services.databases import Databases
import mariadb

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()
fake = faker.Faker()
pg = psycopg2.connect("dbname=postgres user=postgres password=postgres host=localhost")
maria = mariadb.connect(
    user="root",
    password="example",
    host="127.0.0.1",
    database="benchmark",
)

appwrite_client = Client()
(appwrite_client
  .set_endpoint("https://localhost/v1")
  .set_project(os.environ["APPWRITE_PROJECT"])
  .set_key(os.environ["APPWRITE_KEY"])
  .set_self_signed()
)
appwrite_db = Databases(appwrite_client, "benchmark")

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

def benchmark_appwrite_write(data: list[User]) -> list[str]:
    """Test writing to appwrite."""
    ids = []
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
    return ids

def benchmark_appwrite_read(ids: list[str]):
    """Test reading in appwrite."""
    for document_id in ids:
        appwrite_db.get_document(
            collection_id="benchmark",
            document_id=document_id,
        )

def setup_pg_db():
    """Setup PostgreSQL database."""
    cur = pg.cursor()
    cur.execute("""
    CREATE TABLE benchmark (
        id serial PRIMARY KEY,
        name varchar,
        country varchar,
        age int,
        hair_color varchar,
        company varchar,
        bio varchar,
        address varchar
    );
    """)
    pg.commit()
    cur.close()

def cleanup_pg_db():
    """Remove benchmark table."""
    cur = pg.cursor()
    cur.execute("""
    DROP TABLE benchmark;
    """)
    pg.commit()
    cur.close()

def benchmark_pg_write(data: list[User]):
    """Test writing to PostgreSQL."""
    for user in data:
        cur = pg.cursor()
        cur.execute("""
        INSERT INTO benchmark (name, country, age, hair_color, company, bio, address)
        VALUES (%(name)s, %(country)s, %(age)s, %(hair_color)s, %(company)s, %(bio)s, %(address)s)
        """, {
                "name": user.name,
                "country": user.country,
                "age": user.age,
                "hair_color": user.hair_color,
                "company": user.company,
                "bio": user.bio,
                "address": user.address,
            })
        pg.commit()
        cur.close()

def benchmark_pg_read(ids: list[int]):
    """Test reading from PostgreSQL."""
    for row_id in ids:
        cur = pg.cursor()
        cur.execute("""
        SELECT * from benchmark WHERE id = %s;
        """, (row_id,))
        pg.commit()
        cur.close()

def setup_mariadb_db():
    """Setup mariadb."""
    cur = maria.cursor()
    cur.execute("""
        CREATE TABLE benchmark (
        id INT(10) NOT NULL AUTO_INCREMENT,
        name VARCHAR(100),
        country VARCHAR(100),
        age INT(4),
        hair_color VARCHAR(100),
        company VARCHAR(100),
        bio VARCHAR(10000),
        address VARCHAR(1000),
        PRIMARY KEY (id)
        );
    """)
    maria.commit()
    cur.close()

def benchmark_mariadb_write(data: list[User]):
    """Test writing to mariadb."""
    for user in data:
        cur = maria.cursor()
        cur.execute("""
        INSERT INTO benchmark (name, country, age, hair_color, company, bio, address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
                user.name,
                user.country,
                user.age,
                user.hair_color,
                user.company,
                user.bio,
                user.address,
        ))
        maria.commit()
        cur.close()

def benchmark_mariadb_read(ids: list[int]):
    """Test reading from mariadb."""
    for row_id in ids:
        cur = maria.cursor()
        cur.execute("""
        SELECT * from benchmark WHERE id = ?;
        """, (row_id,))
        maria.commit()
        cur.close()

def cleanup_mariadb_db():
    """Remove the benchmark table."""
    cur = maria.cursor()
    cur.execute("""
    DROP TABLE benchmark;
    """)
    maria.commit()
    cur.close()

def main():
    """Entrypoint."""
    setup_pg_db()
    setup_mariadb_db()
    setup_appwrite_db()

    for _ in range(1):
        print("Generating data")
        data = generate_mockup_data(1_000)
        print(f"Generated {len(data)} users")
        print()

        appwrite_write_start = time.time()
        appwrite_ids = benchmark_appwrite_write(data)
        appwrite_write_end = time.time()
        print(f"Appwrite total time: {appwrite_write_end - appwrite_write_start:.2f}s")
        print(f"Average request time: {(appwrite_write_end - appwrite_write_start) / len(data):.4f}s")

        appwrite_read_start = time.time()
        benchmark_appwrite_read(appwrite_ids)
        appwrite_read_end = time.time()
        print(f"Appwrite read total time: {appwrite_read_end - appwrite_read_start:.2f}s")
        print(f"Average request time: {(appwrite_read_end - appwrite_read_start) / len(data):.4f}s")
        print()

        pg_write_start = time.time()
        benchmark_pg_write(data)
        pg_write_end = time.time()
        print(f"pg total time: {pg_write_end - pg_write_start:.2f}s")
        print(f"Average request time: {(pg_write_end - pg_write_start) / len(data):.4f}s")
        pg_read_start = time.time()
        benchmark_pg_read(range(len(data)))
        pg_read_end = time.time()
        print(f"pg total time: {pg_read_end - pg_read_start:.2f}s")
        print(f"Average request time: {(pg_read_end - pg_read_start) / len(data):.4f}s")
        print()

        maria_write_start = time.time()
        benchmark_mariadb_write(data)
        maria_write_end = time.time()
        print(f"mariadb total time: {maria_write_end - maria_write_start:.2f}s")
        print(f"Average request time: {(maria_write_end - maria_write_start) / len(data):.4f}s")
        maria_read_start = time.time()
        benchmark_mariadb_read(range(len(data)))
        maria_read_end = time.time()
        print(f"mariadb read total time: {maria_read_end - maria_read_start:.2f}s")
        print(f"Average request time: {(maria_read_end - maria_write_start) / len(data):.4f}s")
        print()

    cleanup_appwrite_db()
    cleanup_mariadb_db()
    cleanup_pg_db()


if __name__ == "__main__":
    main()
