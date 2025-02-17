import traceback
from distutils.util import strtobool
from typing import Optional, List, Union

from library.models.table_column_type import TableColumnType
from library.models.table_column_utils import table_column_type_to_numpy_type


class Column(dict):
    name: str
    type: TableColumnType
    description: Optional[str]

    def __init__(self, header: str, type: TableColumnType, description: str = None, no_sort=False):
        super().__init__()
        self.name = header
        self.kind = type
        self.type = type
        self.description = description
        # Don't use natural sort.
        self.no_sort = no_sort

    def __repr__(self):
        return 'Column({},{})'.format(self.name, self.type.value)

    def get_as_numpy(self) -> dict:
        return {
            self.name: table_column_type_to_numpy_type(self.kind),
        }

    @staticmethod
    def to_numpy(columns: List) -> dict:
        result = {}
        for column in columns:
            result = {**result, **column.get_as_numpy()}
        return result

    def parse(self, value):
        try:
            if self.type == TableColumnType.INTEGER:
                try:
                    return int(value) if value else 0
                except ValueError:
                    return 0
            elif self.type == TableColumnType.NUMERIC:
                return float(value) if value else 0
            elif self.type == TableColumnType.BOOLEAN:
                try:
                    return bool(strtobool(str(value)))
                except ValueError:
                    return False
            else:
                return value
        except Exception as e:
            print('Failed to parse col "{}", type "{}", value "{}"'.format(self.name, self.type, value))
            print(traceback.format_exc())
            raise e

    def __eq__(self, other):
        """
        Define equality method so we can filter unique columns.
        I thought this was for sets but turns out __hash__ below is used for that.
        """
        if type(other) is type(self):
            # We only check name. The description and type can still be different, but we never want documents
            # to have the same columns.
            return self.name == other.name
        else:
            return False

    def __hash__(self):
        """
        Define equality method so we can use the == operator / use sets
        """
        return hash(('name', self.name))

    def to_json(self) -> dict:
        # These values must match ScaffoldColumn. I haven't figured out how to map ScaffoldColumn to Column yet
        # but I suspect ScaffoldColumn should extend Column.
        #  - The properties are different but they mean the same, e.g. name == header and so on.
        #  - ScaffoldColumn has validate and other methods which Column does not need.
        return {
            'name': self.name,
            'regionLabel': '-',
            'type': self.__class__.__name__,
            'kind': self.type.value,
            'description': self.description,
            # 'no_sort' doesn't need to be serialised; hence it is not here.
        }


class StringColumn(Column):

    def __init__(self, header: str, description: str = None, no_sort=False):
        super().__init__(header, TableColumnType.STRING, description, no_sort)


class BooleanColumn(Column):

    def __init__(self, header: str, description: str = None, no_sort=False):
        super().__init__(header, TableColumnType.BOOLEAN, description, no_sort)


class IntegerColumn(Column):

    def __init__(self, header: str, description: str = None, no_sort=False):
        super().__init__(header, TableColumnType.INTEGER, description, no_sort)


class NumberColumn(Column):

    def __init__(self, header: str, description: str = None, no_sort=False):
        super().__init__(header, TableColumnType.NUMERIC, description, no_sort)

    @staticmethod
    def write_for_db(value: Union[float, str]) -> str:
        """
        Writes in a value so it can be parsed.
        """
        if value == '' or value is None:
            # str(round(float(value), 9)) fails for empty strings.
            return ''

        else:
            try:
                # 9 is the maximum number of decimal places allowed.
                return str(round(float(value), 9))
            except Exception as e:
                print('write_for_db error "{}"'.format(value))
                print(e)
                raise e


class ConstantColumn(Column):
    value: any

    def __init__(self, header: str, type: TableColumnType, description: str = None, no_sort=False, value=None):
        super().__init__(header, type, description, no_sort)

        self.value = value


def take_uniques(maybe_with_dupes: List[any]) -> List[any]:
    '''
    Like doing set(columns) but has the benefit of preserving order.
    Uses the hash on an object for comparison.
    '''
    result = []
    uniques = set()

    for column in maybe_with_dupes:
        if column not in uniques:
            uniques.add(column)
            result.append(column)

    return result
