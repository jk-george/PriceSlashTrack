"""Unit Tests for the loading process of the pipeline."""
# pylint: skip-file
from unittest.mock import Mock, patch, MagicMock
from load import insert_price_change, load_price_changes, product_id_exists


def test_insert_price_change_valid():
    """Insert query for inserting valid data successfully."""
    mock_conn = MagicMock()

    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    insert_price_change(mock_conn, 1, 22.49, "2024-12-04 16:31:40")

    mock_cursor.execute.assert_called_once()
    assert mock_cursor.execute.call_args[0][1] == (
        22.49, 1, "2024-12-04 16:31:40")


def test_insert_price_change_invalid():
    """Test that exception is raised for invalid querying."""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_cursor.execute.side_effect = Exception("Database error")

    try:
        insert_price_change(mock_conn, 1, 22.49, "2024-12-04 16:31:40")
        assert False, "Expected exception not raised"
    except Exception:
        assert "Database error"


@patch("load.product_id_exists")
def test_product_id_exists_valid(mock_product_id_exists):
    """Test product_id_exists returns True when product_id exists."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    result = product_id_exists(mock_conn, 1)
    assert result == True
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM product WHERE product_id = %s", (1,))


@patch("load.product_id_exists")
def test_product_id_exists_invalid(mock_product_id_exists):
    """Test product_id_exists returns False when product_id doesn't exist."""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_cursor.fetchone.return_value = None

    result = product_id_exists(mock_conn, 1)
    assert result == False
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM product WHERE product_id = %s", (1,)
    )


@patch("load.product_id_exists")
def test_load_price_changes_valid(mock_product_id_exists):
    """Loading valid data into the price_changes table successfully."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    test_data = [
        {'price': 22.49, 'product_id': 8, 'timestamp': '2024-12-04 16:31:40'},
        {'price': 7.69, 'product_id': 9, 'timestamp': '2024-12-04 16:31:40'}
    ]

    load_price_changes(test_data, mock_conn)

    assert mock_cursor.execute.call_count == len(test_data)
    assert mock_conn.commit.called
    assert not mock_conn.rollback.called


def test_load_price_changes_one_valid_one_invalid():
    """Loading valid data into the price_changes table successfully even if there is one invalid data."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    test_data = [
        {'product_id': 8, 'timestamp': '2024-12-04 16:31:40'},
        {'price': 7.69, 'product_id': 9, 'timestamp': '2024-12-04 16:31:40'}
    ]

    load_price_changes(test_data, mock_conn)

    assert mock_cursor.execute.call_count == 1
    assert mock_conn.commit.called
    assert not mock_conn.rollback.called


@patch("load.product_id_exists")
@patch("load.insert_price_change")
def test_load_price_changes_invalid(mock_insert_price_change, mock_product_id_exists):
    """Loading invalid data result in a rollback rather than commit being called."""
    mock_conn = MagicMock()
    mock_product_id_exists.return_value = False
    mock_insert_price_change.return_value = Exception("Database error")

    test_data = [{'product_id': 8,
                  'timestamp': '2024-12-04 16:31:40'}]

    load_price_changes(test_data, mock_conn)

    mock_conn.rollback.assert_called_once()
    mock_conn.commit.assert_not_called()


def test_load_price_changes_empty():
    """Ensure no database operations occur when given an empty list."""
    mock_conn = Mock()
    test_data = []

    load_price_changes(test_data, mock_conn)

    mock_conn.commit.assert_not_called()
    mock_conn.rollback.assert_called_once()


def multiple_insertion_side_effect(test_dict: dict):
    """ specifically for the test below:  """
    if test_dict['product_id'] == 8:
        return None
    else:
        return Exception("Database Error")


@patch("load.product_id_exists")
@patch("load.insert_price_change")
def test_load_price_changes_partial_failure(mock_insert_price_change, mock_product_id_exists):
    """Combination of valid and invalid data insertion """
    mock_conn = MagicMock()
    mock_insert_price_change = Mock(side_effect=multiple_insertion_side_effect)
    mock_product_id_exists.return_value = True

    test_data = [
        {'product_id': 8, 'timestamp': '2024-12-04 16:31:40'},
        {'price': 7.69, 'product_id': 9, 'timestamp': '2024-12-04 16:31:40'}
    ]

    load_price_changes(test_data, mock_conn)
    mock_conn.rollback.assert_not_called()
    mock_conn.commit.assert_called_once()
