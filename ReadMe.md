# Appwrite database benchmark

I want to use Appwrite for several projects involving large datasets.

This is a test to see how it performs against PostgreSQL and mariadb.

The benchmark covers:
- writing to the DB
- querying data via an index

Tests are performed on an M2 Apple chip.

Both environements are run with Docker.

We use appwrite version `1.3.3`, mariadb `10.11`, and PostgreSQL `15.2`.

## Data

We will write this data structure:

|  name            |  country       |  age  |  hair_color  |  company  |  bio           |  address |
|  ----            |  ----          |  ---  |  ----------  |  -------  |  ---           |  ----    |
|  Tony Parker     |  United States |  20   |  blue        | ABC Corp  | Lorem ipsum... |  23 Ev.  |
|  Michael Jordan  |  France        |  73   |  green       | XYZ Corp  | Lorem ipsum... |  42 Po.  |

Data will be generated using faker.

## Result of benchmark #1

This test writes 1,000 documents, and get 1,000 documents by ids.

|  db       |  average read  |  average write  |
| ---       |  ---           |  ---            |
| appwrite  |  14.05ms       |  15.1ms         |
| mariadb   |  2.1ms         |  1.1ms          |
| pg        |  1.5ms         |  1.3ms          |

The appwrite Python SDK is using the `requests` package, which is very slow.

It might be the reason why it is 10x slower than mariadb.
