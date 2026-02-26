# assert_container_creation_succeeds() Documentation

## Overview

The `assert_container_creation_succeeds()` method has been added to the `ContainerTestLib` class. This function asserts that container creation succeeds and optionally tests the connection to the created container.

## Source

Converted from bash function in:
- **File**: `/Users/phracek/work/scl-containers/postgresql-container/test/run_test`
- **Lines**: 247-283

## Location

- **Module**: `container_ci_suite/container_lib.py`
- **Class**: `ContainerTestLib`
- **Method**: `assert_container_creation_succeeds()`

## Function Signature

```python
def assert_container_creation_succeeds(
    self,
    container_args: List[str] | str,
    command: str = "",
    test_connection_func=None,
    connection_params: dict = None
) -> bool
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `container_args` | `List[str]` or `str` | Yes | - | Container arguments (e.g., environment variables, ports) |
| `command` | `str` | No | `""` | Command to run in the container |
| `test_connection_func` | `callable` | No | `None` | Optional function to test connection after creation |
| `connection_params` | `dict` | No | `None` | Parameters to pass to the connection test function |

## Returns

- `bool`: `True` if container creation succeeded, `False` otherwise

## Basic Usage

### Simple Container Creation Test

```python
from container_ci_suite.container_lib import ContainerTestLib

# Initialize
ct = ContainerTestLib(image_name="postgres:13")

# Test that container creation succeeds
assert ct.assert_container_creation_succeeds(
    container_args="-e POSTGRESQL_USER=user -e POSTGRESQL_PASSWORD=pass -e POSTGRESQL_DATABASE=db"
)
```

### With List Arguments

```python
# Using list of arguments
assert ct.assert_container_creation_succeeds(
    container_args=[
        "-e", "POSTGRESQL_USER=user",
        "-e", "POSTGRESQL_PASSWORD=pass",
        "-e", "POSTGRESQL_DATABASE=db"
    ]
)
```

### With Custom Command

```python
# Test with custom command
assert ct.assert_container_creation_succeeds(
    container_args="-e POSTGRESQL_USER=user -e POSTGRESQL_PASSWORD=pass",
    command="postgres -c 'max_connections=200'"
)
```

## Advanced Usage with Connection Testing

### PostgreSQL Example

```python
from container_ci_suite.container_lib import ContainerTestLib
from container_ci_suite.engines.database import DatabaseWrapper

# Initialize
ct = ContainerTestLib(image_name="postgres:13")
db = DatabaseWrapper(image_name="postgres:13", db_type="postgresql")

# Define connection test function
def test_postgres_connection(cid_file, params):
    """Test PostgreSQL connection."""
    ct = params['ct']
    db = params['db']

    # Get container IP
    container_ip = ct.get_cip(cid_file)

    # Test connection
    return db.test_connection(
        container_ip=container_ip,
        username=params['user'],
        password=params['pass'],
        database=params['database']
    )

# Test container creation with connection verification
assert ct.assert_container_creation_succeeds(
    container_args="-e POSTGRESQL_USER=testuser -e POSTGRESQL_PASSWORD=testpass -e POSTGRESQL_DATABASE=testdb",
    test_connection_func=test_postgres_connection,
    connection_params={
        'ct': ct,
        'db': db,
        'user': 'testuser',
        'pass': 'testpass',
        'database': 'testdb'
    }
)
```

### MySQL Example

```python
from container_ci_suite.container_lib import ContainerTestLib
from container_ci_suite.engines.database import DatabaseWrapper

# Initialize
ct = ContainerTestLib(image_name="mysql:8.0")
db = DatabaseWrapper(image_name="mysql:8.0", db_type="mysql")

# Define connection test function
def test_mysql_connection(cid_file, params):
    """Test MySQL connection."""
    ct = params['ct']
    db = params['db']

    # Get container IP
    container_ip = ct.get_cip(cid_file)

    # Test connection
    return db.test_connection(
        container_ip=container_ip,
        username=params['user'],
        password=params['pass'],
        database=params['database']
    )

# Test container creation with connection verification
assert ct.assert_container_creation_succeeds(
    container_args="-e MYSQL_USER=testuser -e MYSQL_PASSWORD=testpass -e MYSQL_DATABASE=testdb -e MYSQL_ROOT_PASSWORD=rootpass",
    test_connection_func=test_mysql_connection,
    connection_params={
        'ct': ct,
        'db': db,
        'user': 'testuser',
        'pass': 'testpass',
        'database': 'testdb'
    }
)
```

## PyTest Usage

### Basic Test

```python
import pytest
from container_ci_suite.container_lib import ContainerTestLib

