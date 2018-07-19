# Copyright 2009-present MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""BSON (Binary JSON) encoding and decoding.

The mapping from Python types to BSON types is as follows:

=======================================  =============  ===================
Python Type                              BSON Type      Supported Direction
=======================================  =============  ===================
None                                     null           both
bool                                     boolean        both
int [#int]_                              int32 / int64  py -> bson
long                                     int64          py -> bson
`bson.int64.Int64`                       int64          both
float                                    number (real)  both
string                                   string         py -> bson
unicode                                  string         both
list                                     array          both
dict / `SON`                             object         both
datetime.datetime [#dt]_ [#dt2]_         date           both
`bson.regex.Regex`                       regex          both
compiled re [#re]_                       regex          py -> bson
`bson.binary.Binary`                     binary         both
`bson.objectid.ObjectId`                 oid            both
`bson.dbref.DBRef`                       dbref          both
None                                     undefined      bson -> py
unicode                                  code           bson -> py
`bson.code.Code`                         code           py -> bson
unicode                                  symbol         bson -> py
bytes (Python 3) [#bytes]_               binary         both
=======================================  =============  ===================

Note that, when using Python 2.x, to save binary data it must be wrapped as
an instance of `bson.binary.Binary`. Otherwise it will be saved as a BSON
string and retrieved as unicode. Users of Python 3.x can use the Python bytes
type.

.. [#int] A Python int will be saved as a BSON int32 or BSON int64 depending
   on its size. A BSON int32 will always decode to a Python int. A BSON
   int64 will always decode to a :class:`~bson.int64.Int64`.
.. [#dt] datetime.datetime instances will be rounded to the nearest
   millisecond when saved
.. [#dt2] all datetime.datetime instances are treated as *naive*. clients
   should always use UTC.
.. [#re] :class:`~bson.regex.Regex` instances and regular expression
   objects from ``re.compile()`` are both saved as BSON regular expressions.
   BSON regular expressions are decoded as :class:`~bson.regex.Regex`
   instances.
.. [#bytes] The bytes type from Python 3.x is encoded as BSON binary with
   subtype 0. In Python 3.x it will be decoded back to bytes. In Python 2.x
   it will be decoded to an instance of :class:`~bson.binary.Binary` with
   subtype 0.
"""

from .objectid import ObjectId
