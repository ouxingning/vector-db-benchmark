import numpy
import array
import oracledb

# Convert from NumPy ndarray types to array types when inserting vectors
def numpy_converter_in(value):
    if value.dtype == numpy.float64:
        dtype = "d"
    elif value.dtype == numpy.float32:
        dtype = "f"
    else:
        dtype = "b"
    return array.array(dtype, value)
    
def input_type_handler(cursor, value, arraysize):
    if isinstance(value, numpy.ndarray):
        return cursor.var(
            oracledb.DB_TYPE_VECTOR,
            arraysize=arraysize,
            inconverter=numpy_converter_in,
        )

# Convert from array types to NumPy ndarray types when fetching vectors
def numpy_converter_out(value):
    if value.typecode == "b":
        dtype = numpy.int8
    elif value.typecode == "f":
        dtype = numpy.float32
    else:
        dtype = numpy.float64
    return numpy.array(value, copy=False, dtype=dtype)
    
def output_type_handler(cursor, metadata):
    if metadata.type_code is oracledb.DB_TYPE_VECTOR:
        return cursor.var(
            metadata.type_code,
            arraysize=cursor.arraysize,
            outconverter=numpy_converter_out,
        )