class TestContainerCreation:
    def setup_method(self):
        self.ct = ContainerTestLib(image_name="postgres:13")

    def teardown_method(self):
        self.ct.cleanup()

    def test_container_creation_succeeds(self):
        """Test that container creation succeeds with valid arguments."""
        assert self.ct.assert_container_creation_succeeds(
            container_args="-e POSTGRESQL_USER=user -e POSTGRESQL_PASSWORD=pass -e POSTGRESQL_DATABASE=db"
        )
```

### Parametrized Test

```python
@pytest.mark.parametrize("user,password,database", [
    ("user1", "pass1", "db1"),
    ("user2", "pass2", "db2"),
    ("admin", "adminpass", "admindb"),
])
def test_container_creation_various_configs(self, user, password, database):
    """Test container creation with various configurations."""
    assert self.ct.assert_container_creation_succeeds(
        container_args=f"-e POSTGRESQL_USER={user} -e POSTGRESQL_PASSWORD={password} -e POSTGRESQL_DATABASE={database}"
    )
```

### Test with Connection Verification

```python
from container_ci_suite.engines.database import DatabaseWrapper

class TestContainerWithConnection:
    def setup_method(self):
        self.ct = ContainerTestLib(image_name="postgres:13")
        self.db = DatabaseWrapper(image_name="postgres:13", db_type="postgresql")

    def teardown_method(self):
        self.ct.cleanup()

    def test_container_creation_and_connection(self):
        """Test container creation and verify connection works."""
        def test_conn(cid_file, params):
            container_ip = params['ct'].get_cip(cid_file)
            return params['db'].test_connection(
                container_ip, params['user'], params['pass']
            )

        assert self.ct.assert_container_creation_succeeds(
            container_args="-e POSTGRESQL_USER=user -e POSTGRESQL_PASSWORD=pass -e POSTGRESQL_DATABASE=db",
            test_connection_func=test_conn,
            connection_params={
                'ct': self.ct,
                'db': self.db,
                'user': 'user',
                'pass': 'pass'
            }
        )
```

## Original Bash Implementation

```bash
# From postgresql-container/test/run_test (lines 247-283)
assert_container_creation_succeeds ()
{
  local check_env=false
  local name=pg-success-"$(ct_random_string)"
  local PGUSER='' PGPASS=''  DB=''  ADMIN_PASS=
  local docker_args=
  local ret=0

  for arg; do
    docker_args+=" $(printf "%q" "$arg")"
    if $check_env; then
      local env=${arg//=*/}
      local val=${arg//$env=/}
      case $env in
        POSTGRESQL_ADMIN_PASSWORD)  ADMIN_PASS=$val ;;
        POSTGRESQL_USER)            PGUSER=$val ;;
        POSTGRESQL_PASSWORD)        PGPASS=$val ;;
        POSTGRESQL_DATABASE)        DB=$val ;;
      esac
      check_env=false
    elif test "$arg" = -e; then
      check_env=:
    fi
  done

  DOCKER_ARGS=$docker_args create_container "$name" || ret=1

  if test -n "$PGUSER" && test -n "$PGPASS"; then
    PGUSER=$PGUSER PASS=$PGPASS DB=$DB test_connection "$name" || ret=2
  fi

  if test -n "$ADMIN_PASS"; then
    PGUSER=postgres PASS=$ADMIN_PASS DB=$DB test_connection "$name" || ret=3
  fi

  return $ret
}
```

## Migration from Bash

### Before (Bash)

```bash
# In postgresql-container/test/run_test
assert_container_creation_succeeds \
  -e POSTGRESQL_USER=user \
  -e POSTGRESQL_PASSWORD=pass \
  -e POSTGRESQL_DATABASE=db
```

### After (Python)

```python
from container_ci_suite.container_lib import ContainerTestLib

