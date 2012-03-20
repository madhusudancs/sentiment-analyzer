#!/usr/bin/env python
#
# Copyright 2012 Ajay Narayan, Madhusudan C.S., Shobhit N.S.
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import numpy
import scipy


from sklearn.feature_extraction.text import TfidfVectorizer


SENTIMENT_MAP = {
    'positive': 1,
    'negative': -1,
    'neutral': 0,
    'irrelevant': 0,
    }

REVERSE_SENTIMENT_MAP = {
    1: 'positive',
    -1: 'negative',
    0: 'neutral',
    }


class Vectorizer(TfidfVectorizer):
    """The feature extractor is extended to work Disco MapReduce framework.

    We are inheriting the feature extractor provided by scikit.learn library
    to make it work using the MapReduce approach.
    """

    def build_feature_matrix(self, job):
        """Builds the feature vectors matrix from the mapreducer output.

        Args:
            job: The disco MapReduce job.
        """
        from disco.core import result_iterator

        self.docs_to_row_num_map = {}
        self.row_num_to_docs_map = {}

        row_count = 0

        data = []
        rows = []
        cols = []
        for token_column, doc_count_dict in result_iterator(
          job.wait(show=True)):
            for doc_id, count in doc_count_dict.items():
                if doc_id not in self.docs_to_row_num_map:
                    self.docs_to_row_num_map[doc_id] = row_count
                    self.row_num_to_docs_map[row_count] = doc_id
                    row_count += 1

                data.append(count)
                rows.append(self.docs_to_row_num_map[doc_id])
                cols.append(token_column)

        shape = (len(self.docs_to_row_num_map),
                 max(self.vocabulary_.itervalues()) + 1)

        feature_vector = scipy.sparse.coo_matrix(
            (data, (rows, cols)), shape=shape)

        return (self._tfidf.transform(feature_vector, copy=False),
                self.row_num_to_docs_map)