ct = ContainerTestLib(image_name="postgres:13")
assert ct.assert_container_creation_succeeds(
    container_args="-e POSTGRESQL_USER=user -e POSTGRESQL_PASSWORD=pass -e POSTGRESQL_DATABASE=db"
)
```

## How It Works

1. **Generates unique container name** using random string
2. **Converts arguments** from list to string if needed
3. **Creates the container** using provided arguments
4. **Waits briefly** for container to start (2 seconds)
5. **Checks if container is running**
   - If not running, logs exit status and container logs
6. **Optionally tests connection** if test function provided
7. **Returns success/failure** based on all checks

## Error Handling

The function handles various error scenarios:

- **Empty arguments**: Returns `False` immediately
- **Container creation fails**: Returns `False` and logs error
- **Container not running**: Returns `False`, logs exit status and container logs
- **Connection test fails**: Returns `False` and logs error
- **Connection test exception**: Returns `False` and logs exception

## Test Coverage

The test suite includes **11 comprehensive test cases**:

1. ✅ Basic container creation
2. ✅ Container creation with list arguments
3. ✅ Empty arguments handling
4. ✅ Container creation failure
5. ✅ Container not running after creation
6. ✅ Container creation with connection test (success)
7. ✅ Container creation with connection test (failure)
8. ✅ Container creation with connection test (exception)
9. ✅ Container creation with custom command
10. ✅ Multiple parametrized scenarios
11. ✅ Integration with DatabaseWrapper

## Related Functions

- `assert_container_creation_fails()` - Assert that container creation fails
- `create_container()` - Create a container
- `get_cid()` - Get container ID
- `get_cip()` - Get container IP
- `cleanup()` - Clean up containers

## Running Tests

```bash
cd /Users/phracek/work/scl-utils/container-ci-suite

# Run all tests for this function
pytest tests/test_container_test_lib.py::TestContainerCreationAssertions -v

# Run specific test
pytest tests/test_container_test_lib.py::TestContainerCreationAssertions::test_assert_container_creation_succeeds_basic -v

# Run with coverage
pytest tests/test_container_test_lib.py::TestContainerCreationAssertions --cov=container_ci_suite.container_lib --cov-report=html
```

## Key Improvements Over Bash

| Feature | Bash | Python |
|---------|------|--------|
| Type Safety | ❌ | ✅ Full type hints |
| Flexible Arguments | ⚠️ Positional only | ✅ List or string |
| Connection Testing | ⚠️ Hardcoded | ✅ Pluggable function |
| Error Messages | ⚠️ Basic | ✅ Detailed logging |
| Testing | ⚠️ Limited | ✅ 11 test cases |
| Documentation | ⚠️ Comments | ✅ Comprehensive |
| IDE Support | ❌ | ✅ Autocomplete |
| Reusability | ⚠️ Limited | ✅ High |

## Best Practices

1. **Always use with cleanup**:
   ```python
   ct = ContainerTestLib(image_name="postgres:13")
   try:
       assert ct.assert_container_creation_succeeds(...)
   finally:
       ct.cleanup()
   ```

2. **Use in PyTest with teardown**:
   ```python
   def teardown_method(self):
       self.ct.cleanup()
   ```

3. **Provide connection test for critical tests**:
   ```python
   # Don't just test creation, verify it works!
   assert ct.assert_container_creation_succeeds(
       container_args="...",
       test_connection_func=my_test_func,
       connection_params={...}
   )
   ```

4. **Use descriptive connection test functions**:
   ```python
   def test_database_ready(cid_file, params):
       """Test that database is ready to accept connections."""
       # Implementation
   ```

## Examples by Database Type

### PostgreSQL

```python
ct = ContainerTestLib(image_name="postgres:13")
assert ct.assert_container_creation_succeeds(
    container_args="-e POSTGRESQL_USER=user -e POSTGRESQL_PASSWORD=pass -e POSTGRESQL_DATABASE=db"
)
```

### MySQL

```python
ct = ContainerTestLib(image_name="mysql:8.0")
assert ct.assert_container_creation_succeeds(
    container_args="-e MYSQL_USER=user -e MYSQL_PASSWORD=pass -e MYSQL_DATABASE=db -e MYSQL_ROOT_PASSWORD=root"
)
```

### MariaDB

```python
ct = ContainerTestLib(image_name="mariadb:10.5")
assert ct.assert_container_creation_succeeds(
    container_args="-e MYSQL_USER=user -e MYSQL_PASSWORD=pass -e MYSQL_DATABASE=db -e MYSQL_ROOT_PASSWORD=root"
)
```

### Redis

```python
ct = ContainerTestLib(image_name="redis:6")
assert ct.assert_container_creation_succeeds(
    container_args="-e REDIS_PASSWORD=mypassword"
)
```

## Summary

The `assert_container_creation_succeeds()` function provides a robust, well-tested way to verify that containers are created successfully. It supports flexible argument formats, optional connection testing, and comprehensive error handling, making it ideal for container testing in PyTest-based test suites.

**Key Features**:
- ✅ Flexible argument handling (list or string)
- ✅ Optional connection testing
- ✅ Comprehensive error handling and logging
- ✅ 11 comprehensive test cases
- ✅ Full type hints and documentation
- ✅ PyTest compatible

The function is production-ready and available now in `ContainerTestLib`! 🎉
